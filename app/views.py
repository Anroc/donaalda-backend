# -*- coding: utf-8 -*-

import datetime

from django.core.cache import cache
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import *

from .logic import (
    partition_scenarios,
    sort_scenarios,
    implement_scenarios_from_input)
from .forms import LoginForm
from .permissions import *
from .serializers.v1 import *
from .validators import *
from .suggestions import (
        SuggestionsInputSerializer,
        ScenarioImpl,
        SuggestionsOutputSerializer,
        SuggestionsPagination,
        WeAreRESTfulNowException,
        InvalidShoppingBasketException
)
from .final_product_list import (
        ProductListInputSerializer,
        ProductAlternativesInputSerializer,
        FinalProductListSerializer,
        FinalProductListElement,
        ProductAlternativesSerializer,
        ProductAlternativesElement,
        NoShoppingBasketException,
        InvalidReplacementSlotException,
)


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
        sorted_tuple_list = sort_scenarios(
                sorting_scenarios, suggestions_input)

        if shopping_basket:
            old_solution = implement_scenarios_from_input(None, shopping_basket, suggestions_input)
            if not old_solution:
                raise InvalidShoppingBasketException
            old_product_set = old_solution.products.keys()
        else:
            old_product_set = None

        for scenario, rating in sorted_tuple_list:
            # don't need the device mappings
            new_solution = implement_scenarios_from_input(scenario, shopping_basket, suggestions_input)
            if new_solution:
                yield ScenarioImpl(new_solution.products.keys(), old_product_set, scenario, rating)

    def get_serializer_class(self):
        return SuggestionsOutputSerializer


@permission_classes((permissions.AllowAny,))
class FinalProductList(generics.ListAPIView):
    def get(self, request, format=None):
        raise WeAreRESTfulNowException

    def post(self, request, format=None):
        return self.list(request)

    def get_queryset(self):
        input_serializer = ProductListInputSerializer(data=self.request.data)
        input_serializer.is_valid(raise_exception=True)
        productlist_input = input_serializer.save()

        shopping_basket_scenarios, unused = partition_scenarios(
                productlist_input.shopping_basket)

        # the serializer validates both that the basket is non empty and that
        # the ids in it are valid
        assert shopping_basket_scenarios

        solution = implement_scenarios_from_input(
            None, shopping_basket_scenarios, productlist_input
        )

        if not solution:
            raise InvalidShoppingBasketException

        return [
                FinalProductListElement(product, [
                        metadevice.pk for metadevice in meta.meta_devices
                ], [
                        scenario.pk for scenario in meta.scenarios
                ])
                for product, meta in solution.products.items()
            ]

    def get_serializer_class(self):
        return FinalProductListSerializer


@permission_classes((permissions.AllowAny,))
class ProductAlternatives(generics.ListAPIView):
    serializer_class = ProductAlternativesSerializer

    def get(self, request, format=None):
        raise WeAreRESTfulNowException

    def post(self, request, format=None):
        return self.list(request)

    def get_queryset(self):
        input_serializer = ProductAlternativesInputSerializer(data=self.request.data)
        input_serializer.is_valid(raise_exception=True)
        productlist_input, slot_ids = input_serializer.save()

        shopping_basket_scenarios, unused = partition_scenarios(
                productlist_input.shopping_basket)

        # the serializer validates both that the basket is non empty and that
        # the ids in it are valid
        assert shopping_basket_scenarios

        solution = implement_scenarios_from_input(
                None, shopping_basket_scenarios, productlist_input
        )

        if not solution:
            raise InvalidShoppingBasketException

        slot = frozenset(MetaDevice.objects.filter(pk__in=slot_ids))

        if slot not in solution.slot_alternatives:
            raise InvalidReplacementSlotException

        # mockety mock mock mothermocker
        return [ ProductAlternativesElement(p) for p in solution.slot_alternatives[slot] ]
