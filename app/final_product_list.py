from rest_framework import serializers
from .serializers import ProductSerializer, ScenarioSerializer


class FinalProductListElement(object):
    def __init__(self, product, scenarios):
        self.product = product
        self.scenarios = scenarios


class FinalProductListSerializer(serializers.Serializer):
    product = ProductSerializer()
    scenarios = serializers.ListField(child=serializers.IntegerField())
