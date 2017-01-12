# -*- coding: utf-8 -*-

import datetime

from django.core.cache import cache
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import *

from .logic import (
        partition_scenarios,
        sort_scenarios,
        implement_scenarios)
from .forms import LoginForm
from .permissions import *
from .serializers import *
from .validators import *
from .suggestions import SuggestionsInputSerializer, ScenarioImpl, SuggestionsOutputSerializer, SuggestionsPagination, \
    WeAreRESTfulNowException, InvalidShoppingBasketException
from .final_product_list import FinalProductListSerializer, FinalProductListElement, NoShoppingBasketException


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

    def get(self, request, format=None):
        raise WeAreRESTfulNowException

    def post(self, request, format=None):
        return self.list(request)

    def get_queryset(self):
        input_serializer = SuggestionsInputSerializer(data=self.request.data)
        input_serializer.is_valid(raise_exception=True)
        suggestions_input = input_serializer.save()

        # partition scenarios into shopping basket and suggestable
        shopping_basket, sorting_scenarios = partition_scenarios(
                suggestions_input.shopping_basket)
        # call scenario sorting
        sorted_tuple_list = sort_scenarios(sorting_scenarios, suggestions_input)

        if shopping_basket:
            old_product_set, device_mapping = implement_scenarios(shopping_basket, suggestions_input)
            cache.set(hash(str(input_serializer.data)), device_mapping)
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
    def get(self, request, format=None):
        raise WeAreRESTfulNowException

    def post(self, request, format=None):
        return self.list(request)

    def get_queryset(self):

        input_serializer = SuggestionsInputSerializer(data=self.request.data)
        input_serializer.is_valid(raise_exception=True)
        suggestions_input = input_serializer.save()

        device_mapping = cache.get(
            hash(str(input_serializer.data)),
            None
        )

        if device_mapping is None:
            shopping_basket, unused = partition_scenarios(
                    suggestions_input.shopping_basket)
            old_product_set, device_mapping = implement_scenarios(
                    shopping_basket, suggestions_input)
            if not old_product_set:
                raise NoShoppingBasketException
        return [
                FinalProductListElement(product,
                                        [scenario.id for scenario in scenarios]
                                        )
                for product, scenarios in device_mapping.products.items()
            ]

    def get_serializer_class(self):
        return FinalProductListSerializer
