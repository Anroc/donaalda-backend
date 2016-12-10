import collections

from rest_framework import serializers

from .validators import validate_scenario_preference
from .models import Category


SuggestionsInput = collections.namedtuple(
        "OnboardingAnswers", [
            "category_preference",
            "user_preference",
            "renovation_preference"
        ])


class SuggestionsInputSerializer(serializers.Serializer):
    category_preference = serializers.DictField(
            child=serializers.IntegerField(),
            validators=[validate_scenario_preference])
    user_preference = serializers.ChoiceField(
            choices=['Preis', 'Energie', 'Erweiterbarkeit'])
    renovation_preference = serializers.BooleanField()


    def create(self, validated_data):
        return SuggestionsInput(**validated_data)
