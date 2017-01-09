# -*- coding: utf-8 -*-

import datetime

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import *

from .logic import implement_scenarios
from .logic.sorting import sort_scenarios
from .forms import LoginForm
from .permissions import *
from .serializers import *
from .validators import *
from .suggestions import SuggestionsInputSerializer, ScenarioImpl, SuggestionsOutputSerializer, SuggestionsPagination, \
    InvalidGETException, InvalidShoppingBasketException
from .final_product_list import FinalProductListSerializer, FinalProductListElement, NoShoppingBasketException
from .constants import SUGGESTIONS_INPUT_SESSION_KEY, SHOPPING_BASKET_SCENARIO_ID, SHOPPING_BASKET_SESSION_KEY


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ScenarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer


class SubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


class SubCategoryDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubCategoryDescription.objects.all()
    serializer_class = SubCategoryDescriptionSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(end_of_life=False)
    serializer_class = ProductSerializer


class ProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer


class ProviderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class ProviderProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProviderProfile.objects.all()
    serializer_class = ProviderProfileSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


@permission_classes((permissions.AllowAny,))
class Suggestions(generics.ListAPIView):
    pagination_class = SuggestionsPagination

    def post(self, request, format=None):
        self.request.session[SUGGESTIONS_INPUT_SESSION_KEY] = request.data
        return self.list(request)

    def get_queryset(self):
        request_data = self.request.session.get(
                SUGGESTIONS_INPUT_SESSION_KEY, None)
        if request_data is None:
            raise InvalidGETException

        input_serializer = SuggestionsInputSerializer(data=request_data)
        input_serializer.is_valid(raise_exception=True)
        suggestions_input = input_serializer.save()

        scenario_ids = set()
        scenarios = Scenario.objects.prefetch_related(
            'meta_broker__implementation_requires',
            'meta_endpoints__implementation_requires'
        ).all()
        for basket_elem in suggestions_input.shopping_basket:
            scenario_ids.add(basket_elem[SHOPPING_BASKET_SCENARIO_ID])

        shopping_basket = set()
        sorting_scenarios = set()
        for scenario in scenarios:
            if scenario.pk in scenario_ids:
                shopping_basket.add(scenario)
            else:
                sorting_scenarios.add(scenario)

        # call scenario sorting
        sorted_tuple_list = sort_scenarios(sorting_scenarios, suggestions_input)

        if shopping_basket:
            old_product_set, device_mapping = implement_scenarios(shopping_basket, suggestions_input)
            cache.set(shopping_basket_hash(request_data['shopping_basket']), device_mapping)
            if not old_product_set:
                raise InvalidShoppingBasketException
        else:
            old_product_set = None

        for scenario, rating in sorted_tuple_list:
            # don't need the device mappings
            product_set = implement_scenarios(shopping_basket.union({scenario}), suggestions_input)[0]
            if product_set:
                yield ScenarioImpl(product_set, old_product_set, scenario, rating)

    def get_serializer_class(self):
        return SuggestionsOutputSerializer


@permission_classes((permissions.AllowAny,))
class FinalProductList(generics.ListAPIView):
    def get_queryset(self):
        request_data = self.request.session.get(
                SUGGESTIONS_INPUT_SESSION_KEY, None)
        if request_data is None:
            raise InvalidGETException
        device_mapping = cache.get(
            shopping_basket_hash(request_data['shopping_basket']),
            None
        )
        if device_mapping is None:
            raise NoShoppingBasketException
        return [
                FinalProductListElement(product,
                                        [scenario.id for scenario in scenarios]
                                        )
                for product, scenarios in device_mapping.products.items()
            ]

    def get_serializer_class(self):
        return FinalProductListSerializer


def shopping_basket_hash(shopping_basket):
    h = {hash((key, tuple(value))) for key, value in shopping_basket}
    return hash(frozenset(h))
