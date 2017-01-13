from operator import itemgetter

import math
from ..models import Category
from ..constants import MINIMAL_RATING_VALUE


def sort_scenarios(scenarios, preference):
    """
    Sorts the given scenarios on how well they are matching the given preference.

    :param scenarios:
        the given scenarios
    :param preference:
        the preference generated by the client
    :return:
        sorted tuple list of first entry the scenario and the second entry the matching value.
        (smaller is better)
    """
    scenario_soring = list()
    category_names = Category.objects.values_list('name', flat=True)
    user_category_pref = __normalize(preference.scenario_preference, category_names)

    # filter scenarios
    scenarios = __filter_scenarios(scenarios, preference.subcategory_filter)

    for scenario in scenarios:
        category_ratings = scenario.scenariocategoryrating_set.all()
        scenario_vector = dict()
        for category_rating in category_ratings:
            scenario_vector[category_rating.category.name] = category_rating.rating

        scenario_vector = __normalize(scenario_vector, category_names)

        # divide by pi/2 to get values between one and zero
        # Invert the result to get 1 as the best and 0 as the worst
        angle = 1. - __angle(user_category_pref, scenario_vector) / (math.pi / 2.)

        scenario_soring.append((scenario, angle))

    # http://stackoverflow.com/a/10695161/6190424
    return sorted(scenario_soring, key=itemgetter(1), reverse=True)


def __normalize(dictionary, default_key_set=None):
    """
    Normalize the given dictionary values.

    :param dictionary:
        the given dictionary (may be an immutable dictionary, aka a frozenset of
        (key, value) pairs
    :param default_key_set:
        the default key set. If they are not present their values will be set to 1.
    :return:
        a new reference to the dictionary with the normalized values.
    """
    # create a new dictionary from the input. This method is better than
    # dictionary.copy() because it correctly handles immutable dictionaries
    ret = dict(dictionary)

    if default_key_set is None:
        default_key_set = ret.keys()

    length = 0
    for key in default_key_set:
        if key not in ret:
            ret[key] = MINIMAL_RATING_VALUE
        length += ret[key] ** 2
    length **= 0.5

    for key in default_key_set:
        ret[key] /= length

    return ret


def __dot_product(dict1, dict2):
    return sum(dict1[k]*dict2[k] for k in dict1.keys())


def __length(dic):
    return math.sqrt(__dot_product(dic, dic))


def __angle(dict1, dict2):
    return math.acos(__dot_product(dict1, dict2) / (__length(dict1) * __length(dict2)))


def __filter_scenarios(scenarios, subcategory_filter):
    if not subcategory_filter:
        return scenarios
    return {scenario for scenario in scenarios if scenario.subcategory.filter(pk__in=subcategory_filter)}
