# -*- coding: utf-8

from django.core.exceptions import ValidationError
import re


def validate_legal_chars(value):
    pattern = re.compile("[\WäÄöÖüÜß]")
    if pattern.search(value) is not None:
        raise ValidationError('der Name %(value)s enhält ein unerlaubtes Zeichen. Gültige Zeichen sind a-zA-Z0-9.',
                              params={'value': value}, code='illegal_character')


def validate_suggestions_input(value, categories):
    if value.category_preference.keys() != set(c.name for c in categories):
        raise ValidationError('Category_preference should contain exactly all categories.')

    for key, value in value.category_preference.items():
        if not 1 <= value <= 10:
            raise ValidationError('Values should be in the range of 0 to 10')
