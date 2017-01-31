import logging


LOGGER = logging.getLogger(__name__)


class DeviceMapping(object):
    """
    Class for saving dicts of meta devices to scenarios and
    product to scenarios.
    """

    def __init__(
        self, suggested_scenario, endpoints=None, broker=None, products=None, bridges=None, original_to_merged=None
    ):
        self.suggested_scenario = suggested_scenario
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
            self.suggested_scenario,
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
        merged_endpoint = meta_devices.pop()
        merged_endpoints.add(merged_endpoint)
        device_mapping[merged_endpoint] = {scenario}
        original_to_merged_mapping[merged_endpoint] = merged_endpoint
    tmp_add_entries = dict()
    tmp_remove_keys = set()

    # check if the given meta endpoint has features that are already satisfied by other meta endpoints
    for new_me in meta_devices:
        # matching on pk
        new_md_features = set(new_me.implementation_requires.values_list('pk', flat=True))
        for merged_endpoint in merged_endpoints:
            merged_endpoint_features = set(merged_endpoint.implementation_requires.values_list('pk', flat=True))

            # check if the current already merged endpoint is a subset of the current meta device
            if merged_endpoint_features.issubset(new_md_features):
                # check if current element is already in the merged list
                if new_me in tmp_add_entries:
                    LOGGER.warning("Can't current meta device has more than one possible merge option.")
                    if merged_endpoint in tmp_remove_keys:
                        tmp_remove_keys.remove(merged_endpoint)
                    tmp_add_entries[new_me] = None
                    # remove updated mapping by calling the same function with inverted values
                    update_original_to_merged_mapping(original_to_merged_mapping, new_me, merged_endpoint)
                else:
                    tmp_remove_keys.add(merged_endpoint)
                    tmp_add_entries[new_me] = device_mapping[merged_endpoint].union({scenario})
                    # update mappings with ne endpoint that was merged
                    update_original_to_merged_mapping(original_to_merged_mapping, merged_endpoint, new_me)

        # if the new meta endpoint could not be used as a new merge partner
        if new_me not in tmp_add_entries:
            if new_me in device_mapping:
                # meta device may be already in the set if included by other scenario
                # can't be twice in tmp_add_entries since we only inspecting one scenario at time
                tmp_add_entries[new_me] = device_mapping[new_me].union({scenario})
            else:
                tmp_add_entries[new_me] = {scenario}
            original_to_merged_mapping[new_me] = new_me

    # remove all merged keys
    for tmp_remove_key in tmp_remove_keys:
        del device_mapping[tmp_remove_key]

    # add the meta_endpoints to the set of meta endpoints
    device_mapping.update(
        {key: tmp_add_entries[key] for key in tmp_add_entries if tmp_add_entries[key] is not None}
    )
    return device_mapping


def update_original_to_merged_mapping(mapping, replacee, replacer):
    if replacer in mapping:
        replacee = replacer
        replacer = mapping[replacer]
    else:
        mapping[replacer] = replacer
    mapping[replacee] = replacer
    for key in mapping:
        if mapping[key] is replacee:
            mapping[key] = replacer
