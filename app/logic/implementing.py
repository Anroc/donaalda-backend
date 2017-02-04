import logging
import collections

from ..models import Scenario
from .data import __find_implementing_product, __get_bridges, __get_protocols, __direct_compatible
from .validating import Path, __filter_paths_for_valid_broker, __matches_product_type_preference, __cost_function
from .utils import __dict_cross_product, dict_cross_product


LOGGER = logging.getLogger(__name__)


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
    assert len(device_mapping.broker) == 1, "Expected ONE broker as base of operations."

    meta_broker = device_mapping.get_any_broker()
    meta_endpoints = set(device_mapping.endpoints.keys()).union(set(device_mapping.bridges.keys()))

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

    # 2. start running F
    # we already validated that each endpoint have at least one implementation
    product_sets = set()
    for broker_impl in impl_of_meta_device[meta_broker]:
        # this enables us to do paths[thing].add(thing) without having to check
        # if thing is already a key in there.
        possible_paths = collections.defaultdict(set)

        for meta_endpoint in meta_endpoints:
            for endpoint_impl in impl_of_meta_device[meta_endpoint]:
                # 2.1 call f
                # take an broker impl and an endpoint impl and find the matching ways
                res = __find_communication_partner(endpoint_impl, broker_impl, preference.renovation_preference)
                res = __filter_paths_for_valid_broker(res, meta_endpoint, device_mapping, impl_of_meta_device)
                for path_set in res:
                    path = Path(endpoint_impl, path_set)

                    possible_paths[meta_endpoint].add(path)

                    LOGGER.debug('%s->%s: %s' % (endpoint_impl, broker_impl, path))

        # check if current broker impl can reach every endpoint
        if len(meta_endpoints) != len(possible_paths):
            continue

        # add products to DeviceMapping
        device_mapping.add_product(meta_broker, broker_impl)
        for me in meta_endpoints:
            for path in possible_paths[me]:
                device_mapping.add_products(me, path.products)

        solutions = dict_cross_product(possible_paths)
        merged_set = set(map(lambda thing: frozenset().union(*map(lambda d: d.products, thing.values())), solutions))

        # apply filter for current scenario
        if device_mapping.suggested_scenario is not None:
            merged_set = __remove_mismatching_paths(
                device_mapping.suggested_scenario, device_mapping, preference.product_type_filter, merged_set
            )

        # filter for valid product filter of shopping basket
        for basket_elem in preference.shopping_basket:
            # TODO: resolve the shopping basket scenario id -> scenario
            # reference at the view layer
            scenario = Scenario.objects.get(pk=basket_elem.scenario_id)
            pt_preference = basket_elem.product_type_filter
            merged_set = __remove_mismatching_paths(scenario, device_mapping, pt_preference, merged_set)

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


def __remove_mismatching_paths(scenario, device_mapping, pt_filter, merged_set):
    """
    Removes all mismatching paths from a given merged path set.

    :param scenario:
        the scenario that is the filter indicator for each path that uses at least one device that is a valid
        implemenation of a scenario meta device
    :param device_mapping:
        the well known device mapping
    :param pt_filter:
        the current product type filter either read from the shopping basket or the user product type preference
    :param merged_set:
        the set of sets of product paths
    :return:
        the new filtered sets of sets of product paths
    """
    remove_paths = set()
    for p_set in merged_set:
        scenario_p_set = {elem for elem in p_set if scenario in device_mapping.products[elem]}
        if not __matches_product_type_preference(scenario_p_set, pt_filter):
            remove_paths.add(p_set)
    return {elem for elem in merged_set if elem not in remove_paths}


def __find_communication_partner(endpoint, target, renovation_allowed,  path=None, max_depth=None):
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

    # begin of the algorithm
    if max_depth <= 0:
        LOGGER.error('Recursive call exceeded maximal depth.')
        raise Exception("max_depth exceeded")

    # define methods for follower/leader protocols
    endpoint_protocols = __get_protocols(endpoint, False)

    assert endpoint not in current_path
    current_path.add(endpoint)
    paths = list()

    bridges = __get_bridges(renovation_allowed).difference(current_path).union({target})

    if len(bridges) == 0:
        return list()

    for bridge in bridges:
        if __direct_compatible(__get_protocols(bridge, True), endpoint_protocols):
            if bridge == target:
                current_path.add(target)
                paths.append(current_path)
            else:
                # recursive call with the current bridge as a new endpoint
                next_path = __find_communication_partner(bridge, target, renovation_allowed, current_path, max_depth - 1)
                if len(next_path) != 0:
                    paths.extend(next_path)
    return paths
