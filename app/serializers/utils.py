"""This module contains a few serializer related utilities."""

import markdown

from rest_framework import serializers


class MarkdownField(serializers.CharField):
    """A serializer field that interprets its input as markdown and returns a
    rendered representation.

    When deserializing, this behaves like a standard CharField. It will not try
    to parse any html (e.g. '<h1>title</h1><br />text' will be treated as is and
    not transformed to '#title\ntext'
    """
    def to_representation(self, instance):
        return markdown.markdown(instance)


class PkToIdSerializer(serializers.ModelSerializer):
    """A serializer that exposes an id field that is sourced from a django
    models pk attribute.

    The automatically generated primary key of django models is also called id
    but it may be overridden. This also serves to check that the primary key is
    an Integer since some of the code probably relies on that (or at least that
    it is sortable and/or hashable)
    """
    id = serializers.IntegerField(source='pk')
