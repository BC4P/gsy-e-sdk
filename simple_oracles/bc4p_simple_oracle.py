"""
Template file for a trading strategy through the gsy-e-sdk api client using Redis.
"""

from time import sleep
from typing import List, Dict
from gsy_e_sdk.redis_aggregator import RedisAggregator
from gsy_e_sdk.clients.redis_asset_client import RedisAssetClient


class Oracle(RedisAggregator):
    """Class that defines the behaviour of an "oracle" aggregator."""

    def __init__(self,TICK_DISPATCH_FREQUENCY_PERCENT = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_finished = False
        self.asset_strategy = {}
        self.TICK_DISPATCH_FREQUENCY_PERCENT = TICK_DISPATCH_FREQUENCY_PERCENT
        

    def on_market_slot(self, market_info):
        """Place a bid or an offer whenever a new market is created."""
        if self.is_finished is True:
            return
        self.build_strategies(market_info)
        self.post_bid_offer()

    def on_tick(self, tick_info):
        """Place a bid or an offer each 10% of the market slot progression."""
        rate_index = int(float(tick_info["slot_completion"].strip("%")) /
                          self.TICK_DISPATCH_FREQUENCY_PERCENT)
        self.post_bid_offer(rate_index)

    def build_strategies(self, market_info):
        """
        Assign a simple strategy to each asset in the form of an array of length 10,
        ranging between Feed-in Tariff and Market Maker rates.
        """
        fit_rate = market_info["feed_in_tariff_rate"]
        market_maker_rate = market_info["market_maker_rate"]
        med_price = (market_maker_rate - fit_rate) / 2 + fit_rate

        for area_uuid, area_dict in self.latest_grid_tree_flat.items():
            if "asset_info" not in area_dict or area_dict["asset_info"] is None:
                continue
            self.asset_strategy[area_uuid] = {}
            self.asset_strategy[area_uuid]["asset_name"] = area_dict["area_name"]
            self.asset_strategy[area_uuid][
                "fee_to_market_maker"
            ] = self.calculate_grid_fee(
                area_uuid,
                self.get_uuid_from_area_name("Market Maker"),
                "current_market_fee",
            )

            # Consumption strategy
            if "energy_requirement_kWh" in area_dict["asset_info"]:
                load_strategy = []
                for tick in range(0,  self.TICK_DISPATCH_FREQUENCY_PERCENT):
                    if tick <  self.TICK_DISPATCH_FREQUENCY_PERCENT - 2:
                        buy_rate = (fit_rate -
                                    self.asset_strategy[area_uuid]["fee_to_market_maker"] +
                                    (market_maker_rate +
                                     2 * self.asset_strategy[area_uuid]["fee_to_market_maker"] -
                                     fit_rate) * (tick /  self.TICK_DISPATCH_FREQUENCY_PERCENT)
                                    )
                        load_strategy.append(buy_rate)
                    else:
                        buy_rate = (market_maker_rate +
                                    self.asset_strategy[area_uuid]["fee_to_market_maker"])
                        load_strategy.append(buy_rate)
                self.asset_strategy[area_uuid]["buy_rates"] = load_strategy

            # Generation strategy
            if "available_energy_kWh" in area_dict["asset_info"]:
                gen_strategy = []
                for tick in range(0,  self.TICK_DISPATCH_FREQUENCY_PERCENT):
                    if tick <  self.TICK_DISPATCH_FREQUENCY_PERCENT - 2:
                        sell_rate = (market_maker_rate +
                                     self.asset_strategy[area_uuid]["fee_to_market_maker"] -
                                     (market_maker_rate +
                                      2 * self.asset_strategy[area_uuid]["fee_to_market_maker"] -
                                      fit_rate) * (tick /  self.TICK_DISPATCH_FREQUENCY_PERCENT)
                                     )
                        gen_strategy.append(max(0, sell_rate))
                    else:
                        sell_rate = fit_rate - (
                            self.asset_strategy[area_uuid]["fee_to_market_maker"])
                        gen_strategy.append(max(0, sell_rate))
                self.asset_strategy[area_uuid]["sell_rates"] = gen_strategy

            # Storage strategy
            if "used_storage" in area_dict["asset_info"]:
                batt_buy_strategy = []
                batt_sell_strategy = []
                for tick in range(0,  self.TICK_DISPATCH_FREQUENCY_PERCENT):
                    buy_rate = (fit_rate -
                                self.asset_strategy[area_uuid]["fee_to_market_maker"] +
                                (med_price -
                                 (fit_rate -
                                  self.asset_strategy[area_uuid]["fee_to_market_maker"]
                                  )
                                 ) * (tick /  self.TICK_DISPATCH_FREQUENCY_PERCENT)
                                )
                    batt_buy_strategy.append(buy_rate)
                    sell_rate = (market_maker_rate +
                                 self.asset_strategy[area_uuid]["fee_to_market_maker"] -
                                 (market_maker_rate +
                                  self.asset_strategy[area_uuid]["fee_to_market_maker"] -
                                  med_price) * (tick /  self.TICK_DISPATCH_FREQUENCY_PERCENT)
                                 )
                    batt_sell_strategy.append(sell_rate)
                self.asset_strategy[area_uuid]["buy_rates"] = batt_buy_strategy
                self.asset_strategy[area_uuid]["sell_rates"] = batt_sell_strategy

    def post_bid_offer(self, rate_index=0):
        """Post a bid or an offer to the exchange."""
        for area_uuid, area_dict in self.latest_grid_tree_flat.items():
            asset_info = area_dict.get("asset_info")
            if not asset_info:
                continue

            # Consumption assets
            required_energy = asset_info.get("energy_requirement_kWh")
            if required_energy:
                rate = self.asset_strategy[area_uuid]["buy_rates"][rate_index]
                self.add_to_batch_commands.bid_energy_rate(
                    asset_uuid=area_uuid, rate=rate, energy=required_energy
                )

            # Generation assets
            available_energy = asset_info.get("available_energy_kWh")
            if available_energy:
                rate = self.asset_strategy[area_uuid]["sell_rates"][rate_index]
                self.add_to_batch_commands.offer_energy_rate(
                    asset_uuid=area_uuid, rate=rate, energy=available_energy
                )

            # Storage assets
            buy_energy = asset_info.get("energy_to_buy")
            if buy_energy:
                buy_rate = self.asset_strategy[area_uuid]["buy_rates"][rate_index]
                self.add_to_batch_commands.bid_energy_rate(
                    asset_uuid=area_uuid, rate=buy_rate, energy=buy_energy
                )

            sell_energy = asset_info.get("energy_to_sell")
            if sell_energy:
                sell_rate = self.asset_strategy[area_uuid]["sell_rates"][rate_index]
                self.add_to_batch_commands.offer_energy_rate(
                    asset_uuid=area_uuid, rate=sell_rate, energy=sell_energy
                )

            self.execute_batch_commands()

    def on_event_or_response(self, message):
        pass

    def on_finish(self, finish_info):
        self.is_finished = True


