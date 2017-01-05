from rest_framework import serializers, exceptions
from .serializers import ProductSerializer


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
