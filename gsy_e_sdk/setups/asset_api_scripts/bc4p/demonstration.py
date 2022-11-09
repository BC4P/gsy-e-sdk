from gsy_e_sdk.setups.asset_api_scripts.bc4p.common.assets import Assets

# List of assets' names to be connected with the API
Load_PXL = ["main_P_L1", "main_P_L2", "main_P_L3"]
PV_PXL = ["PV_LS_105A_power", "PV_LS_105B_power", "PV_LS_105E_power"]
Load_PXL_Makerspace = ["PXL_makerspace_EmbroideryMachine","PXL_makerspace_LaserBig","PXL_makerspace_LaserSmall","PXL_makerspace_MillingMachine","PXL_makerspace_Miscellaneous","PXL_makerspace_PcLaserBig","PXL_makerspace_PcLaserSmall","PXL_makerspace_PcUltimakers","PXL_makerspace_PcVinylEmbroid","PXL_makerspace_PcbMilling","PXL_makerspace_Photostudio","PXL_makerspace_Press","PXL_makerspace_SheetPress","PXL_makerspace_Ultimaker3Left","PXL_makerspace_Ultimaker3Right","PXL_makerspace_UltimakerS5","PXL_makerspace_VacuumFormer","PXL_makerspace_VinylCutter"]
Load_FHAC = ["FH General Load"]
Combined_Berg = ["Berg Business","Berg House 1","Berg House 2"]

assets = Assets(load_names=Load_PXL+Load_PXL_Makerspace+Load_FHAC, pv_names=PV_PXL)
assets.run()