from gsy_e_sdk.setups.asset_api_scripts.bc4p.common.assets import Assets

# List of assets' names to be connected with the API
LOAD_NAMES = ["FH Load"]
PV_NAMES = ["FH PV"]
STORAGE_NAMES = ["FH Storage"]

assets = Assets(load_names=LOAD_NAMES, pv_names=PV_NAMES, storage_names=STORAGE_NAMES)
assets.run()