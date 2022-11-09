from typing import List, Dict
from time import sleep

from gsy_e_sdk.setups.asset_api_scripts.bc4p.common.oracle import Oracle
from gsy_e_sdk.clients.redis_asset_client import RedisAssetClient

class Assets:
    def __init__(self, load_names = [], pv_names = [], storage_names = []):
        ORACLE_NAME = "oracle"
        # Frequency of bids/offers posting in a market slot - to leave as it is
        self.aggregator = Oracle(aggregator_name=ORACLE_NAME)
        asset_args = {"autoregister": True, "pubsub_thread": self.aggregator.pubsub}

        print()
        print("Registering assets ...")
        asset_uuid_mapping = {}
        asset_uuid_mapping = self.register_asset_list(asset_names=load_names + pv_names + storage_names, asset_params=asset_args, asset_uuid_map=asset_uuid_mapping)
        print()
        print("Summary of assets registered:")
        print()
        print(asset_uuid_mapping)
    
    def run(self):
        # loop to allow persistence
        while not self.aggregator.is_finished:
            sleep(0.5)
            
    def register_asset_list(self, asset_names: List, asset_params: Dict, asset_uuid_map: Dict) -> Dict:
        """Register the provided list of assets with the aggregator."""
        for asset_name in asset_names:
            print("Registered asset:", asset_name)
            asset_params["area_id"] = asset_name
            asset = RedisAssetClient(**asset_params)
            asset_uuid_map[asset.area_uuid] = asset.area_id
            asset.select_aggregator(self.aggregator.aggregator_uuid)
        return asset_uuid_map