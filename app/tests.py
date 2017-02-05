# -*- coding: utf-8 -*-

from django.test import TestCase, tag
from django.core.cache import cache

from .models import (
        Provider,
        Scenario,
        Category,
        ScenarioCategoryRating,
        Product,
        ProductType,
        Protocol,
)

from .logic.implementing import __find_communication_partner


# because of pythons underscore name wrangling, we cannot use this from within a
# class. I guess the lesson to be learned here is that you should use at most
# one underscore (preferably none at all) to mark methods as private
fcp = __find_communication_partner


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


@tag('matching')
class FindCommunicationPartnerTest(TestCase):
    def setUp(self):
        # we have to clear the cache bifore running each test because some tests
        # modify the data set which is not considered by the caching thing since
        # it should change so seldom.
        cache.clear()

    @classmethod
    def setUpTestData(cls):
        # create some protocols
        # The structure of the test data looks like this
        # target <- protocol0 - product0 <- protocol1 <- ... - productn <- protocl n+1 - nothing
        for i in range(5):
            protocol_name = "protocol{0}".format(i)
            setattr(cls, protocol_name, Protocol(name=protocol_name))
            getattr(cls, protocol_name).save()

        # create a dummy product type and provider so that postgresql won't
        # complain about constraings
        cls.producttype = ProductType(type_name="test_producttype")
        cls.producttype.save()
        cls.provider = Provider(name="test_provider")
        cls.provider.save()

        # create the target product that all other products connect to
        cls.target = Product(
                name="target",
                provider=cls.provider,
                product_type=cls.producttype,
                renovation_required=False)
        cls.target.save()
        cls.target.leader_protocol.add(cls.protocol0)

        for i in range(4):
            product_name = "product{0}".format(i)
            prod = Product(
                    name=product_name,
                    provider=cls.provider,
                    product_type=cls.producttype,
                    renovation_required=False)
            prod.save()
            prod.follower_protocol.add(getattr(cls, "protocol{0}".format(i)))
            prod.leader_protocol.add(getattr(cls, "protocol{0}".format(i+1)))
            setattr(cls, product_name, prod)

    @staticmethod
    def _prepare_results(endpoint, target, renovation, **kwargs):
        """Runs __find_communication_partner and maps the results to a frozenset
        of frozensets since the order does not matter.
        """
        # fcp is an alias to __find_communication_partner
        ret = fcp(endpoint, target, renovation, **kwargs)
        return frozenset(map(frozenset, ret))

    @staticmethod
    def _expect(*results):
        """Returns a set containing a frozenset made from each argument. This
        exists because writing {frozenset([asdf, jkl]), frozenset([asdf])} a lot
        is annoying and writing _expect({asdf, jkl}, {asdf}) is much easier to
        read.
        """
        return {
            frozenset(result)
            for result in results
        }

    def testSameProduct(self):
        res = self._prepare_results(self.target, self.target, True)
        self.assertEqual(res, self._expect({self.target}))

    def testDirectConnection(self):
        res = self._prepare_results(self.product0, self.target, True)
        self.assertEqual(res, self._expect({self.target, self.product0}))

    def testOneBridge(self):
        res = self._prepare_results(self.product1, self.target, True)
        self.assertEqual(
                res,
                self._expect({
                    self.target,
                    self.product0,
                    self.product1,
                }))

    def testOneBridgeNotPossibleBecauseRenovation(self):
        self.product0.renovation_required = True
        self.product0.save()
        res = self._prepare_results(self.product1, self.target, False)
        self.assertEqual(res, set())

    def testTwoOneBridgePaths(self):
        self.product0_alternative = Product(
                name="product0_alternative",
                provider=self.provider,
                product_type=self.producttype,
                renovation_required=False)
        self.product0_alternative.save()
        self.product0_alternative.follower_protocol.add(self.protocol0)
        self.product0_alternative.leader_protocol.add(self.protocol1)
        res = self._prepare_results(self.product1, self.target, True)
        self.assertEqual(
                res,
                self._expect({
                    self.target,
                    self.product0,
                    self.product1,
                }, {
                    self.target,
                    self.product0_alternative,
                    self.product1,
                }))

    def testTwoPathsOneDirect(self):
        self.product1.follower_protocol.add(self.protocol0)
        res = self._prepare_results(self.product1, self.target, True)
        self.assertEqual(
                res,
                self._expect({
                    self.target,
                    self.product1,
                }, {
                    self.target,
                    self.product0,
                    self.product1,
                }))

    def testTwoBridges(self):
        res = self._prepare_results(self.product2, self.target, True)
        self.assertEqual(
                res,
                self._expect({
                    self.target,
                    self.product0,
                    self.product1,
                    self.product2,
                }))

    def testNoPath(self):
        self.product0.follower_protocol = []
        res = self._prepare_results(self.product0, self.target, True)
        self.assertEqual(res, set())

    def testPathLongerThanAllowed(self):
        res = self._prepare_results(self.product3, self.target, True, max_depth=3)
        self.assertEqual(res, set())
