import operator
import logging

from django.core.cache import cache

from ..constants import (
        PRODUCT_PREF_PRICE,
        PRODUCT_PREF_EFFICIENCY,
        PRODUCT_PREF_EXTENDABILITY
)
from .utils import __dict_cross_product
from .data import __get_broker_of_products, __get_protocols


LOGGER = logging.getLogger(__name__)


def __filter_paths_for_valid_broker(paths, meta_endpoint, device_mapping, impl_of_meta_device):
    """
    This method filters the given paths for every path that contains a broker that is a
    valid implementation of the broker of the scenario of the current meta_endpoint.

    :param paths:
        all possible paths of an endpoint implementation to a master broker implementation
    :param meta_endpoint:
        the current endpoint that was implemented
    :param device_mapping:
        the mapping that contains a "original_to_merged" broker function
    :param impl_of_meta_device:
        the dict of a merged meta endpoint to all possible implementation of it
    :return:
        the filtered paths
    """
    if not paths:
        return paths
    else:
        if meta_endpoint in device_mapping.bridges:
            # nothing to validate because we only check if the endpoint is compatible with his broker
            return paths
        else:
            # get all scenarios that this endpoint is implementing
            scenarios = set().union(
                *(device_mapping.endpoints[endpoint]
                    for endpoint in device_mapping.originals_from_merged(meta_endpoint))
            )
            # get all brokers of the scenarios. This brokers are unmerged.
            brokers = {
                scenario.meta_broker for scenario in scenarios
            }
            # find the merged brokers and their implementing products
            merged_broker_products = {
                frozenset(
                    impl_of_meta_device[device_mapping.original_to_merged[broker]]
                ) for broker in brokers
            }
            # prepare a bucket for each broker implementation
            paths_over_broker = {
                broker: set()
                for broker in merged_broker_products
            }
            # check each paths in paths
            for path in paths:
                # that a broker implementation existed
                for broker in merged_broker_products:
                    # that this one of the implementation
                    for tmp_broker_impl in broker:
                        # is contained in the current path
                        if tmp_broker_impl in path:
                            # if this is given then add this path into the bucket of the scenario
                            paths_over_broker[broker].add(frozenset(path))
                            break  # each other check will just add the same values in the bucket
            # compute the cross product of each found bucket implementation.
            # if one bucket was not filled this will return the empty set
            # This is needed because each broker implementation have to be satisfied.
            return __dict_cross_product(paths_over_broker)


def __matches_product_type_preference(product_set, product_type_filters):
    """
    Filters a given product set for the given product type filters.

    TODO: should this really be cached? Does it get used more than once

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
        if not  __matches_product_type_preference(current_set, preference.product_type_filter):
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
