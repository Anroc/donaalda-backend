# -*- coding: utf-8
import re

from django.core.exceptions import ValidationError

import app.models
from .constants import (
        SHOPPING_BASKET_PRODUCT_TYPE_FILTER,
        SHOPPING_BASKET_SCENARIO_ID,
        LOCKEDPRODUCTS_PRODUCT_ID,
        LOCKEDPRODUCTS_SLOT_ID
)


def validate_legal_chars(value):
    pattern = re.compile("[\WäÄöÖüÜß]")
    if pattern.search(value) is not None:
        raise ValidationError('der Name %(value)s enhält ein unerlaubtes Zeichen. Gültige Zeichen sind a-zA-Z0-9.',
                              params={'value': value}, code='illegal_character')


def _validate_ids(value, model, message):
    """Validate that a set of values only contains things that are valid public
    keys for the given model. Otherwise a ValidationError with the given message
    is raised"""
    modelids = model.objects.values_list('pk', flat=True)
    # checking it this way instead of set(value).issubset(...) avoids overhead
    # if the value is already a set (issuperset works on any iterable)
    if not set(modelids).issuperset(value):
        raise ValidationError(message)


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
    _validate_ids(value, app.models.ProductType, _ERR_PRODUCTTYPES)


_ERR_SUBCATEGORIES = 'Subcategory filters may only contain valid subcategory ids'


def validate_subcategory_filter(value):
    _validate_ids(value, app.models.SubCategory, _ERR_PRODUCTTYPES)


_ERR_SCENARIOS = 'Shopping basket may contain invalid scenario ids'


# TODO: this just validates a shopping basket. It should be renamed to
# validate_shoppingbasket or something like that
def validate_scenario_id(value):
    basket_scenario_ids = set()
    basket_product_type_filter = set()
    for val in value:
        basket_scenario_ids.add(val[SHOPPING_BASKET_SCENARIO_ID])
        basket_product_type_filter.update(val[SHOPPING_BASKET_PRODUCT_TYPE_FILTER])

    _validate_ids(basket_scenario_ids, app.models.Scenario, _ERR_SCENARIOS)
    _validate_ids(basket_product_type_filter, app.models.ProductType, _ERR_PRODUCTTYPES)


_ERR_SLOTID = 'Invalid slot id'
_ERR_PRODUCTID = 'Invalid product id'

def validate_lockedproducts(value):
    slotid_metadevices = set()
    productids = set()
    for val in value:
        slotid_metadevices.update(val[LOCKEDPRODUCTS_SLOT_ID])
        productids.add(val[LOCKEDPRODUCTS_PRODUCT_ID])

    _validate_ids(slotid_metadevices, app.models.MetaDevice, _ERR_SLOTID)
    _validate_ids(productids, app.models.Product, _ERR_PRODUCTID)
