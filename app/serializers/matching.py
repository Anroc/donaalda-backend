"""This module contains common serializers and datastructures for inputs to the
matching algorithm. They are used in the scenario and product selection phases.

There are additional serializers in app.suggestions and app.final_product_list
that are specific to their respective phases.
"""

import collections

from rest_framework import serializers

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


class MatchingSerializerBase(serializers.Serializer):
    """
    Contains fields that are needed for all endpoints throughout the
    consultation process.
    """
    product_preference = serializers.ChoiceField(
            choices=[PRODUCT_PREF_PRICE, PRODUCT_PREF_EFFICIENCY, PRODUCT_PREF_EXTENDABILITY])
    renovation_preference = serializers.BooleanField()
