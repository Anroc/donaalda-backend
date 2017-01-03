import logging


LOGGER = logging.getLogger(__name__)


class DeviceMapping(object):
    """
    Class for saving dicts of meta devices to scenarios and
    product to scenarios.
    """

    def __init__(self, endpoints=None, broker=None, products=None, bridges=None, original_to_merged=None):
        if endpoints is None:
            endpoints = dict()
        if broker is None:
            broker = dict()
        if products is None:
            products = dict()
        if bridges is None:
            bridges = dict()
        if original_to_merged is None:
            original_to_merged = dict()
        self.endpoints = endpoints
        self.broker = broker
        self.products = products
        self.bridges = bridges
        self.original_to_merged = original_to_merged

    def get_any_broker(self):
        return list(self.broker.keys())[0]

    def add_product(self, meta_device, product):
        scenarios = set()
        if product in self.products:
            scenarios = self.products[product]
        if meta_device.is_broker:
            if meta_device in self.broker:
                self.products[product] = self.broker[meta_device].union(scenarios)
            else:
                self.products[product] = self.bridges[meta_device].union(scenarios)
            return
        # else: broker is shifted to endpoints
        self.products[product] = self.endpoints[meta_device].union(scenarios)

    def add_products(self, meta_device, products):
        for product in products:
            self.add_product(meta_device, product)

    def shift_all_brokers_except(self, broker):
        other = self.__copy__()
        for b in self.broker.keys():
            if b is not broker:
                scenarios = other.broker.pop(b)
                other.bridges[b] = scenarios
        return other

    def __copy__(self):
        return DeviceMapping(
            self.endpoints.copy(),
            self.broker.copy(),
            self.products.copy(),
            self.bridges.copy(),
            self.original_to_merged.copy()
        )

    def intersect_products(self, products):
        tmp = dict()
        for product in products:
            tmp[product] = self.products[product]
        self.products = tmp

    def originals_from_merged(self, merged_device):
        return {key for key in self.original_to_merged if merged_device is self.original_to_merged[key]}

    def merge_scenario(self, scenario):
        # TODO: this seems like it could be simplified even further but my main
        # conern here is to encapsulate these two method calls into an instance
        # method.

        # merge meta broker
        self.broker = _merge_meta_device(
                {scenario.meta_broker},
                self.broker,
                scenario,
                self.original_to_merged
        )

        # merge meta endpoints
        self.endpoints = _merge_meta_device(
                set(scenario.meta_endpoints.all()),
                self.endpoints,
                scenario,
                self.original_to_merged
        )


def _merge_meta_device(meta_devices, meta_device_mapping, scenario, original_to_merged_mapping):
    """
    Merges a given set of meta_devices into a present_set of thous.
    This method also checks if the current features of the meta devices can be already satisfied by
    an element in the present set.

    :param meta_devices:
        the meta_devices that should be added in the set of present devices

        Note: The input meta devices are not going to be merged among themselves.
        Because they come directly from a single scenario which is assumed to have no unmerged meta devices.
    :param meta_device_mapping:
        a dictionary of either meta broker or meta endpoints to scenarios.
        See the class DeviceMapping for more information.
    :param scenario
        the scenario of the meta_devices that should be added.
    :param original_to_merged_mapping
        dict of mappings from original meta devices to merged ones.
    :return:
        device_mapping: the merge dict of meta devices to scenario
        original_to_merged_mapping: a dict of meta devices and their merged reference
    """
    device_mapping = meta_device_mapping.copy()
    merged_endpoints = set(device_mapping.keys()).copy()

    if not merged_endpoints:
        me = meta_devices.pop()
        merged_endpoints.add(me)
        device_mapping[me] = {scenario}
        original_to_merged_mapping[me] = me
    tmp_add_entries = dict()
    tmp_remove_keys = set()

    # check if the given meta endpoint has features that are already satisfied by other meta endpoints
    for cme in meta_devices:
        # matching on pk
        features_cme = set(cme.implementation_requires.values_list('pk', flat=True))
        for me in merged_endpoints:
            features_me = set(me.implementation_requires.values_list('pk', flat=True))
            if cme in tmp_add_entries:
                LOGGER.warning("Can't current meta endpoint has more than one possible merge option.")
                if me in tmp_remove_keys:
                    tmp_remove_keys.remove(me)
                tmp_add_entries[cme] = None
                continue
            elif not features_cme.issubset(features_me):
                device_mapping[cme] = {scenario}
                original_to_merged_mapping[cme] = cme
                continue
            elif features_me.issubset(features_cme):
                tmp_remove_keys.add(me)
                tmp_add_entries[cme] = device_mapping[me].union({scenario})
            original_to_merged_mapping[cme] = me
            for key in original_to_merged_mapping:
                if original_to_merged_mapping[key] is me:
                    original_to_merged_mapping[key] = cme

    for tmp_remove_key in tmp_remove_keys:
        del device_mapping[tmp_remove_key]
    # add the meta_endpoints to the set of meta endpoints
    device_mapping.update(
        {key: tmp_add_entries[key] for key in tmp_add_entries if tmp_add_entries[key] is not None}
    )
    return device_mapping
