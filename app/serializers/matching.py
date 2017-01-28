"""This module contains common serializers and datastructures for inputs to the
matching algorithm. They are used in the scenario and product selection phases.

There are additional serializers in app.suggestions and app.final_product_list
that are specific to their respective phases.
"""

import collections

from rest_framework import serializers

from ..validators import validate_scenario_id
from ..constants import (
        SHOPPING_BASKET_SCENARIO_ID,
        SHOPPING_BASKET_PRODUCT_TYPE_FILTER,
        PRODUCT_PREF_PRICE,
        PRODUCT_PREF_EFFICIENCY,
        PRODUCT_PREF_EXTENDABILITY,
)


ShoppingBasketEntry = collections.namedtuple(
        'ShoppingBasketEntry', [
            SHOPPING_BASKET_SCENARIO_ID,
            SHOPPING_BASKET_PRODUCT_TYPE_FILTER])


class ShoppingBasketEntrySerializer(serializers.Serializer):
    scenario_id = serializers.IntegerField()
    product_type_filter = serializers.ListField(
            child=serializers.IntegerField()
    )


MatchingInputBase = collections.namedtuple(
        'MatchingInputBase', [
                'shopping_basket',
                'product_preference',
                'renovation_preference',
        ])


class MatchingSerializerBase(serializers.Serializer):
    """
    Contains fields that are needed for all endpoints throughout the
    consultation process.
    """
    shopping_basket = serializers.ListField(
            required=False,
            default=[],
            child=ShoppingBasketEntrySerializer(),
            validators=[validate_scenario_id]
    )
    product_preference = serializers.ChoiceField(
            choices=[PRODUCT_PREF_PRICE, PRODUCT_PREF_EFFICIENCY, PRODUCT_PREF_EXTENDABILITY])
    renovation_preference = serializers.BooleanField()

    def create(self, validated_data):
        """Turn the validated data into a hashable representation and return it
        as a namedtuple."""
        validated_data['shopping_basket'] = frozenset(
                ShoppingBasketEntry(
                        entry[SHOPPING_BASKET_SCENARIO_ID],
                        frozenset(entry[SHOPPING_BASKET_PRODUCT_TYPE_FILTER]))
                for entry in validated_data['shopping_basket'])

        # remove all unused keys not needed by the MatchingInputBase constructor
        for unused_key in validated_data.keys() - set(MatchingInputBase._fields):
            del validated_data[unused_key]

        # technically, this isn't needed anywhere but it is consistent with the
        # behaviour of the more specialized matching serializers so I am keeping
        # this for better extendability
        return MatchingInputBase(**validated_data)
