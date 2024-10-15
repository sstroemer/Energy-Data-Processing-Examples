import atlite
import matplotlib.pyplot as plt
import geopandas as gpd
import nuts_finder


# NOTE: CRS3035 is in meters
# This code only supports this CRS.
CRS = 3035
CORINE = "U2018_CLC2018_V2020_20u1.tif"  # taken from Copernicus
NATURA = "natura.tiff"  # taken from the PyPSA-Eur bundle

# Configuration for the technologies.
config = {
    "solar": {
        "capacity_per_sqkm": 5.1,
        "corine_include": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 26, 31, 32],
        "corine_exclude": None,
        "corine_distance_to_exclude": None,
        "natura": True,
    },
    "onwind": {
        "capacity_per_sqkm": 3.0,
        "corine_include": [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32],
        "corine_exclude": [1, 2, 3, 4, 5, 6],
        "corine_distance_to_exclude": 1000,
        "natura": True,
    },
}

# ======================================================================================================================

# Prepare NUTS regions for Austria.
nf_shapes = nuts_finder.NutsFinder(year=2024).shapes
gdf_nuts = gpd.GeoDataFrame.from_features(nf_shapes, crs=nf_shapes["crs"]["properties"]["name"])
gdf_nuts = gdf_nuts.set_index("NUTS_ID")
gdf_at_nuts3 = gdf_nuts.loc[(gdf_nuts.CNTR_CODE == "AT") & (gdf_nuts.LEVL_CODE == 3)].copy()

# Calculate capacity for each technology and area.
for tech, attr in config.items():
    excluder = atlite.gis.ExclusionContainer()
    excluder.add_raster(CORINE, codes=attr["corine_include"], crs=CRS, invert=True)
    if attr.get("corine_exclude", None):
        excluder.add_raster(CORINE, codes=attr["corine_exclude"], crs=CRS, buffer=attr["corine_distance_to_exclude"])
    if attr.get("natura", False):
        excluder.add_raster(NATURA, crs=CRS, allow_no_overlap=True, nodata=0)

    # TODO: why do we not need to do `.to_crs(excluder.crs)`?

    # Plot available land, and total percentage.
    fig, ax = plt.subplots()
    excluder.plot_shape_availability(gdf_at_nuts3.geometry)
    plt.savefig(f"{tech}.png")

    # Calculate the area of each NUTS3 region and the area of eligible land.
    gdf_at_nuts3["area_sqkm"] = gdf_at_nuts3.geometry.to_crs(excluder.crs).area / 1e6
    gdf_at_nuts3["area_eligible_sqkm"] = 0.0
    for nuts_id in gdf_at_nuts3.index:
        masked, transform = excluder.compute_shape_availability(gdf_at_nuts3.loc[[nuts_id]].geometry)
        gdf_at_nuts3.loc[nuts_id, "area_eligible_sqkm"] = masked.sum() * excluder.res**2 / 1e6

    # Calculate the technologies capacity for each NUTS3 region.
    gdf_at_nuts3[f"{tech}_capacity_mw"] = gdf_at_nuts3["area_eligible_sqkm"] * attr["capacity_per_sqkm"]

gdf_at_nuts3.to_excel("nuts_stats.xlsx")
