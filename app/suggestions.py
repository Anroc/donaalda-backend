import collections

from rest_framework import serializers, exceptions

from .constants import *
from .serializers import ScenarioSerializer

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
            choices=[PRODUCT_PREF_PRICE, PRODUCT_PREF_EFFICIENCY, PRODUCT_PREF_EXTENDABILITY])
    renovation_preference = serializers.BooleanField()

    product_type_filter = serializers.ListField(
            child=serializers.IntegerField(),
            validators=[validate_producttype_filter])
    subcategory_filter = serializers.ListField(
            child=serializers.IntegerField(),
            validators=[validate_subcategory_filter])

    def create(self, validated_data):
        return SuggestionsInput(**validated_data)


class ScenarioImpl(object):
    def __init__(self, product_set, scenario, rating):
        self.scenario = scenario
        self.rating = rating
        self.product_set = product_set
        self.price = 0.0
        self.efficiency = 0
        self.extendability = 0
        self.compute_specs()

    def compute_specs(self):
        protocols = set()
        for product in self.product_set:
            self.price += product.price
            self.efficiency += product.efficiency
            protocols = protocols.union(
                set(product.leader_protocol.all()).union(set(product.follower_protocol.all())))
        self.extendability = len(protocols)


class SuggestionsOutputSerializer(serializers.Serializer):
    scenario = ScenarioSerializer()

    price = serializers.FloatField()
    efficiency = serializers.IntegerField()
    extendability = serializers.IntegerField()
    rating = serializers.FloatField()


class InvalidGETException(exceptions.APIException):
    status_code = 400
    default_code = 'client error'
    default_detail = 'A POST requests that sets the onboarding preferences is required before a GET to the suggestions endpoint is possible'
