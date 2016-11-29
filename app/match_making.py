from .models import *


def find_implementing_product(meta_device):
    """
    Finds implementing products to a given meta device.
    This device should either be a meta broker or an meta endpoint.

    :param
        meta_device: the meta device (either broker or endpoint)
    :return:
        set of all products that could implement the given meta broker
    """
    if type(meta_device) is MetaBroker:
        return __find_matching_products(meta_device, True)
    else:
        return __find_matching_products(meta_device, False)


def __find_matching_products(meta_device, leader=True):
    """
    Find all matching products to a given meta_device.

    :param
        meta_device: the meta device that should be implemented
    :param
        leader: if the given meta device is a meta broker
    :return:
        set of all matching products that have at least one protocol matching
        the defined behavior (e.g. borker -> least one leader protocol;
        endpoint -> at least one follower protocol.)
    """
    products = get_products()
    meta_feature = set(meta_device.implementation_requires)
    matching_products = set()
    for product in products:
        if meta_feature.issubset(set(product.features)):
            for protocol in product.protocol:
                if protocol.is_leader == leader:
                    matching_products.add(product)
    return matching_products


def find_matching_product_sets(broker, *endpoints, max_deph=3):
    """
    Assembles to the given broker and endpoints valid product sets that allows
    the broker to communicate with all endpoints.

    :param
        broker: the master broker in this product set configuration
    :param
        endpoints: varargs of endpoints that should be slaves of the broker
    :param
        max_deph: the number of maximal number bridges that should be included in
        the search set.
    :return:
        A set of product sets that are a valid in that kind that the broker
        can communicate with each endpoint (directly or over bridges)
        Or 'none' if no matching product set could be found
    :raises:
        ConfigurationException if the given parameter were in some kind invalid
    """
    broker_protcols = __get_protocols(broker, True)
    return_set = set()
    bridges = get_bridges().difference(broker)
    for endpoint in endpoints:
        protocols = __get_protocols(endpoint, False)

        # if endpoint is direct compatible to broker add to tuple and continue
        if __direct_compatible(broker_protcols, protocols):
            __add_to_set(return_set, (endpoint, ))
            continue

        # if not then check first level broker
        for bridge in bridges:
            if __direct_compatible(__get_protocols(bridge, True), protocols):
                if __direct_compatible(broker_protcols, __get_protocols(bridge, False)):
                    __add_to_set(return_set, (endpoint, bridge, ))
                    continue


def __find_communication_partner(endpoint, target, path=set(), max_deph=5, bridges_visited=set()):
    if max_deph <= 0:
        raise Exception("max_deph exeeded")

    # define methods for follower/leader protocols
    endpoint_protocols = __get_protocols(endpoint, False)
    bridges = get_bridges().difference(endpoint).difference(bridges_visited).union(set(target))

    if len(bridges) == 0:
        return set()

    path.add(endpoint)
    paths = set()
    for bridge in bridges:
        if __direct_compatible(__get_protocols(bridge, True), endpoint_protocols):
            if bridge is target:
                paths.add(path.add(target))
            else:
                next_path = __find_communication_partner(bridge, target, path, max_deph - 1, bridges)
                if len(next_path) != 0:
                    paths.union(next_path)
    return paths




def __add_to_set(_set, _tuple):
    if _set.__sizeof__() == 0:
        return set(_tuple)
    return_set = set()
    for elem in set:
        return_set.add(elem + _tuple)
    return return_set


def __direct_compatible(broker_protocols, endpoint_protocols):
    # check if endpoint can talk directly with broker
    for protocol in endpoint_protocols:
        for broker_protocol in broker_protocols:
            if protocol.name is broker_protocol.name:
                return True
    return False



def __get_protocols(product, leader):
    return next(protocol for protocol in product.protocol if protocol.is_leader == leader)


def get_bridges():
    """
    Gets all bridges in the product query set.

    :return:
        set of all bridges in the product query set.
    """
    products = get_products()
    return_set = set()
    for product in products:
        leader, follower = False
        protocols = product.protocol
        for protocol in products:
            if protocol.is_leader:
                leader = True
            else:
                follower = True
        if leader and follower:
            return_set.add(product)
    return return_set



def get_products():
    return Product.objects.all()
