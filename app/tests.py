# -*- coding: utf-8 -*-

import unittest

from django.test import Client
from django.contrib.auth.models import User
from django.contrib import auth
from rest_framework.schemas import SchemaGenerator

from .models import Category, Product


class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        # enforce_csrf_checks=True

    def test_details(self):

        response = self.client.get('/app/')
        self.assertEqual(response.status_code, 200)
        print(response)
        #        response = self.client.get('/app/login')

        # register
        for i in range(1, 20):
            un = 'un' + str(i)
            fn = 'fn' + str(i)
            ln = 'ln' + str(i)
            email = 'email' + str(i)
            pw = 'pw' + str(i)
            self.assertFalse(User.objects.filter(username=un).exists())  # should not be registered yet
            response = self.client.post('/app/register',
                                        {'username': un, 'firstname': fn, 'lastname': ln, 'email': email,
                                         'password': pw})  # send register request
            self.assertTrue(User.objects.filter(username=un).exists())  # should be registered now

        for i in range(1, 20):
            un = 'un' + str(i)
            pw = 'pw' + str(i)
            print(i)
            user = auth.get_user(self.client)
            assert not user.is_authenticated()  # should not be logged in yet
            # login
            response = self.client.post('/app/login', {'username': un, 'password': pw})  # send login request
            user = auth.get_user(self.client)
            assert user.is_authenticated()  # should be logged in now
            # logout
            response = self.client.post('/app/logout', {'username': un, 'password': pw})  # send logout request
            user = auth.get_user(self.client)
            assert not user.is_authenticated()  # should not be logged in anymore


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
