# -*- coding: utf-8
import re

from django.core.exceptions import ValidationError

import app.models
from .constants import (
        SHOPPING_BASKET_PRODUCT_TYPE_FILTER,
        SHOPPING_BASKET_SCENARIO_ID,
)


def validate_legal_chars(value):
    pattern = re.compile("[\WäÄöÖüÜß]")
    if pattern.search(value) is not None:
        raise ValidationError('der Name %(value)s enhält ein unerlaubtes Zeichen. Gültige Zeichen sind a-zA-Z0-9.',
                              params={'value': value}, code='illegal_character')


_ERR_CATEGORIES = 'Category_preference should contain exactly all categories.'
_ERR_VALUES = 'Values should be in the range of 0 to 10'


def validate_scenario_preference(value):
    categories = app.models.Category.objects.values_list('name', flat=True)
    if value.keys() != set(categories):
        raise ValidationError(_ERR_CATEGORIES)

    for key, value in value.items():
        if not 1 <= value <= 10:
            raise ValidationError(_ERR_VALUES)


_ERR_PRODUCTTYPES = 'Producttype filters may only contain valid producttype ids'


def validate_producttype_filter(value):
    producttype_ids = app.models.ProductType.objects.values_list('pk', flat=True)
    if not set(value).issubset(set(producttype_ids)):
        raise ValidationError(_ERR_PRODUCTTYPES)


_ERR_SUBCATEGORIES = 'Subcategory filters may only contain valid subcategory ids'


def validate_subcategory_filter(value):
    subcategory_ids = app.models.SubCategory.objects.values_list('pk', flat=True)
    if not set(value).issubset(set(subcategory_ids)):
        raise ValidationError(_ERR_SUBCATEGORIES)


_ERR_SCENARIOS = 'Shopping basket may contain invalid scenario ids'


# TODO: this just validates a shopping basket. It should be renamed to
# validate_shoppingbasket or something like that
def validate_scenario_id(value):
    scenario_ids = app.models.Scenario.objects.values_list('pk', flat=True)
    basket_scenario_ids = set()
    basket_product_type_filter = set()
    for val in value:
        basket_scenario_ids.add(val[SHOPPING_BASKET_SCENARIO_ID])
        basket_product_type_filter.update(val[SHOPPING_BASKET_PRODUCT_TYPE_FILTER])
    if not basket_scenario_ids.issubset(scenario_ids):
        raise ValidationError(_ERR_SCENARIOS)
    validate_producttype_filter(basket_product_type_filter)
