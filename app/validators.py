# -*- coding: utf-8

from django.core.exceptions import ValidationError
import re


def validate_legal_chars(value):
    pattern = re.compile("[\WäÄöÖüÜß]")
    if pattern.search(value) is not None:
        raise ValidationError('der Name %(value)s enhält ein unerlaubtes Zeichen. Gültige Zeichen sind a-zA-Z0-9.',
                              params={'value': value}, code='illegal_character')

