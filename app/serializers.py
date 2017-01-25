import markdown
import collections

from rest_framework import serializers
from django.contrib.auth.models import User

from .models import *
from .constants import (
        SHOPPING_BASKET_SCENARIO_ID,
        SHOPPING_BASKET_PRODUCT_TYPE_FILTER,
        PRODUCT_PREF_PRICE,
        PRODUCT_PREF_EFFICIENCY,
        PRODUCT_PREF_EXTENDABILITY,
)


class MarkdownField(serializers.CharField):
    def to_representation(self, instance):
        return markdown.markdown(instance)


class PkToIdSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')


# TODO: the next 3 things don't really look like they belong here but I don't
# know where else to put them. suggestions.py and final_product_list.py fall out
# because they are used in both. logic also doesn't fit since they are mostly
# relevant for gluing the view and logic levels together.
ShoppingBasketEntry = collections.namedtuple(
        'ShoppingBasketEntry', [
            SHOPPING_BASKET_SCENARIO_ID,
            SHOPPING_BASKET_PRODUCT_TYPE_FILTER])


class ShoppingBasketEntrySerializer(serializers.Serializer):
    scenario_id = serializers.IntegerField()
    product_type_filter = serializers.ListField(
            child=serializers.IntegerField()
    )


class MatchingSerializerBase(serializers.Serializer):
    """
    Contains fields that are needed for all endpoints throughout the
    consultation process.
    """
    product_preference = serializers.ChoiceField(
            choices=[PRODUCT_PREF_PRICE, PRODUCT_PREF_EFFICIENCY, PRODUCT_PREF_EXTENDABILITY])
    renovation_preference = serializers.BooleanField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class ProviderSerializer(PkToIdSerializer):
    class Meta:
        model = Provider
        fields = ('id', 'name', 'is_visible', 'public_name', 'logo_image')


class ProviderProfileSerializer(PkToIdSerializer):
    owner = ProviderSerializer()

    class Meta:
        model = ProviderProfile
        fields = ('id',
                  'url_name', 'profile_image', 'banner_image', 'introduction',
                  'contact_email',
                  'website', 'owner',)


class CategorySerializer(PkToIdSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'picture', 'backgroundPicture', 'short_description', 'description', 'iconString',)


class ProductTypeSerializer(PkToIdSerializer):
    class Meta:
        model = ProductType
        fields = ('id', 'type_name', 'svg_id', 'icon')


class ProductSerializer(PkToIdSerializer):
    provider = ProviderSerializer()
    product_type = ProductTypeSerializer()
    extendability = serializers.SerializerMethodField()
    description = MarkdownField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'provider', 'product_type', 'serial_number', 'description',
                  'image1', 'image2', 'image3', 'price', 'efficiency', 'extendability',
                  'renovation_required', )

    def get_extendability(self, obj):
        return obj.leader_protocol.count() + obj.follower_protocol.count()


class ScenarioCategoryRatingSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.ReadOnlyField(source='category.name')
    id = serializers.ReadOnlyField(source='category.id')

    class Meta:
        model = ScenarioCategoryRating
        fields = ('id', 'name', 'rating', )


class MinimalSubCategorySerializer(PkToIdSerializer):
    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'picture', )


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


class ScenarioSerializer(PkToIdSerializer):
    provider = ProviderSerializer()
    subcategory = MinimalSubCategorySerializer(read_only=True, many=True)
    category_ratings = ScenarioCategoryRatingSerializer(many=True)

    class Meta:
        model = Scenario
        fields = (
            'id', 'name', 'description', 'url_name', 'picture', 'provider', 'subcategory', 'category_ratings', )


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
