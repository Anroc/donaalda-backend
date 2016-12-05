from rest_framework import serializers
from .models import *
from . import utils
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ('pk', 'name', 'is_visible',)


class ProviderProfileSerializer(serializers.ModelSerializer):
    owner = ProviderSerializer()

    class Meta:
        model = ProviderProfile
        fields = ('pk',
                  'public_name', 'url_name', 'logo_image', 'profile_image', 'banner_image', 'introduction',
                  'contact_email',
                  'website', 'owner',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('pk', 'name', 'picture', 'backgroundPicture', 'short_description', 'description', 'iconString',)


class ProductSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer()

    class Meta:
        model = Product
        fields = ('pk',
                  'name', 'provider', 'product_type', 'serial_number', 'description', 'specifications', 'image1',
                  'image2',
                  'image3', 'end_of_life',)


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('pk', 'type_name',)


class ScenarioSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer()

    class Meta:
        model = Scenario
        fields = (
            'pk', 'name', 'url_name', 'short_description', 'picture', 'provider',)


class SubCategorySerializer(serializers.ModelSerializer):
    belongs_to_category = CategorySerializer()

    class Meta:
        model = SubCategory
        fields = ('pk', 'belongs_to_category', 'name', 'url_name', 'short_description', 'picture',)


class SubCategoryDescriptionSerializer(serializers.ModelSerializer):
    belongs_to_subcategory = SubCategorySerializer()

    class Meta:
        model = SubCategoryDescription
        fields = ('pk', 'belongs_to_subcategory', 'description', 'image', 'left_right', 'order',)


class EmployeeSerializer(serializers.ModelSerializer):
    employer = ProviderSerializer()

    class Meta:
        model = Employee
        fields = ('pk', 'employer',)


class UserImageSerializer(serializers.ModelSerializer):
    belongs_to_user = UserSerializer()

    class Meta:
        model = UserImage
        fields = ('pk', 'belongs_to_user', 'image',)


class CommentSerializer(serializers.ModelSerializer):
    comment_from = UserSerializer()

    class Meta:
        model = Comment
        fields = ('pk', 'comment_from', 'comment_title', 'comment_content', 'rating', 'creation_date', 'page_url',)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('pk', 'belongs_to_question', 'answer_text',)


class QuestionSerializer(utils.SubmodelSerializer):
    answer_set = AnswerSerializer(read_only=True, many=True)

    class Meta:
        model = Question
        fields = (
            'pk',
            'question_text',
            'answer_presentation',
            'order',
            'answer_set',
        )
        optional_field_sets = (
            ('rating_min', 'rating_max'),
        )


class GivenAnswersSerializer(utils.SubmodelSerializer):
    user = UserSerializer()
    user_answer = AnswerSerializer(read_only=True, many=True)

    class Meta:
        model = GivenAnswers
        fields = ('pk', 'user', 'user_answer',)
        optional_field_sets = (
            ('rating_value',),
        )


class QuestionSetSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True, many=True)

    class Meta:
        model = QuestionSet
        fields = ('pk', 'name', 'question', 'order',)


class QuestionStepSerializer(serializers.ModelSerializer):
    question_steps = QuestionSetSerializer(read_only=True, many=True)

    class Meta:
        model = QuestionStep
        fields = ('pk', 'name', 'question_steps',)
