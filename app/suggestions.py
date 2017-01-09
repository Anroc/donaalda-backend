import itertools
import collections

from rest_framework import pagination, serializers, exceptions
from rest_framework.utils.urls import replace_query_param

from .constants import *
from .serializers import ScenarioSerializer, ProductTypeSerializer

from .validators import (
        validate_scenario_preference,
        validate_producttype_filter,
        validate_subcategory_filter,
        validate_scenario_id,
)


class GeneratorPagination(pagination.LimitOffsetPagination):
    """
    A pagination style for "querysets" that are actually cached generator
    functions.

    The thing that differentiates this from a standard LimitOffsetPagination
    style is that with a generator, you don't know the count before evaluating
    the whole generator (which would probably be quite expensive).

    An alternative base for this would have been CursorPagination but that
    one uses to many features that are specific to django querysets to be useful
    for us.
    """
    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request

        ret = list(itertools.islice(
                queryset, self.offset, self.offset + self.limit))

        self.count = len(ret)
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        return ret

    def get_next_link(self):
        if self.limit > self.count:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.offset + self.limit
        return replace_query_param(url, self.offset_query_param, offset)


class SuggestionsPagination(GeneratorPagination):
    default_limit = 6


SuggestionsInput = collections.namedtuple(
        'SuggestionsInput', [
            'scenario_preference',
            'product_preference',
            'renovation_preference',
            'product_type_filter',
            'subcategory_filter',
            'shopping_basket',
        ])


class ShoppingBasketEntrySerializer(serializers.Serializer):
    scenario_id = serializers.IntegerField()
    product_type_filter = serializers.ListField(
            child=serializers.IntegerField()
    )


class SuggestionsInputSerializer(serializers.Serializer):
    scenario_preference = serializers.DictField(
            child=serializers.IntegerField(),
            validators=[validate_scenario_preference])
    product_preference = serializers.ChoiceField(
            choices=[PRODUCT_PREF_PRICE, PRODUCT_PREF_EFFICIENCY, PRODUCT_PREF_EXTENDABILITY])
    renovation_preference = serializers.BooleanField()

    product_type_filter = serializers.ListField(
            required=False,
            default=[],
            child=serializers.IntegerField(),
            validators=[validate_producttype_filter]
    )
    subcategory_filter = serializers.ListField(
            required=False,
            default=[],
            child=serializers.IntegerField(),
            validators=[validate_subcategory_filter])
    shopping_basket = serializers.ListField(
            required=False,
            default=[],
            child=ShoppingBasketEntrySerializer(),
            validators=[validate_scenario_id]
    )

    def create(self, validated_data):
        return SuggestionsInput(**validated_data)


class ScenarioImpl(object):
    def __init__(self, product_set, old_product_set, scenario, rating):
        self.scenario = scenario
        self.rating = rating
        self.product_set = product_set
        self.price = 0.0
        self.efficiency = 0
        self.extendability = 0
        self.renovation_required = False
        self.product_types = set()
        self.compare_specs(old_product_set)

    def compare_specs(self, old_product_set):
        self.price, self.efficiency, self.product_types, self.extendability, self.renovation_required = \
            compute_specs(self.product_set)
        if old_product_set is not None:
            price, efficiency, unused, extendability, unused = compute_specs(old_product_set)
            self.price -= price
            self.efficiency -= efficiency
            self.extendability -= extendability


def compute_specs(product_set):
    protocols = set()
    price = 0
    efficiency = 0
    product_types = set()
    renovation_required = False
    for product in product_set:
        price += product.price
        efficiency += product.efficiency
        protocols = protocols.union(
            set(product.leader_protocol.all()).union(set(product.follower_protocol.all())))
        product_types.add(product.product_type)
        renovation_required |= product.renovation_required
    extendability = len(protocols)
    return price, efficiency, product_types, extendability, renovation_required


class SuggestionsOutputSerializer(serializers.Serializer):
    scenario = ScenarioSerializer()

    price = serializers.FloatField()
    efficiency = serializers.IntegerField()
    extendability = serializers.IntegerField()
    rating = serializers.FloatField()
    renovation_required = serializers.BooleanField()
    product_types = ProductTypeSerializer(many=True)


class InvalidGETException(exceptions.APIException):
    status_code = 400
    default_code = 'client error'
    default_detail = 'A POST requests that sets the onboarding preferences is required before a GET to the suggestions endpoint is possible'


class InvalidShoppingBasketException(exceptions.APIException):
    status_code = 400
    default_code = 'client error'
    default_detail = 'The given shopping basket is not implementable.'
