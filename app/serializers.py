from rest_framework import serializers
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'picture', 'backgroundPicture', 'short_description', 'description', 'iconString',)


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ('name', 'url_name', 'short_description', 'picture', 'provider', 'scenario_product_set', 'categories',)


class ScenarioDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioDescription
        fields = ('belongs_to_scenario', 'description', 'image', 'thumbnail', 'left_right', 'order',)


class ProductSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSet
        fields = ('name', 'description', 'products', 'creator', 'tags',)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'name', 'provider', 'product_type', 'serial_number', 'description', 'specifications', 'image1', 'image2',
            'image3', 'thumbnail', 'end_of_life', 'tags',)


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('type_name',)


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ('name', 'is_visible',)


class ProviderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderProfile
        fields = (
            'public_name', 'url_name', 'logo_image', 'profile_image', 'banner_image', 'introduction', 'contact_email',
            'website', 'owner',)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('employer',)


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ('belongs_to_user', 'image',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('comment_from', 'comment_title', 'comment_content', 'rating', 'creation_date', 'page_url',)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('question_text', 'answer_presentation', 'order',)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('belongs_to_question', 'answer_text', 'tag',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('code', 'name',)


class GivenAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GivenAnswers
        fields = ('user', 'user_answer',)


class QuestionSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionSet
        fields = ('name', 'question', 'category', 'order',)


class SessionTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionTags
        fields = ('session', 'tag',)


class QuestionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionStep
        fields = ('name', 'question_steps',)
