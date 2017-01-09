# -*- coding: utf-8 -*-

import datetime

from rest_framework import generics, status
from rest_framework import viewsets
from rest_framework.decorators import *

from .logic.match_making import implement_scenario
from .logic.sorting import sort_scenarios
from .forms import LoginForm
from .permissions import *
from .serializers import *
from .validators import *
from .suggestions import SuggestionsInputSerializer, ScenarioImpl, SuggestionsOutputSerializer, SuggestionsPagination, InvalidGETException
from .constants import SUGGESTIONS_INPUT_SESSION_KEY


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

        # call scenario sorting
        sorted_tuple_list = sort_scenarios(Scenario.objects.all(), suggestions_input)
        for scenario, rating in sorted_tuple_list:
            product_set = implement_scenario(scenario, suggestions_input)
            if product_set:
                yield ScenarioImpl(product_set, scenario, rating)

    def get_serializer_class(self):
        return SuggestionsOutputSerializer
