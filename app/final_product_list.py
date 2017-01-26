import collections

from django.core.validators import MinLengthValidator
from rest_framework import serializers, exceptions

from .validators import validate_scenario_id, validate_lockedproducts
from .constants import (
        SHOPPING_BASKET_SCENARIO_ID,
        SHOPPING_BASKET_PRODUCT_TYPE_FILTER,
        LOCKEDPRODUCTS_SLOT_ID,
        LOCKEDPRODUCTS_PRODUCT_ID,
)
from .serializers.v1 import ProductSerializer
from .serializers.matching import (
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
            'locked_products',
        ])


LockedProductEntry = collections.namedtuple(
        'LockedProductEntry', [
            LOCKEDPRODUCTS_SLOT_ID,
            LOCKEDPRODUCTS_PRODUCT_ID,
        ])


class LockedProductEntrySerializer(serializers.Serializer):
    slot_id = serializers.ListField(
            child=serializers.IntegerField(),
            validators=[MinLengthValidator(1)]
    )
    product_id = serializers.IntegerField()


class ProductListInputSerializer(MatchingSerializerBase):
    shopping_basket = serializers.ListField(
            required=True,
            child=ShoppingBasketEntrySerializer(),
            validators=[MinLengthValidator(1), validate_scenario_id]
    )
    locked_products = serializers.ListField(
            required=False,
            default=[],
            child=LockedProductEntrySerializer(),
            validators=[validate_lockedproducts]
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
        validated_data['locked_products'] = frozenset(
                LockedProductEntry(
                        frozenset(entry[LOCKEDPRODUCTS_SLOT_ID]),
                        entry[LOCKEDPRODUCTS_PRODUCT_ID])
                for entry in validated_data['locked_products'])

        return ProductListInput(**validated_data)


class ProductAlternativesInputSerializer(ProductListInputSerializer):
    replacement_slot = serializers.ListField(
            child=serializers.IntegerField(),
            validators=[MinLengthValidator(1)]
    )

    def create(self, validated_data):
        prefs = super(ProductAlternativesInputSerializer, self).create(validated_data)
        return prefs, validated_data['replacement_slot']
