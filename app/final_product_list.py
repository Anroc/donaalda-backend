import collections

from django.core.validators import MinLengthValidator
from rest_framework import serializers, exceptions

from .validators import validate_scenario_id, validate_lockedproducts
from .constants import (
        LOCKEDPRODUCTS_SLOT_ID,
        LOCKEDPRODUCTS_PRODUCT_ID,
)
from .serializers.v1 import ProductSerializer
from .serializers.matching import (
        MatchingSerializerBase,
        MatchingInputBase,
        ShoppingBasketEntrySerializer,
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
        'ProductListInput', set(MatchingInputBase._fields).union({
            'locked_products',
        }))


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
    # we need to override the shopping bakset serializer from the super class
    # because it is no longer optional.
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
        # see app/suggestions.py for details why this is implemented this way
        base = super().create(validated_data.copy())
        validated_data.update(base._asdict())

        validated_data['locked_products'] = frozenset(
                LockedProductEntry(
                        frozenset(entry[LOCKEDPRODUCTS_SLOT_ID]),
                        entry[LOCKEDPRODUCTS_PRODUCT_ID])
                for entry in validated_data['locked_products'])

        for unused_key in validated_data.keys() - set(ProductListInput._fields):
            del validated_data[unused_key]

        return ProductListInput(**validated_data)


class ProductAlternativesInputSerializer(ProductListInputSerializer):
    replacement_slot = serializers.ListField(
            child=serializers.IntegerField(),
            validators=[MinLengthValidator(1)]
    )

    def create(self, validated_data):
        prefs = super().create(validated_data.copy())
        return prefs, validated_data['replacement_slot']
