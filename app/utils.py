from rest_framework import serializers

class SubmodelSerializer(serializers.ModelSerializer):
    """
    Acts like a ModelSerializer but allows serializing additional sets of fields
    that aren't declared in the base model. These additional fields have to be
    declared in the Meta class as an iterable of tuples of field names stored in
    Meta.optional_field_sets.

    When serializing, fields from optional_field_sets are added to the output
    only if all the fields in the set are present in the input object.

    This serializer does not support deserialization
    """

    def from_representation(self, value):
        raise NotImplementedError("""
            SubmodelSerializer cannot deserialize objects because there is no
            way of knowing what class they should be deserialized as
        """)

    def to_representation(self, value):
        ret = super().to_representation(value)
        for fields in self.Meta.optional_field_sets:
            attrs = {
                key:getattr(value,key,None)
                for key in fields
            }
            if all(attrs[field] is not None for field in fields):
                # add the key value pairs from attrs to ret if
                ret.update(attrs)
        return ret
