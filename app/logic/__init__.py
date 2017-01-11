import logging

from .merging import DeviceMapping
from .implementing import compute_matching_product_set
from .validating import __cost_function

# These are just imported for encapsulation so that everywherre else in the code
# just has to import stuff from the top level module
from .sorting import sort_scenarios
from .data import partition_scenarios

LOGGER = logging.getLogger(__name__)


def implement_scenarios(scenarios, preference):
    """
    This method takes a set of scenarios and merge them in that kind that
    meta devices that provide the same feature set are just listed onces.

    :param scenarios:
        the scenarios that should be implemented with the current shopping basket
    :param preference:
        the user defined preference
    :return:
        best matching implementing product set
        todo change
    """
    # merging the endpoints
    meta_device_mapping = DeviceMapping()
    for scenario in scenarios:
        meta_device_mapping.merge_scenario(scenario)

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
