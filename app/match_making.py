"""
1.  Call find_implementing_product for each meta device in the scenrio
2.  for each Broker -> Endpoint combination find pahts with: find_communication_partner(endpoint, broker)
3.  Merge the result: for each broker in look if it can reach all endpoints.
    If it do so: create a product set of the current configuration
4.  Apply U_pref on to all product sets for each broker to find the current best solution for the current broker-product-set
5.  Apply U_pref on all product sets for each different broker to find the over all best solution for the current scenrio
"""

from .models import *
import operator


def implement_scenario(scenario):
    """
    Will return an empty set if no matching product implemenatation was found.
    :param scenario:
    :return:
    """
    print('Scenario: %s' % scenario.short_description)
    meta_broker = scenario.meta_broker
    meta_endpoints = set(scenario.meta_endpoints.all())

    # 1. find implementing products
    impl_of_meta_device = dict()
    print('Metabroker: %s' % meta_broker)
    impl_of_meta_device[meta_broker] = find_implementing_product(meta_broker, True)
    print(impl_of_meta_device[meta_broker])
    # no implementation was found
    if len(impl_of_meta_device[meta_broker]) == 0:
        return set()

    # needed for later propose
    used_products = impl_of_meta_device[meta_broker]

    for meta_endpoint in meta_endpoints:
        print('Metaendpoint: %s' % meta_endpoint)
        impl_of_meta_device[meta_endpoint] = find_implementing_product(meta_endpoint, False)
        print('%s : %s' % (meta_endpoint, impl_of_meta_device[meta_endpoint]))
        # no implementation was found
        if len(impl_of_meta_device[meta_endpoint]) == 0:
            return set()
        used_products = used_products.union(impl_of_meta_device[meta_endpoint])

    # 2. start running F
    # we already validated that each endpoint have at least one implementation
    product_sets = set()
    for broker_impl in impl_of_meta_device[meta_broker]:
        possible_paths = dict()
        for meta_endpoint in meta_endpoints:
            for endpoint_impl in impl_of_meta_device[meta_endpoint]:
                # 2.1 call f
                # take an broker impl and an endpoint impl and find the matching ways
                res = find_communication_partner(endpoint_impl, broker_impl)
                if len(res) > 0:
                    # convert inner set to frozenset and list to set
                    res = set(
                            ((frozenset(e))
                                for e in res
                            )
                        )
                    try:
                        possible_paths[meta_endpoint] = possible_paths[meta_endpoint].union(res)
                    except KeyError:
                        possible_paths[meta_endpoint] = res
                    print('%s->%s: %s' % (endpoint_impl, broker_impl, res))

        # check if current broker impl can reach every endpoint
        if len(possible_paths) == 0:
            continue

        possible_sets = __merge_paths(meta_endpoints, possible_paths)
        # 3. apply cost function U_pref to get one product set
        # TODO: change to user preference
        possible_sets = cost_function(possible_sets, "extensible", used_products)
        # 4. merge all product sets
        product_sets.add(possible_sets)

    # 5. apply cost function U_pref to get the best product set
    product_sets = cost_function(product_sets, "extensible", used_products)

    # return the product set
    return product_sets


def cost_function(product_sets, preference, used_products):
    """
    Cost function which decides which product set matches the user preferences.

    :param product_sets:
        set of possible product implementations
    :param preference:
        Preference value of "extensible", "cost", "efficiency"
    :param used_products:
        The broker and endpoint implementations that was used to assemble this product sets.
    :return:
        The product set that will match the user preferences the best.
    """
    if len(product_sets) == 0:
        return set()

    sorting = dict()
    for current_set in product_sets:
        bridges = product_sets.difference(used_products)

        x = 1
        if preference == "extensible":
            x = 0
            for product in current_set:
                x += len(product.leader_protocol.all()) + len(product.follower_protocol.all())
        elif preference == "cost":
            # TODO: implement
            pass
        elif preference == "efficiency":
            # TODO: implement
            pass
        else:
            raise(AttributeError("Unsupported preference %s" % preference))
        sorting[current_set] = 1./x * 0.95**len(bridges)

    return sorted(sorting.items(), key=operator.itemgetter(1))[0][0]


def __merge_paths(meta_endpoints, possible_paths):
    endpoints = list(meta_endpoints.copy())
    if len(endpoints) == 0:
        return set()
    ret = possible_paths[endpoints[0]]
    for elem in endpoints[1:]:
        ret = __product(ret, possible_paths[elem])
    return ret


def __product(a, b):
    ret = set()
    for elem_a in a:
        for elem_b in b:
            ret.add(frozenset(elem_a.union(elem_b)))
    return ret


def find_implementing_product(meta_device, leader):
    """
    Find all implementing products to a given meta_device.

    :param
        meta_device: the meta device that should be implemented
    :param
        leader: if the given meta device is a meta broker
    :return:
        set of all matching products that have at least one protocol matching
        the defined behavior (e.g. borker -> least one leader protocol;
        endpoint -> at least one follower protocol.)
    """
    products = get_products()
    meta_feature = set(meta_device.implementation_requires.all())
    matching_products = set()
    for product in products:
        if meta_feature.issubset(set(product.features.all())):
            if len(__get_protocols(product, leader)) != 0:
                matching_products.add(product)
    return matching_products


def find_communication_partner(endpoint, target, path=None, max_depth=None, bridges_visited=None):
    """
    This function will serve the propose we called small "f". It will find all ways from a given endpoint
    to a given target (most likely the master broker in the scenario/system). For this it will recursively
    traverse through the graph of which products can communicate with which other products.

    :param endpoint:
        the endpoint where the current path should start searching
    :param target:
        the target which is broker or the master broker
    :param path:
        the current path this method traveled, only used in recursive calls
    :param max_depth:
        the maximal depth the algorithms should search; in loops it may be stuck and can't escape.
    :param bridges_visited:
        the reference to product bridges which was already visited, only used in recursive calls
    :return:
        list of sets of all matching product sets that allow the endpoint to communicate with the target
    """
    # init default parameter
    # see "http://effbot.org/zone/default-values.htm" why we have do this in this way
    # we need also create a new reference to the object else python will reuse this objects in recursive calls
    if path is None:
        current_path = set()
    else:
        current_path = path.copy()
    if max_depth is None:
        max_depth = 5
    if bridges_visited is None:
        current_bridges_visited = set()
    else:
        current_bridges_visited = bridges_visited.copy()

    # begin of the algorithm
    if max_depth <= 0:
        raise Exception("max_deph exeeded")

    # define methods for follower/leader protocols
    endpoint_protocols = __get_protocols(endpoint, False)
    bridges = get_bridges().difference({endpoint}).difference(current_bridges_visited).union({target})

    if len(bridges) == 0:
        return list()

    current_path.add(endpoint)
    paths = list()
    for bridge in bridges:
        if __direct_compatible(__get_protocols(bridge, True), endpoint_protocols):
            if bridge == target:
                current_path.add(target)
                paths.append(current_path)
            else:
                # recursive call with the current bridge as a new endpoint
                next_path = find_communication_partner(bridge, target, current_path, max_depth - 1, bridges)
                if len(next_path) != 0:
                    paths.extend(next_path)
    return paths


def __direct_compatible(broker_protocols, endpoint_protocols):
    """
    Checks if the given broker_protocols can communicate with the given endpoint_protocols.

    :param broker_protocols:
        protocols in leader mode
    :param endpoint_protocols:
        protocols in follower mode
    :return:
        if the given broker_protocols can communicate with the given endpoint_protocols
    """
    # TODO: if follower and leader protocol names differ in the future then the if check have to be changed as well
    # check if endpoint can talk directly with broker
    for protocol in endpoint_protocols:
        for broker_protocol in broker_protocols:
            if protocol.name == broker_protocol.name:
                return True
    return False


def __get_protocols(product, leader):
    """
    Returns all the protocols of the given product that matches the given mode.

    :param product:
        the product which speaks a set of protocols
    :param leader:
        if the protocols should be in leader (True) or in follower (False) mode
    :return:
        all spoken protocols by the product in the given mode.
    """
    if leader:
        return set(product.leader_protocol.all())
    else:
        return set(product.follower_protocl.all())


def get_bridges():
    """
    Gets all bridges in the product query set.

    :return:
        set of all bridges in the product query set.
    """
    products = get_products()
    return_set = set()
    for product in products:
        if len(product.leader_protocol.all()) > 0 and len(product.follower_protocol.all()) > 0:
            return_set.add(product)
    return return_set


def get_products():
    """
    Returns all the product as a set.

    :return:
        A set of all known products.
    """
    return set(Product.objects.all())
