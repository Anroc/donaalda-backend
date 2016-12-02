"""
1.  Call find_implementing_product for each meta device in the scenrio
2.  for each Broker -> Endpoint combination find pahts with: find_communication_partner(endpoint, broker)
3.  Merge the result: for each broker in look if it can reach all endpoints.
    If it do so: create a product set of the current configuration
4.  Apply U_pref on to all product sets for each broker to find the current best solution for the current broker-product-set
5.  Apply U_pref on all product sets for each different broker to find the over all best solution for the current scenrio
"""

from .models import *

def implement_scenario(scenario):
    meta_devices = scenario.meta_devices



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
    Find all implementing products to a given meta_device.

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


def find_communication_partner(endpoint, target, path=set(), max_deph=5, bridges_visited=set()):
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
                next_path = find_communication_partner(bridge, target, path, max_deph - 1, bridges)
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
