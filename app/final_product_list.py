import collections

from django.core.validators import MinLengthValidator
from rest_framework import serializers, exceptions

from .validators import validate_scenario_id
from .constants import (
        SHOPPING_BASKET_SCENARIO_ID,
        SHOPPING_BASKET_PRODUCT_TYPE_FILTER,
)
from .serializers import (
        ProductSerializer,
        MatchingSerializerBase,
        ShoppingBasketEntrySerializer,
        ShoppingBasketEntry,
)


class FinalProductListElement(object):
    def __init__(self, product, scenarios):
        self.product = product
        self.scenarios = scenarios


class FinalProductListSerializer(serializers.Serializer):
    product = ProductSerializer()
    scenarios = serializers.ListField(child=serializers.IntegerField())


class NoShoppingBasketException(exceptions.APIException):
    status_code = 400
    default_code = 'client error'
    default_detail = 'Need at least one scenario in the shopping basket.'


ProductListInput = collections.namedtuple(
        'ProductListInput', [
            'product_preference',
            'renovation_preference',
            'shopping_basket',
        ])


class ProductListInputSerializer(MatchingSerializerBase):
    shopping_basket = serializers.ListField(
            required=True,
            child=ShoppingBasketEntrySerializer(),
            validators=[MinLengthValidator(1), validate_scenario_id]
    )

    def create(self, validated_data):
        # TODO: There is a little bit of code duplication here. Both this class
        # and SuggestionsInputSerializer transform the shopping basket into a
        # hashable representation. It would be nice if we found a way to handle
        # this in one place
        validated_data['shopping_basket'] = frozenset(
                ShoppingBasketEntry(
                        entry[SHOPPING_BASKET_SCENARIO_ID],
                        frozenset(entry[SHOPPING_BASKET_PRODUCT_TYPE_FILTER]))
                for entry in validated_data['shopping_basket'])

        return ProductListInput(**validated_data)
