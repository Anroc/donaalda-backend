# -*- coding: utf-8 -*-

from django.test import TestCase

from .models import Provider, Scenario, Category, ScenarioCategoryRating


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
