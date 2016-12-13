# -*- coding: utf-8 -*-

import unittest

from django.test import Client
from rest_framework.schemas import SchemaGenerator


class SchemaTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        # get the api schema
        generator = SchemaGenerator()
        self.schema = generator.get_schema()

    def test_v1_endpoints(self):
        v1_endpoints = self.schema['v1']

        for name, obj in v1_endpoints.items():
            for method, link in obj.items():
                # only test 'list' endpoints for now
                if method != 'list':
                    continue

                print("Testing endpoint %s (%s)" % (name, method))
                self.assertFalse(any(field.required for field in link.fields))
                response = getattr(self.client, link.action)(link.url)
                self.assertEqual(response.status_code, 200)
