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


class DeviceMapping(object):
    """
    Class for saving dicts of meta devices to scenarios and
    product to scenarios.
    """
    endpoints = dict()
    broker = dict()

    products = dict()

    def __init__(self, endpoints=None, broker=None, products=None):
        if endpoints is None:
            endpoints = dict()
        if broker is None:
            broker = dict()
        if products is None:
            products = dict()
        self.endpoints = endpoints
        self.broker = broker
        self.products = products

    def get_any_broker(self):
        return list(self.broker.keys())[0]

    def add_product(self, meta_device, product):
        scenarios = set()
        if product in self.products:
            scenarios = self.products[product]
        if meta_device.is_broker and meta_device in self.broker:
            self.products[product] = self.broker[meta_device].union(scenarios)
            return
        # else: broker is shifted to endpoints
        self.products[product] = self.endpoints[meta_device].union(scenarios)

    def add_products(self, meta_device, products):
        for product in products:
            self.add_product(meta_device, product)

    def shift_all_brokers_except(self, broker):
        other = self.__copy__()
        for b in self.broker.keys():
            if b is not broker:
                scenarios = other.broker.pop(broker)
                other.endpoints[broker] = scenarios
        return other

    def __copy__(self):
        return DeviceMapping(self.endpoints.copy(), self.broker.copy(), self.products.copy())

    def intersect_products(self, products):
        tmp = dict()
        for product in products:
            tmp[product] = self.products[product]
        self.products = tmp


def implement_scenario(scenario, preference, shopping_basket=None):
    """
    This method takes a set of scenarios and merge them in that kind that
    meta devices that provide the same feature set are just listed onces.

    :param scenario:
        the scenario that should be implemented with the current shopping basket
    :param preference:
        the user defined preference
    :param shopping_basket: (optional)
        set of scenarios that are in the shopping basket of the user
    :return:
        best matching implementing product set
        todo change
    """
    if shopping_basket is None:
        scenario_ids = set()
        # get shopping basket elements
        for basket_elem in preference.shopping_basket:
            scenario_ids.add(basket_elem[SHOPPING_BASKET_SCENARIO_ID])
            shopping_basket = set(
                Scenario.objects.prefetch_related(
                    'meta_broker__implementation_requires',
                    'meta_endpoints__implementation_requires'
                ).filter(id__in=scenario_ids)
            )

    # merge shopping basket with new scenario
    scenarios = shopping_basket.copy()
    scenarios.add(scenario)

    # merging the endpoints
    meta_device_mapping = DeviceMapping()
    for scenario in scenarios:
        # merge meta broker
        meta_device_mapping.broker = __merge_meta_device(
                {scenario.meta_broker},
                meta_device_mapping.broker,
                scenario
        )

        # merge meta endpoints
        meta_device_mapping.endpoints = __merge_meta_device(
                set(scenario.meta_endpoints.all()),
                meta_device_mapping.endpoints,
                scenario
        )

    # 1. case: meta brokers contain only one element
    if len(meta_device_mapping.broker) == 1:
        # we are finished here
        # call matching function to compute the reset
        return compute_matching_product_set(meta_device_mapping, preference)

    # 2. case: meta brokers contain more then one element
    all_possible_solutions = dict()

    for meta_broker in meta_device_mapping.broker.keys():
        res, device_mapping = compute_matching_product_set(
                meta_device_mapping.shift_all_brokers_except(meta_broker),
                preference
            )
        res = frozenset(res)
        if res:
            all_possible_solutions[res] = device_mapping

    if len(all_possible_solutions) == 0:
        # 2.1. if all possible solutions have no elements we return the empty set
        return set(), None
    elif len(all_possible_solutions) == 1:
        # 2.2. if all possible solutions have only one solution we are done.
        return all_possible_solutions.popitem()
    else:
        # 2.3 if all possible solutions have more then one element we have to apply the cost function again
        solution = __cost_function(set(all_possible_solutions.keys()), preference)
        return solution, all_possible_solutions[frozenset(solution)]


def __merge_meta_device(meta_devices, meta_device_mapping, scenario):
    """
    Merges a given set of meta_devices into a present_set of thous.
    This method also checks if the current features of the meta devices can be already satisfied by
    an element in the present set.

    :param meta_devices:
        the meta_devices that should be added in the set of present devices
    :param meta_device_mapping:
        a dictionary of either meta broker or meta endpoints to scenarios.
        See the class DeviceMapping for more information.
    :param scenario
        the scenario of the meta_devices that should be added.
    :return:
        the merge dict of meta devices to scenario
    """
    device_mapping = meta_device_mapping.copy()
    merged_endpoints = set(device_mapping.keys()).copy()

    if not merged_endpoints:
        me = meta_devices.pop()
        merged_endpoints.add(me)
        device_mapping[me] = {scenario}
    tmp_add_entries = dict()
    tmp_remove_keys = set()

    # check if the given meta endpoint has features that are already satisfied by other meta endpoints
    for cme in meta_devices:
        # matching on pk
        features_cme = set(cme.implementation_requires.values_list('pk', flat=True))
        for me in merged_endpoints:
            features_me = set(me.implementation_requires.values_list('pk', flat=True))
            if features_me.issubset(features_cme):
                tmp_remove_keys.add(me)
                tmp_add_entries[cme] = device_mapping[me].union({scenario})
            elif not features_cme.issubset(features_me):
                tmp_add_entries[cme] = {scenario}

    for tmp_remove_key in tmp_remove_keys:
        del device_mapping[tmp_remove_key]
    # add the meta_endpoints to the set of meta endpoints
    device_mapping.update(tmp_add_entries)
    return device_mapping


def compute_matching_product_set(device_mapping, preference):
    """
    1.  Call find_implementing_product for each meta device in the scenario
    2.  for each Broker -> Endpoint combination find paths with: find_communication_partner(endpoint, broker)
    3.  Merge the result: for each broker check if it can reach all endpoints.
        If possible: create a product set of the current configuration
    4.  Apply U_pref on all product sets for each broker to find the current best solution for the current broker-product-set
    5.  Apply U_pref on all product sets for each different broker to find the overall best solution for the current scenario
    :param device_mapping:
        An instance of the class DeviceMapping that contains a dict of
        meta endpoints and meta broker. This method will use this attributes to compute the matching
        on thous.
        It will also fill the product dictionary in this class and return a reference to this class.
    :param preference
        the user preference that was passed by the client
    :return a set of implementing products that matches the user preferences optimally.
    change
    """
    # validation:
    if len(device_mapping.broker) != 1:
        raise RuntimeError("Expected ONE broker as base of operations.")

    meta_broker = device_mapping.get_any_broker()
    meta_endpoints = set(device_mapping.endpoints.keys())

    # 1. find implementing products
    impl_of_meta_device = dict()
    LOGGER.debug('Metabroker: %s' % meta_broker)
    impl_of_meta_device[meta_broker] = __find_implementing_product(meta_broker, preference.renovation_preference)

    LOGGER.debug(impl_of_meta_device[meta_broker])

    for meta_endpoint in meta_endpoints:
        LOGGER.debug('Metaendpoint: %s' % meta_endpoint)
        impl_of_meta_device[meta_endpoint] = __find_implementing_product(meta_endpoint, preference.renovation_preference)
        LOGGER.debug('%s : %s' % (meta_endpoint, impl_of_meta_device[meta_endpoint]))
        # no implementation was found
        if len(impl_of_meta_device[meta_endpoint]) == 0:
            return set(), device_mapping

    # check product type filter
    if not __product_type_filter_satisfiable(impl_of_meta_device.values(), preference):
        return set(), device_mapping

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

        # add products to DeviceMapping
        device_mapping.add_product(meta_broker, broker_impl)
        for me in meta_endpoints:
            for path in possible_paths[me]:
                device_mapping.add_products(me, path)

        merged_set = __merge_paths(meta_endpoints, possible_paths)
        # 3. apply cost function U_pref to get one product set
        merged_set = __cost_function(merged_set, preference)

        if merged_set:
            # 4. merge all product sets
            product_sets.add(merged_set)

    # 5. apply cost function U_pref to get the best product set
    product_sets = __cost_function(product_sets, preference)

    LOGGER.info('Found matching product set "%s"' % product_sets)

    # cleanup DeviceMapping
    device_mapping.intersect_products(product_sets)

    # return the product set
    return product_sets, device_mapping


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
        # we want to know exactly which set is not satisfiable (the reason of {current_set})
        if not __product_type_filter_satisfiable({current_set}, preference):
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


def __product_type_filter_satisfiable(meta_implementations, preference):
    """
    Checks if a given set of product implementations of meta devices contains a
    configuration that satisfies the given product type filter.

    :param meta_implementations:
        a set containing sets of all products that implement each meta device in
        a scenario
    :param preference:
        the user preference
    :return:
        whether or not there is a way to choose a product from each set so that
        all product types in the filters are satisfied by the choice
    """
    # TODO: maybe remove later
    filters = set()
    for basket_elem in preference.shopping_basket:
        filters = filters.union(set(basket_elem[SHOPPING_BASKET_PRODUCT_TYPE_FILTER]))
    filters = filters.union(set(preference.product_type_filter))

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
        return cache.get_or_set(
            input_hash,
            set(Product.objects.prefetch_related(
                'product_type',
                'protocol_leader',
                'protocol_follower',
                'features'
            ).all()),
            EXPIRATION_TIME
        )
    return cache.get_or_set(
        input_hash,
        set(Product.objects.prefetch_related(
                'product_type',
                'leader_protocol',
                'follower_protocol',
                'features'
            ).filter(renovation_required=False)),
        EXPIRATION_TIME)


def __get_broker_of_products(product_set):
    return_set = set()
    for product in product_set:
        if len(__get_protocols(product, True)) > 0:
            return_set.add(product)

    return return_set
