import collections

from rest_framework import serializers

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
