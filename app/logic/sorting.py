from operator import itemgetter
from ..models import Category
from ..constants import MINIMAL_RATING_VALUE


def sort_scenarios(scenarios, scenario_preference):
    """
    Sorts the given scenarios on how well they are matching the given preference.

    :param scenarios:
        the given scenarios
    :param scenario_preference:
        the given user preference
    :return:
        sorted tuple list of first entry the scenario and the second entry the matching value.
        (smaller is better)
    """
    scenario_soring = list()
    category_names = Category.objects.values_list('name', flat=True)
    scenario_preference = __normalize(scenario_preference, category_names)

    for scenario in scenarios:
        category_ratings = scenario.scenariocategoryrating_set.all()
        scenario_vector = dict()
        for category_rating in category_ratings:
            scenario_vector[category_rating.category.name] = category_rating.rating

        scenario_vector = __normalize(scenario_vector, category_names)
        distance = 0
        for key in scenario_preference.keys():
            distance += (scenario_preference[key] - scenario_vector[key]) ** 2
        distance **= 0.5

        scenario_soring.append((scenario, distance))

    # http://stackoverflow.com/a/10695161/6190424
    return sorted(scenario_soring, key=itemgetter(1))


def __normalize(dictionary, default_key_set=None):
    """
    Normalize the given dictionary values.

    :param dictionary:
        the given dictionary
    :param default_key_set:
        the default key set. If they are not present their values will be set to 1.
    :return:
        a new reference to the dictionary with the normalized values.
    """
    ret = dictionary.copy()

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
