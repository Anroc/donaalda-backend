import json
import logging
import unittest

import openapi
import jsonschema
from jsonschema.validators import RefResolver
from django.test import TestCase
from django.core.management.base import BaseCommand
from rest_framework.schemas import SchemaGenerator


class IgnoreFilterFieldsSchemaGenerator(SchemaGenerator):
    def get_filter_fields(*args, **kwargs):
        return []


# code shamelessly stolen from
# https://python-jsonschema.readthedocs.io/en/latest/faq/#why-doesn-t-my-schema-that-has-a-default-property-actually-set-the-default-on-my-instance
# slightly modified because I only need one validator and that one doesn't need
# to validate the properties, only add the default values
def set_defaults(validator, properties, instance, schema):
    for property, subschema in properties.items():
        if "default" in subschema:
            instance.setdefault(property, subschema["default"])

# we have default values for everything (including required fields). Because of
# this, we have to validate requied with a no op to ensure that missing required
# fields (which are going to be added by defaults) don't throw exceptions
DefaultAddingValidator = jsonschema.validators.extend(
    jsonschema.validators.Draft4Validator, {
        "properties" : set_defaults,
        "required" : lambda *args, **kwargs: None
    },
)


class Command(BaseCommand):
    help = """
    Runs a series of tests on the database to verify that the requests in the
    api description schema (swagger) produce the expected results.
    """

    def handle(self, *args, **options):
        suite = unittest.TestLoader().loadTestsFromTestCase(SchemaTest)
        logging.disable(logging.CRITICAL)
        unittest.TextTestRunner().run(suite)
        logging.disable(logging.NOTSET)


class SchemaTest(TestCase):
    def test_swagger_endpoints(self):
        # get the static swagger schema
        json_schema = json.load(open("app/static/swagger.json"))
        resolver = jsonschema.validators.RefResolver.from_schema(json_schema)
        swagger = openapi.Swagger(json_schema)

        swagger.validate()

        for uri, path in swagger.paths.items():
            for method, operation in path.items():
                # only test the post'able swagger endpoints
                if 'swagger' not in operation['tags']:
                    continue
                with self.subTest(uri=uri, method=method):
                    self.runOperation(uri, method, operation, resolver)

    def runOperation(self, uri, method, operation, resolver):
        # we might add other methods in the future but until then, this will
        # ensure that we don't forget to update the tests
        self.assertEqual(method, 'post')

        body_params = list(filter(
            lambda param: param['in'] == 'body',
            operation['parameters']))

        # the swagger spec says that there should only be one body parameter
        self.assertEqual(len(body_params), 1)
        request_schema = body_params[0]['schema']

        # extract the default input that is shown in the swagger ui
        default_data = {}
        DefaultAddingValidator(
                request_schema, resolver=resolver).validate(default_data)

        # validate it against the swagger schema
        jsonschema.validate(
                default_data, request_schema, resolver=resolver)

        # throw it against the test server
        response = self.client.post(
                uri, json.dumps(default_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_v1_endpoints(self):
        # get the api schema
        generator = IgnoreFilterFieldsSchemaGenerator()
        schema = generator.get_schema()

        v1_endpoints = schema['v1']

        for name, obj in v1_endpoints.items():
            for method, link in obj.items():
                # only test 'list' endpoints for now
                if method != 'list':
                    continue

                #print("Testing endpoint %s (%s)" % (name, method))
                self.assertFalse(any(field.required for field in link.fields))
                response = getattr(self.client, link.action)(link.url)
                self.assertEqual(response.status_code, 200)
