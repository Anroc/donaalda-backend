# -*- coding: utf-8
import re

from django.core.exceptions import ValidationError

from . import models


def validate_legal_chars(value):
    pattern = re.compile("[\WäÄöÖüÜß]")
    if pattern.search(value) is not None:
        raise ValidationError('der Name %(value)s enhält ein unerlaubtes Zeichen. Gültige Zeichen sind a-zA-Z0-9.',
                              params={'value': value}, code='illegal_character')


_ERR_CATEGORIES = 'Category_preference should contain exactly all categories.'
_ERR_VALUES = 'Values should be in the range of 0 to 10'
def validate_scenario_preference(value):
    categories = models.Category.objects.values_list('name', flat=True)
    if value.keys() != set(categories):
        raise ValidationError(_ERR_CATEGORIES)

    for key, value in value.items():
        if not 1 <= value <= 10:
            raise ValidationError(_ERR_VALUES)
