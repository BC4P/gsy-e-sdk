from gsy_e_sdk.setups.asset_api_scripts.bc4p.common.assets import Assets

# List of assets' names to be connected with the API
LOAD_NAMES = ["main_P_L1", "main_P_L2", "main_P_L3"]
PV_NAMES = ["PV_LS_105A_power", "PV_LS_105B_power", "PV_LS_105E_power"]

assets = Assets(load_names=LOAD_NAMES, pv_names=PV_NAMES)
assets.run()