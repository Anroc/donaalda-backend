import collections

from rest_framework import serializers
from operator import itemgetter

from .models import Category
from .validators import (
        validate_scenario_preference,
        validate_producttype_filter,
        validate_subcategory_filter,
)


SuggestionsInput = collections.namedtuple(
        'SuggestionsInput', [
            'scenario_preference',
            'product_preference',
            'renovation_preference',
            'product_type_filter',
            'subcategory_filter',
        ])


class SuggestionsInputSerializer(serializers.Serializer):
    scenario_preference = serializers.DictField(
            child=serializers.IntegerField(),
            validators=[validate_scenario_preference])
    product_preference = serializers.ChoiceField(
            choices=['Preis', 'Energie', 'Erweiterbarkeit'])
    renovation_preference = serializers.BooleanField()

    product_type_filter = serializers.ListField(
            child=serializers.IntegerField(),
            validators=[validate_producttype_filter])
    subcategory_filter = serializers.ListField(
            child=serializers.IntegerField(),
            validators=[validate_subcategory_filter])

    def create(self, validated_data):
        return SuggestionsInput(**validated_data)


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
    compare_vector = [
        scenario_preference['Energie'],
        scenario_preference['Gesundheit'],
        scenario_preference['Sicherheit'],
        scenario_preference['Komfort']
    ]

    for scenario in scenarios:
        category_ratings = scenario.scenariocategoryrating_set.all()
        scenario_vector = [1, 1, 1, 1]
        for category_rating in category_ratings:
            if category_rating.category.name == "Energie":
                scenario_vector[0] = category_rating.rating
            elif category_rating.category.name == "Gesundheit":
                scenario_vector[1] = category_rating.rating
            elif category_rating.category.name == "Sicherheit":
                scenario_vector[2] = category_rating.rating
            elif category_rating.category.name == "Komfort":
                scenario_vector[3] = category_rating.rating
            else:
                raise AttributeError("Unsupported category name '%s'", category_rating.name)

        distance = 0
        for i in range(0,len(scenario_vector)):
            distance += (compare_vector[i] - scenario_vector[i]) ** 2
        distance **= 0.5

        scenario_soring.append((scenario, distance))

    # http://stackoverflow.com/a/10695161/6190424
    return sorted(scenario_soring, key=itemgetter(1))
