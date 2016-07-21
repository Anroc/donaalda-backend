from rest_framework import serializers
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('pk', 'name', 'picture', 'backgroundPicture', 'short_description', 'description', 'iconString',)


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ('pk', 'name', 'url_name', 'short_description', 'picture', 'provider', 'scenario_product_set', 'categories',)


class ScenarioDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioDescription
        fields = ('pk', 'belongs_to_scenario', 'description', 'image', 'thumbnail', 'left_right', 'order',)


class ProductSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSet
        fields = ('pk', 'name', 'description', 'products', 'creator', 'tags',)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('pk',
            'name', 'provider', 'product_type', 'serial_number', 'description', 'specifications', 'image1', 'image2',
            'image3', 'end_of_life', 'tags',)


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('pk', 'type_name',)


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ('pk', 'name', 'is_visible',)


class ProviderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderProfile
        fields = ('pk',
            'public_name', 'url_name', 'logo_image', 'profile_image', 'banner_image', 'introduction', 'contact_email',
            'website', 'owner',)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('pk', 'employer',)


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ('pk', 'belongs_to_user', 'image',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('pk', 'comment_from', 'comment_title', 'comment_content', 'rating', 'creation_date', 'page_url',)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('pk', 'question_text', 'answer_presentation', 'order',)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('pk', 'belongs_to_question', 'answer_text', 'tag',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('pk', 'code', 'name',)


class GivenAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GivenAnswers
        fields = ('pk', 'user', 'user_answer',)


class QuestionSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionSet
        fields = ('pk', 'name', 'question', 'category', 'order',)


class SessionTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionTags
        fields = ('pk', 'session', 'tag',)


class QuestionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionStep
        fields = ('pk', 'name', 'question_steps',)
