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


def implement_scenario(scenario, preference):
    """
    1.  Call find_implementing_product for each meta device in the scenario
    2.  for each Broker -> Endpoint combination find paths with: find_communication_partner(endpoint, broker)
    3.  Merge the result: for each broker check if it can reach all endpoints.
        If possible: create a product set of the current configuration
    4.  Apply U_pref on all product sets for each broker to find the current best solution for the current broker-product-set
    5.  Apply U_pref on all product sets for each different broker to find the overall best solution for the current scenario
    :param scenario
        the scenario where a implementation should be found
    :param preference
        the user preference that was passed by the client
    :return a set of implementing products that matches the user preferences optimally.
    """

    LOGGER.debug('Scenario: %s' % scenario.name)
    meta_broker = scenario.meta_broker
    meta_endpoints = set(scenario.meta_endpoints.all())

    # 1. find implementing products
    impl_of_meta_device = dict()
    LOGGER.debug('Metabroker: %s' % meta_broker)
    impl_of_meta_device[meta_broker] = __find_implementing_product(meta_broker)
    LOGGER.debug(impl_of_meta_device[meta_broker])
    # no implementation was found
    if len(impl_of_meta_device[meta_broker]) == 0:
        return set()

    for meta_endpoint in meta_endpoints:
        LOGGER.debug('Metaendpoint: %s' % meta_endpoint)
        impl_of_meta_device[meta_endpoint] = __find_implementing_product(meta_endpoint)
        LOGGER.debug('%s : %s' % (meta_endpoint, impl_of_meta_device[meta_endpoint]))
        # no implementation was found
        if len(impl_of_meta_device[meta_endpoint]) == 0:
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
                res = __find_communication_partner(endpoint_impl, broker_impl)
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

    LOGGER.info('Start matching for scenario: "%s", found matching product set "%s"' % (scenario.name, product_sets))
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
        if not __matches_renovation_preference(current_set, preference.renovation_preference):
            continue
        if not __filter_product_set(current_set, preference.product_type_filter):
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


def __matches_renovation_preference(product_set, renovation_preference):
    """
    Returns true if the given product set matches the given renovation preference, else false.

    :param product_set:
        the product set that should be checked
    :param renovation_preference:
        the renovation preference of the user, either True or False
    :return:
        True if the given product set matches the requirements
    """
    if renovation_preference:
        return True
    input_hash = hash(frozenset(product_set))
    if cache.get(input_hash) is not None:
        return cache.get(input_hash)
    res = all(not product.renovation_required for product in product_set)
    cache.set(input_hash, res)
    return res


def __filter_product_set(product_set, product_type_filters):
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
    input_hash = hash((frozenset(product_set), product_type_filters))
    if cache.get(input_hash) is not None:
        return cache.get(input_hash)

    product_types = set()
    for product in product_set:
        product_types.add(product.product_type_id)

    res = product_type_filters in product_types
    cache.set(input_hash, res)
    return res


def __find_implementing_product(meta_device):
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
    products = __get_products()
    meta_feature = set(meta_device.implementation_requires.all())
    matching_products = set()
    for product in products:
        if meta_feature.issubset(set(product.features.all())):
            if len(__get_protocols(product, meta_device.is_broker)) != 0:
                matching_products.add(product)
    return matching_products


def __find_communication_partner(endpoint, target, path=None, max_depth=None, bridges_visited=None):
    """
    This function will serve the purpose we called small "f". It will find all ways from a given endpoint
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
        LOGGER.error('Recursive call exceeded maximal depth.')
        raise Exception("max_depth exceeded")

    # define methods for follower/leader protocols
    endpoint_protocols = __get_protocols(endpoint, False)
    bridges = __get_bridges().difference({endpoint}).difference(current_bridges_visited).union({target})

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
                next_path = __find_communication_partner(bridge, target, current_path, max_depth - 1, bridges)
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


def __get_bridges():
    """
    Gets all bridges in the product query set.

    :return:
        set of all bridges in the product query set.
    """
    if cache.get(BRIDGES_ID_HASH) is not None:
        return cache.get(BRIDGES_ID_HASH)

    products = __get_products()
    return_set = set()
    for product in products:
        if len(__get_protocols(product, True)) > 0 and len(__get_protocols(product, False)) > 0:
            return_set.add(product)

    cache.set(BRIDGES_ID_HASH, return_set.copy(), EXPIRATION_TIME)
    return return_set


def __get_products():
    """
    Returns all the product as a set.

    :return:
        A set of all known products.
    """
    return cache.get_or_set(PRODUCT_ID_HASH, set(Product.objects.all()), EXPIRATION_TIME)


def __get_broker_of_products(product_set):
    return_set = set()
    for product in product_set:
        if len(__get_protocols(product, True)) > 0:
            return_set.add(product)

    return return_set
