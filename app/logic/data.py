from .cache import cached
from ..models import Product


BRIDGES_ID_HASH = hash('matching.bridges.cache')
PRODUCT_ID_HASH = hash('matching.product.cache')


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
            if len(__get_protocols(product, meta_device.is_broker)) != 0:
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
def __get_protocols(product, leader):
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
        if len(__get_protocols(product, True)) > 0 and len(__get_protocols(product, False)) > 0:
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


def __get_broker_of_products(product_set):
    return_set = set()
    for product in product_set:
        if len(__get_protocols(product, True)) > 0:
            return_set.add(product)

    return return_set
