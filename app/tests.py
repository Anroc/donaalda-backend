# -*- coding: utf-8 -*-

import unittest

import openapi
from django.test import TestCase
from rest_framework.schemas import SchemaGenerator

from .models import Provider, Scenario, Category, ScenarioCategoryRating


class IgnoreFilterFieldsSchemaGenerator(SchemaGenerator):
    def get_filter_fields(*args, **kwargs):
        return []


class SchemaTest(TestCase):
    def test_swagger_endpoints(self):
        # get the static swagger schema
        swagger = openapi.load(open("app/static/swagger.json"))

        swagger.validate()

        for uri, path in swagger.paths.items():
            # only test the post'able swagger endpoints
            if 'post' not in path:
                continue

            operation = path['post']

            if 'swagger' not in operation['tags']:
                continue

            body_params = list(filter(
                lambda param: param['in'] == 'body',
                operation['parameters']))

            self.assertEqual(len(body_params), 1)

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


class ScenarioCategoryRatingFixupTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        provider = Provider(public_name="testprovider")
        provider.save()

        # generate 4 test categories (accessible via selv.c0,... later)
        for cn in ["c1", "c2", "c3", "c4"]:
            setattr(cls, cn, Category(name=cn))
            getattr(cls, cn).save()

        # generate 4 test scenarios with 0,1,2 or all categories rated
        # respectively
        for sn in ["s0", "s1", "s2", "s4"]:
            setattr(cls, sn, Scenario(name=sn, provider=provider))
            getattr(cls, sn).save()

        # delete all ScenarioCategoryRatings that may have been created
        ScenarioCategoryRating.objects.all().delete()

        # create the ratings for the scenarios
        for n in [0, 1, 2, 4]:
            sn = "s%d" % n
            for k in range(1,n+1):
                cn = "c%d" % k
                ScenarioCategoryRating(scenario=getattr(cls, sn), category=getattr(cls, cn), rating = 3).save()

    def _assert_database_integrity(self, scenario):
        # save the scenario to trigger the fixup
        scenario.save()

        # get the lists of rated categories (as ids)
        scrs_manage = scenario.category_ratings
        rated_categories = scrs_manage.values_list('category', flat=True)

        # assert that our scenario has been rated in every category
        self.assertEqual(set(rated_categories),
                         set(Category.objects.values_list('pk', flat=True)))

        # assert that there is exactly one rating for every category
        self.assertEqual(len(rated_categories), Category.objects.count())

    def testNoRatings(self):
        self._assert_database_integrity(self.s1)

    def testOneRating(self):
        self._assert_database_integrity(self.s1)

    def testTwoRatings(self):
        self._assert_database_integrity(self.s2)

    def testAllRatings(self):
        self._assert_database_integrity(self.s4)
