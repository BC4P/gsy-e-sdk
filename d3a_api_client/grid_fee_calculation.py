import logging
from copy import copy

from d3a_interface.utils import key_in_dict_and_not_none


class GridFeeCalculation:

    def __init__(self):
        self.latest_grid_stats_tree = {}
        self.paths_to_root_mapping = {}
        self.market_name_grid_fee_mapping = {"last_market_fee": {},
                                             "next_market_fee": {}}

    def _handle_grid_stats(self, message):
        for device_event in message["content"]:
            if device_event["event"] == "grid stats":
                self.latest_grid_stats_tree = device_event["grid_stats_tree"]
                message["content"].remove(device_event)
        self._populate_grid_fee_mappings()

    def _populate_grid_fee_mappings(self):
        for fee_type in ["last_market_fee", "next_market_fee"]:
            self._get_grid_fee_area_mapping_from_dict(self.latest_grid_stats_tree, fee_type)

        self._get_all_paths_in_grid_stats_dict(self.latest_grid_stats_tree, [])

    def _get_grid_fee_area_mapping_from_dict(self, indict, fee_type):
        for child_name, child_stats in indict.items():
            if "children" in child_stats and fee_type in child_stats:
                self.market_name_grid_fee_mapping[fee_type][child_name] = child_stats[fee_type]
                self._get_grid_fee_area_mapping_from_dict(child_stats["children"], fee_type)

    def _get_all_paths_in_grid_stats_dict(self, indict, parent_path):
        for child_name, child_stats in indict.items():
            sub_path = parent_path + [child_name]
            self.paths_to_root_mapping[child_name] = parent_path
            if "children" in child_stats:
                self._get_all_paths_in_grid_stats_dict(child_stats["children"], sub_path)

    @staticmethod
    def _strip_away_intersection_from_list(in_list, intersection):
        out_list = copy(in_list)
        for inter in intersection:
            out_list.remove(inter)
        return out_list

    @staticmethod
    def _find_lowest_intersection_market(in_list, intersection):
        last_li = in_list[0]
        for li in in_list:
            if li not in intersection:
                return last_li
            last_li = li
        return last_li

    def calculate_grid_fee(self, start_market_or_device_name: str,
                           target_market_or_device_name: str = None, fee_type: str="next_market_fee"):
        """
        Calculates the grid fees along path between two assets or markets in the grid
        """
        if not self.latest_grid_stats_tree:
            logging.info("Grid fees can not be calculated because there were no grid_stats sent yet.")
            return None

        if target_market_or_device_name is None:
            if start_market_or_device_name not in self.market_name_grid_fee_mapping[fee_type]:
                return self.market_name_grid_fee_mapping[fee_type][
                    self.paths_to_root_mapping[start_market_or_device_name][-1]]
            else:
                return self.market_name_grid_fee_mapping[fee_type][start_market_or_device_name]

        path_start_market = self.paths_to_root_mapping[start_market_or_device_name]
        path_target_market = self.paths_to_root_mapping[target_market_or_device_name]

        intersection_markets = list(set(path_start_market).intersection(path_target_market))

        path_start_market_stripped = \
            self._strip_away_intersection_from_list(path_start_market, intersection_markets)
        path_target_market_stripped = \
            self._strip_away_intersection_from_list(path_target_market, intersection_markets)

        if path_start_market_stripped == [target_market_or_device_name]:
            # case when start_market child of target_market
            all_markets_along_path = path_start_market_stripped
        elif path_target_market_stripped == [start_market_or_device_name]:
            # case when target_market child of start_market
            all_markets_along_path = path_target_market_stripped
        else:
            lowest_intersection_market = \
                self._find_lowest_intersection_market(path_start_market, intersection_markets)

            all_markets_along_path = set([lowest_intersection_market] +
                                         path_start_market_stripped + path_target_market_stripped +
                                         [start_market_or_device_name] + [target_market_or_device_name])

        total_grid_fees = 0
        for ma in all_markets_along_path:
            if key_in_dict_and_not_none(self.market_name_grid_fee_mapping[fee_type], ma):
                total_grid_fees += self.market_name_grid_fee_mapping[fee_type][ma]

        return total_grid_fees
