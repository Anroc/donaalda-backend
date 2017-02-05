import operator
import logging
import collections

from .cache import cached

from ..constants import (
        PRODUCT_PREF_PRICE,
        PRODUCT_PREF_EFFICIENCY,
        PRODUCT_PREF_EXTENDABILITY
)
from .utils import __dict_cross_product
from .data import get_broker_of_products, __get_protocols


LOGGER = logging.getLogger(__name__)


class Path(object):
    """Represents a path between a endpoint from the merged meta device set and
    the current implementation of the master broker.

    Because of the way compute_matching_product_set is implemented, we only need
    to store the implementation of the meta device and the set of products
    involved in the communication (including endpoint and broker). The meta
    device, the meta broker are aparent from the context the paths are created
    in.
    """

    def __init__(self, endpoint_impl, products):
        self.endpoint_impl = endpoint_impl
        self.products = products


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
            scenarios = device_mapping.endpoints[meta_endpoint]

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


@cached(lambda ps, ptf: hash((frozenset(ps), frozenset(ptf))))
def matches_product_type_preference(product_set, product_type_filters):
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

    product_types = set()
    for product in product_set:
        product_types.add(product.product_type_id)

    return all(product_type in product_types for product_type in product_type_filters)


def __cost_function(solutions, preference):
    """
    Cost function which decides which product set matches the user preferences
    best.

    :param product_sets:
        set of possible product implementations, already checked for validity.
    :param preference:
        preference that was defined by the client; containing all the user preferences
    :return:
        The product set that will match the user preferences the best.
    """
    if not solutions:
        return None

    # this just selects the first element of the input set (afterwards iterator
    # will allow for x in ying over the other elements of the set)
    iterator = iter(solutions)
    best = next(iterator)

    # kickstart our product alternatives collection
    alternatives = collections.defaultdict(set, best.slot_alternatives)

    for solution in iterator:
        # merge slot alternatives by adding the slot -> product mappings from the new solution
        for slot, products in solution.slot_alternatives.items():
            alternatives[slot].update(products)

        # continue with the new best solution
        if solution.rating(preference) > best.rating(preference):
            best = solution

    # update the product alternatives of the found best solution
    best.slot_alternatives = alternatives

    # and return it
    return best


SolutionProductMeta = collections.namedtuple(
        'SolutionProductMeta', [
            'meta_devices', 'scenarios'
        ])


class Solution(object):
    """Represents a (not necessarily valid) Solution (which is a set of products
    with some meta information attached)."""

    def __init__(self, path_choice, meta_broker, broker_impl, device_mapping):
        """Construct a solution from a path choice which maps every meta device
        to a path to a possible implementation."""
        self.products = collections.defaultdict(
                lambda: SolutionProductMeta(set(), set()))
        self.slot_alternatives = collections.defaultdict(set)

        for metadevice, path in path_choice.items():
            scenarios = device_mapping.get_scenarios_for_metadevice(metadevice)
            self.products[path.endpoint_impl].meta_devices.add(metadevice)
            for product in path.products:
                self.products[product].scenarios.update(scenarios)

        # TODO: figure out how to extract what products implement the mandatory
        # brokers in device_mapping.bridges. This information gets lost
        # somewhere in __filter_paths_for_valid_broker

        # set the meta device for the master broker (the scenarios are already
        # set since it is included in every path)
        self.products[broker_impl].meta_devices.add(meta_broker)

        # fill the slot alternatives (currently just with the products from this
        # solution, they will be merged together with other solutions later)
        for product, meta in self.products.items():
            if meta.meta_devices != set():
                self.slot_alternatives[frozenset(meta.meta_devices)].add(product)

        # we need to remove the factory from the default dict to make the
        # solution cachable (pickle can't serialize lambdas)
        self.products.default_factory = None
        # we technically don't need to do this because the constructor of set is
        # serializable but it is probably a good idea to do it anyway to avoid
        # bugs
        self.slot_alternatives.default_factory = None

    def rating(self, preference):
        """Return a (floating point) number representing the cost of this
        solution according to the product preference (price, extendability,
        ...).

        Higher is better.
        """
        # will resolve in set that contains the master broker and other bridges; this set is at least on element big
        broker = get_broker_of_products(self.products.keys())

        x = 1
        if preference.product_preference == PRODUCT_PREF_EXTENDABILITY:
            x = 0
            for product in self.products:
                x += len(__get_protocols(product, True)) + len(__get_protocols(product, False))
            return 1.0 / (float(len(broker)**2) / x)
        elif preference.product_preference == PRODUCT_PREF_PRICE:
            for product in self.products:
                x += product.price
            return 1. / x * 0.95 ** len(broker)
        elif preference.product_preference == PRODUCT_PREF_EFFICIENCY:
            for product in self.products:
                x += product.efficiency
            return 1. / x * 0.95 ** len(broker)
        else:
            raise(AttributeError("Unsupported preference %s" % preference.product_preference))

    def validate_scenario_product_filter(self, scenario, pt_filter):
        scenario_p_set = {
                elem for elem, meta in self.products.items()
                if scenario in meta.scenarios}
        return matches_product_type_preference(scenario_p_set, pt_filter)
