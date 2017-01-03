from django.core.cache import cache

from ..models import Product


# 1h
EXPIRATION_TIME = 60 * 60
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
    input_hash = hash((frozenset(broker_protocols), frozenset(endpoint_protocols)))
    if cache.get(input_hash) is not None:
        return cache.get(input_hash)

    # check if endpoint can talk directly with broker
    for protocol in endpoint_protocols:
        for broker_protocol in broker_protocols:
            if protocol.name == broker_protocol.name:
                cache.set(input_hash, True, EXPIRATION_TIME)
                return True
    cache.set(input_hash, False)
    return False


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
    input_hash = hash((product, leader))
    if cache.get(input_hash) is not None:
        return cache.get(input_hash)

    if leader:
        cache.set(input_hash, set(product.leader_protocol.all()), EXPIRATION_TIME)
    else:
        cache.set(input_hash, set(product.follower_protocol.all()), EXPIRATION_TIME)
    return cache.get(input_hash)


def __get_bridges(renovation_allowed=True):
    """
    Gets all bridges in the product query set.

    :return:
        set of all bridges in the product query set.
    """
    if cache.get(BRIDGES_ID_HASH) is not None:
        return cache.get(BRIDGES_ID_HASH)

    products = __get_products(renovation_allowed)
    return_set = set()
    for product in products:
        if len(__get_protocols(product, True)) > 0 and len(__get_protocols(product, False)) > 0:
            return_set.add(product)

    cache.set(BRIDGES_ID_HASH, return_set.copy(), EXPIRATION_TIME)
    return return_set


def __get_products(renovation_allowed=True):
    """
    Returns all the product as a set.

    :return:
        A set of all known products.
    """
    input_hash = hash((PRODUCT_ID_HASH, renovation_allowed))
    if renovation_allowed:
        return cache.get_or_set(
            input_hash,
            set(Product.objects.prefetch_related(
                'product_type',
                'leader_protocol',
                'follower_protocol',
                'features'
            ).all()),
            EXPIRATION_TIME
        )
    return cache.get_or_set(
        input_hash,
        set(Product.objects.prefetch_related(
                'product_type',
                'leader_protocol',
                'follower_protocol',
                'features'
            ).filter(renovation_required=False)),
        EXPIRATION_TIME)


def __get_broker_of_products(product_set):
    return_set = set()
    for product in product_set:
        if len(__get_protocols(product, True)) > 0:
            return_set.add(product)

    return return_set
