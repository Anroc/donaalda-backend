import operator

from .cache import cached
from ..models import Product, Scenario
from ..constants import SHOPPING_BASKET_SCENARIO_ID


BRIDGES_ID_HASH = hash('matching.bridges.cache')
PRODUCT_ID_HASH = hash('matching.product.cache')


def __get_scenarios(scenario_ids, exclude=False):
    """
    Return a frozenset of prefetched scenarios with the given ids.

    :param scenario_ids:
        The set of scenario ids to filter for
    :param exclude:
        Whether to return scenarios whose ids are in the set (exclude=False)
        or scenarios that aren't (exclude=True)
    :return:
        A frozenset of scenarios.
    """
    queryset = Scenario.objects.prefetch_related(
            'meta_broker__implementation_requires',
            'meta_endpoints__implementation_requires')
    if exclude:
        return frozenset(queryset.exclude(pk__in=scenario_ids))
    return frozenset(queryset.filter(pk__in=scenario_ids))


def partition_scenarios(shopping_basket):
    """
    Partition the set of scenarios in the database into those that are in the
    given shopping basket and those which are not and might be suggested to te
    user.

    :param shopping_basket:
        The shopping basket part of the matching user input
    :return:
        A tuple consisting of
        0: a frozenset of scenarios that make up the given shopping basket, and
        1: the rest of the scenarios (as frozenset).
        The returned scenarios have been prefetched with everything that is
        relevant to the matching algorithm (meta devices and features of the
        meta devices)
    """
    shopping_basket_scenario_ids = set(map(
            operator.attrgetter(SHOPPING_BASKET_SCENARIO_ID),
            shopping_basket))

    shoping_basket_scenarios = __get_scenarios(shopping_basket_scenario_ids)
    suggestable_scenarios = __get_scenarios(shopping_basket_scenario_ids, True)

    return shoping_basket_scenarios, suggestable_scenarios


def __find_implementing_product(meta_device, renovation_allowed):
    """
    Find all implementing products to a given meta_device.
    This have to fit two criteria:
    1. the product must implement all features of the meta device
    2. the product must speak at least one protocol in the given mode

    :param
        meta_device: the meta device that should be implemented
    :return:
        set of all matching products that have at least one protocol matching
        the defined behavior (e.g. broker -> least one leader protocol;
        endpoint -> at least one follower protocol.)
    """
    products = __get_products(renovation_allowed)
    meta_feature = set(meta_device.implementation_requires.all())
    matching_products = set()
    for product in products:
        if meta_feature.issubset(set(product.features.all())):
            if len(get_protocols(product, meta_device.is_broker)) != 0:
                matching_products.add(product)
    return matching_products


@cached(lambda bp, ep: hash((frozenset(bp), frozenset(ep))))
def __direct_compatible(broker_protocols, endpoint_protocols):
    """
    Checks if the given broker_protocols can communicate with the given endpoint_protocols.

    :param broker_protocols:
        protocols in leader mode
    :param endpoint_protocols:
        protocols in follower mode
    :return:
        if the given broker_protocols can communicate with the given endpoint_protocols
    """
    # check if endpoint can talk directly with broker
    for protocol in endpoint_protocols:
        for broker_protocol in broker_protocols:
            if protocol.name == broker_protocol.name:
                return True
    return False


@cached(lambda p, l: hash((p, l)))
def get_protocols(product, leader):
    """
    Returns all the protocols of the given product that matches the given mode.

    :param product:
        the product which speaks a set of protocols
    :param leader:
        if the protocols should be in leader (True) or in follower (False) mode
    :return:
        all spoken protocols by the product in the given mode.
    """
    if leader:
        return set(product.leader_protocol.all())
    else:
        return set(product.follower_protocol.all())


@cached(lambda r: hash((BRIDGES_ID_HASH, r)))
def __get_bridges(renovation_allowed=True):
    """
    Gets all bridges in the product query set.

    :return:
        set of all bridges in the product query set.
    """
    products = __get_products(renovation_allowed)
    return_set = set()
    for product in products:
        if len(get_protocols(product, True)) > 0 and len(get_protocols(product, False)) > 0:
            return_set.add(product)

    return return_set


@cached(lambda r: hash((PRODUCT_ID_HASH, r)))
def __get_products(renovation_allowed=True):
    """
    Returns all the product as a set.

    :return:
        A set of all known products.
    """
    if renovation_allowed:
        return set(Product.objects.prefetch_related(
                   'product_type',
                   'leader_protocol',
                   'follower_protocol',
                   'features').all())
    return set(Product.objects.prefetch_related(
               'product_type',
               'leader_protocol',
               'follower_protocol',
               'features').filter(renovation_required=False))


def get_broker_of_products(product_set):
    return_set = set()
    for product in product_set:
        if len(get_protocols(product, True)) > 0:
            return_set.add(product)

    return return_set
