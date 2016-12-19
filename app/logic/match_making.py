from ..models import *
import operator
import logging
from django.core.cache import cache
from ..constants import *

# 1h
EXPIRATION_TIME = 60 * 60
BRIDGES_ID_HASH = hash('matching.bridges.cache')
PRODUCT_ID_HASH = hash('matching.product.cache')

LOGGER = logging.getLogger(__name__)


def implement_scenarios(scenarios, preference):
    """
    This method takes a set of scenarios and merge them in that kind that
    meta devices that provide the same feature set are just listed onces.

    :param scenarios:
        set of scenarios that should be implemented.
        Most likely a set of scenarios in the shopping basekt union the new selected scenario
    :param preference:
        the user defined preference
    :return:
        best matching implementing product set
    """
    # merging the endpoints
    meta_endpoints = set()
    meta_brokers = set()
    for scenario in scenarios:
        # merge meta endpoints
        meta_endpoints = __merge_meta_device(set(scenario.meta_endpoints.all()), meta_endpoints)

        # merge meta broker
        meta_brokers = __merge_meta_device({scenario.meta_broker}, meta_brokers)

    # 1. case: meta brokers contain only one element
    if len(meta_brokers) == 1:
        # we are finished here
        # call matching function to compute the reset
        return compute_matching_product_set(meta_brokers.pop(), meta_endpoints, preference)

    # 2. case: meta brokers contain more then one element
    all_possible_solutions = set()

    for meta_broker in list(meta_brokers):
        updated_meta_endpoints = meta_endpoints.copy().union(meta_brokers.copy().difference({meta_broker}))
        res = frozenset(compute_matching_product_set(meta_broker, updated_meta_endpoints, preference))
        if res:
            all_possible_solutions.add(res)

    if len(all_possible_solutions) == 0:
        # 2.1. if all possible solutions have no elements we return the empty set
        return all_possible_solutions
    elif len(all_possible_solutions) == 1:
        # 2.2. if all possible solutions have only one solution we are done.
        return all_possible_solutions.pop()
    else:
        # 2.3 if all possible solutions have more then one element we have to apply the cost function again
        return __cost_function(all_possible_solutions, preference)


def __merge_meta_device(meta_devices, present_set):
    """
    Merges a given set of meta_devices into a present_set of thous.
    This method also checks if the current features of the meta devices can be already satisfied by
    an element in the present set.

    :param meta_devices:
        the meta_devices that should be added in the set of present devices
    :param present_set:
        the set of present devices
    :return:
        the merged set of the meta devices.
    """
    if not present_set:
        present_set.add(meta_devices.pop())
    tmp_add = set()
    tmp_remove = set()

    # check if the given meta endpoint has features that are already satisfied by other meta endpoints
    for cme in meta_devices:
        features_cme = set(cme.implementation_requires.values_list('name', flat=True))
        for me in present_set:
            features_me = set(me.implementation_requires.values_list('name', flat=True))
            if features_me.issubset(features_cme):
                tmp_remove.add(me)
                tmp_add.add(cme)
            elif not features_cme.issubset(features_me):
                tmp_add.add(cme)

    # add the meta_endpoints to the set of meta endpoints
    return present_set.difference(tmp_remove).union(tmp_add)


def compute_matching_product_set(meta_broker, meta_endpoints, preference):
    """
    1.  Call find_implementing_product for each meta device in the scenario
    2.  for each Broker -> Endpoint combination find paths with: find_communication_partner(endpoint, broker)
    3.  Merge the result: for each broker check if it can reach all endpoints.
        If possible: create a product set of the current configuration
    4.  Apply U_pref on all product sets for each broker to find the current best solution for the current broker-product-set
    5.  Apply U_pref on all product sets for each different broker to find the overall best solution for the current scenario
    :param meta_broker:
        the meta broker in the system
    :param meta_endpoints:
        the meta endpoints of the system
    :param preference
        the user preference that was passed by the client
    :return a set of implementing products that matches the user preferences optimally.
    """

    # 1. find implementing products
    impl_of_meta_device = dict()
    LOGGER.debug('Metabroker: %s' % meta_broker)
    impl_of_meta_device[meta_broker] = __find_implementing_product(meta_broker, preference.renovation_preference)

    LOGGER.debug(impl_of_meta_device[meta_broker])
    # no implementation was found
    if len(impl_of_meta_device[meta_broker]) == 0:
        return set()

    for meta_endpoint in meta_endpoints:
        LOGGER.debug('Metaendpoint: %s' % meta_endpoint)
        impl_of_meta_device[meta_endpoint] = __find_implementing_product(meta_endpoint, preference.renovation_preference)
        LOGGER.debug('%s : %s' % (meta_endpoint, impl_of_meta_device[meta_endpoint]))
        # no implementation was found
        if len(impl_of_meta_device[meta_endpoint]) == 0:
            return set()

    if not __product_type_filter_satisfiable(
            impl_of_meta_device.values(), preference.product_type_filter):
        return set()

    # 2. start running F
    # we already validated that each endpoint have at least one implementation
    product_sets = set()
    for broker_impl in impl_of_meta_device[meta_broker]:
        possible_paths = dict()
        for meta_endpoint in meta_endpoints:
            for endpoint_impl in impl_of_meta_device[meta_endpoint]:
                # 2.1 call f
                # take an broker impl and an endpoint impl and find the matching ways
                res = __find_communication_partner(endpoint_impl, broker_impl, preference.renovation_preference)
                if len(res) > 0:
                    # convert inner set to frozenset and list to set
                    res = set(
                        ((frozenset(e))
                         for e in res
                         )
                    )
                    if meta_endpoint in possible_paths:
                        possible_paths[meta_endpoint] = possible_paths[meta_endpoint].union(res)
                    else:
                        possible_paths[meta_endpoint] = res
                    LOGGER.debug('%s->%s: %s' % (endpoint_impl, broker_impl, res))

        # check if current broker impl can reach every endpoint
        if len(meta_endpoints) != len(possible_paths):
            continue

        merged_set = __merge_paths(meta_endpoints, possible_paths)
        # 3. apply cost function U_pref to get one product set
        merged_set = __cost_function(merged_set, preference)

        if merged_set:
            # 4. merge all product sets
            product_sets.add(merged_set)

    # 5. apply cost function U_pref to get the best product set
    product_sets = __cost_function(product_sets, preference)

    LOGGER.info('Found matching product set "%s"' % product_sets)
    # return the product set
    return product_sets


def __cost_function(product_sets, preference):
    """
    Cost function which decides which product set matches the user preferences.

    :param product_sets:
        set of possible product implementations
    :param preference:
        preference that was defined by the client; containing all the user preferences
    :return:
        The product set that will match the user preferences the best.
    """
    if len(product_sets) == 0:
        return set()

    sorting = dict()
    for current_set in product_sets:
        if not __matches_product_type_preference(current_set, preference.product_type_filter):
            continue
        # will resolve in set that contains the master broker and other bridges; this set is at least on element big
        broker = __get_broker_of_products(current_set)

        x = 1
        if preference.product_preference == PRODUCT_PREF_EXTENDABILITY:
            x = 0
            for product in current_set:
                x += len(__get_protocols(product, True)) + len(__get_protocols(product, False))
            sorting[current_set] = 1.0 / (float(len(broker)**2) / x)
        elif preference.product_preference == PRODUCT_PREF_PRICE:
            for product in current_set:
                x += product.price
            sorting[current_set] = 1. / x * 0.95 ** len(broker)
        elif preference.product_preference == PRODUCT_PREF_EFFICIENCY:
            for product in current_set:
                x += product.efficiency
            sorting[current_set] = 1. / x * 0.95 ** len(broker)
        else:
            raise(AttributeError("Unsupported preference %s" % preference.product_preference))
        # search for minimum
    if sorting:
        return sorted(sorting.items(), key=operator.itemgetter(1))[-1][0]
    return set()


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


def __product_type_filter_satisfiable(meta_implementations, filters):
    """
    Checks if a given set of product implementations of meta devices contains a
    configuration that satisfies the given product type filter.

    :param meta_implementations:
        a set containing sets of all products that implement each meta device in
        a scenario
    :param filters:
        the set of product type filters
    :return:
        whether or not there is a way to choose a product from each set so that
        all product types in the filters are satisfied by the choice
    """
    # start by creating a set that contains a frozenset of the filters
    remaining_filters = set()
    remaining_filters.add(frozenset(filters))
    # now go over each meta device that will be implemented
    for ps in meta_implementations:
        previous_filters = remaining_filters.copy()
        # and over each product that implements this meta device
        for p in ps:
            # and see what product type filters we would still need to satisfy
            # if we chose this product. (f - frozenset((p.product_type.id,)))
            # The remaining_filters set represents the choices we already took.
            # It is necessary because two implementations of a certain meta
            # device might each be able to satisfy one of the product type
            # filters but we can only choose one of them. In this case, the
            # remaining_filters set (assuming the complete set of filters is
            # {1,2}) would be {{1} if we chose the first product, {2} if we
            # chose the second product, {1,2} if we chose neither}
            remaining_filters |= set(
                    f - frozenset((p.product_type.id,))
                    for f in previous_filters)

    return frozenset() in remaining_filters


def __matches_product_type_preference(product_set, product_type_filters):
    """
    Filters a given product set for the given product type filters.

    :param product_set:
        the given product set
    :param product_type_filters:
        the given product type filters (list of pk of product types)
    :return:
        if the product set contains all of the given product type filters
    """
    if not product_type_filters:
        return True

    input_hash = hash((frozenset(product_set), frozenset(product_type_filters)))

    tmp = cache.get(input_hash)
    if tmp is not None:
        return tmp

    product_types = set()
    for product in product_set:
        product_types.add(product.product_type_id)

    res = all(product_type in product_types for product_type in product_type_filters)
    cache.set(input_hash, res)
    return res


def __find_implementing_product(meta_device, renovation_allowed):
    """
    Find all implementing products to a given meta_device.
    This have to fit two criteria:
    1. the product must implement all features of the meta device
    2. the product must speak at least one protocol in the given mode

    :param
        meta_device: the meta device that should be implemented
    :return:
        set of all matching products that have at least one protocol matching
        the defined behavior (e.g. broker -> least one leader protocol;
        endpoint -> at least one follower protocol.)
    """
    products = __get_products(renovation_allowed)
    meta_feature = set(meta_device.implementation_requires.all())
    matching_products = set()
    for product in products:
        if meta_feature.issubset(set(product.features.all())):
            if len(__get_protocols(product, meta_device.is_broker)) != 0:
                matching_products.add(product)
    return matching_products


def __find_communication_partner(endpoint, target, renovation_allowed,  path=None, max_depth=None, bridges_visited=None):
    """
    This function will serve the purpose we called small "f". It will find all ways from a given endpoint
    to a given target (most likely the master broker in the scenario/system). For this it will recursively
    traverse through the graph of which products can communicate with which other products.

    :param endpoint:
        the endpoint where the current path should start searching
    :param target:
        the target which is broker or the master broker
    :param renovation_allowed:
        if renovation is allowed in the users home
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
        LOGGER.error('Recursive call exceeded maximal depth.')
        raise Exception("max_depth exceeded")

    # define methods for follower/leader protocols
    endpoint_protocols = __get_protocols(endpoint, False)
    bridges = __get_bridges(renovation_allowed).difference({endpoint}).difference(current_bridges_visited).union({target})

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
                next_path = __find_communication_partner(bridge, target, renovation_allowed, current_path, max_depth - 1, bridges)
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
    input_hash = hash((frozenset(broker_protocols), frozenset(endpoint_protocols)))
    if cache.get(input_hash) is not None:
        return cache.get(input_hash)

    # check if endpoint can talk directly with broker
    for protocol in endpoint_protocols:
        for broker_protocol in broker_protocols:
            if protocol.name == broker_protocol.name:
                cache.set(input_hash, True, EXPIRATION_TIME)
                return True
    cache.set(input_hash, False)
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
    input_hash = hash((product, leader))
    if cache.get(input_hash) is not None:
        return cache.get(input_hash)

    if leader:
        cache.set(input_hash, set(product.leader_protocol.all()), EXPIRATION_TIME)
    else:
        cache.set(input_hash, set(product.follower_protocol.all()), EXPIRATION_TIME)
    return cache.get(input_hash)


def __get_bridges(renovation_allowed=True):
    """
    Gets all bridges in the product query set.

    :return:
        set of all bridges in the product query set.
    """
    if cache.get(BRIDGES_ID_HASH) is not None:
        return cache.get(BRIDGES_ID_HASH)

    products = __get_products(renovation_allowed)
    return_set = set()
    for product in products:
        if len(__get_protocols(product, True)) > 0 and len(__get_protocols(product, False)) > 0:
            return_set.add(product)

    cache.set(BRIDGES_ID_HASH, return_set.copy(), EXPIRATION_TIME)
    return return_set


def __get_products(renovation_allowed=True):
    """
    Returns all the product as a set.

    :return:
        A set of all known products.
    """
    input_hash = hash((PRODUCT_ID_HASH, renovation_allowed))
    if renovation_allowed:
        return cache.get_or_set(input_hash, set(Product.objects.all()), EXPIRATION_TIME)
    return cache.get_or_set(input_hash, set(Product.objects.filter(renovation_required=False)), EXPIRATION_TIME)


def __get_broker_of_products(product_set):
    return_set = set()
    for product in product_set:
        if len(__get_protocols(product, True)) > 0:
            return_set.add(product)

    return return_set
