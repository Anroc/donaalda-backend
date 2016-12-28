from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class PkToIdSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class ProviderSerializer(PkToIdSerializer):
    class Meta:
        model = Provider
        fields = ('id', 'name', 'is_visible',)


class ProviderProfileSerializer(PkToIdSerializer):
    owner = ProviderSerializer()

    class Meta:
        model = ProviderProfile
        fields = ('id',
                  'public_name', 'url_name', 'logo_image', 'profile_image', 'banner_image', 'introduction',
                  'contact_email',
                  'website', 'owner',)


class CategorySerializer(PkToIdSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'picture', 'backgroundPicture', 'short_description', 'description', 'iconString',)


class ProductSerializer(PkToIdSerializer):
    provider = ProviderSerializer()

    class Meta:
        model = Product
        fields = ('id',
                  'name', 'provider', 'product_type', 'serial_number', 'description', 'specifications', 'image1',
                  'image2',
                  'image3', 'end_of_life',)


class ProductTypeSerializer(PkToIdSerializer):
    class Meta:
        model = ProductType
        fields = ('id', 'type_name',)


class ScenarioSerializer(PkToIdSerializer):
    provider = ProviderSerializer()

    class Meta:
        model = Scenario
        fields = (
            'id', 'name', 'description', 'url_name', 'picture', 'provider', 'subcategory', )


class SubCategorySerializer(PkToIdSerializer):
    belongs_to_category = CategorySerializer(read_only=True, many=True)

    class Meta:
        model = SubCategory
        fields = ('id', 'belongs_to_category', 'name', 'url_name', 'short_description', 'picture',)


class SubCategoryDescriptionSerializer(PkToIdSerializer):
    belongs_to_subcategory = SubCategorySerializer()

    class Meta:
        model = SubCategoryDescription
        fields = ('id', 'belongs_to_subcategory', 'description', 'image', 'left_right', 'order',)


class EmployeeSerializer(PkToIdSerializer):
    employer = ProviderSerializer()

    class Meta:
        model = Employee
        fields = ('id', 'employer',)


class UserImageSerializer(PkToIdSerializer):
    belongs_to_user = UserSerializer()

    class Meta:
        model = UserImage
        fields = ('id', 'belongs_to_user', 'image',)


class CommentSerializer(PkToIdSerializer):
    comment_from = UserSerializer()

    class Meta:
        model = Comment
        fields = ('id', 'comment_from', 'comment_title', 'comment_content', 'rating', 'creation_date', 'page_url',)


class AnswerSerializer(PkToIdSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'description', 'belongs_to_question', 'answer_text', 'icon_name')


class QuestionSerializer(PkToIdSerializer):
    answer_set = AnswerSerializer(read_only=True, many=True)

    class Meta:
        model = Question
        fields = (
            'id',
            'title',
            'question_text',
            'description',
            'answer_presentation',
            'order',
            'rating_min',
            'rating_max',
            'icon_name',
            'answer_set',
        )


class GivenAnswersSerializer(PkToIdSerializer):
    user = UserSerializer()
    user_answer = AnswerSerializer(read_only=True, many=True)

    class Meta:
        model = GivenAnswers
        fields = ('id', 'user', 'user_answer', 'rating_value',)
