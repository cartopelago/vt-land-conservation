#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  name:     representativeness.py
#  purpose:  to evaluate representativeness of conservation lands,
#              tree blocks, and habitat connectors for 30x2030 and 50x2050 goals.
#
#  author:   Jeff Howarth
#  update:   06/29/2022
#  license:  Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# import tools from WBT module

import sys
sys.path.insert(1, '/Users/jhowarth/tools')
from WBT.whitebox_tools import WhiteboxTools

# declare a name for the tools

wbt = WhiteboxTools()

#
# Set the Whitebox working directory
# You will need to change this to your local path name
#
# # Full data
# # wbt.work_dir = "/Volumes/LaCie/GEOG0310/data/lForestBlocks"
#
# Test data

wbt.work_dir = "/Volumes/limuw/conservation/outputs/represent"

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Required datasets:
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

nc = "/Volumes/limuw/conservation/data/midd/iNatCom_12222021.tif"
town = "/Volumes/limuw/conservation/data/vtShapes/vtBoundaries/BoundaryTown_TWNBNDS/middlebury.shp"
blocks = "/Volumes/limuw/conservation/outputs/tree_blocks/142_C1_blocks_gt10_0nd.tif"
pro = "/Volumes/limuw/conservation/data/midd/proStackFlat_062621.tif"
connectors = "/Volumes/limuw/conservation/outputs/connectors/252_connector_classes.tif"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Compute acres of potential natural communities in town.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ----------------------------------------------------
# 1.1. Convert town boundary to binary raster.
# ----------------------------------------------------

# 1.1.1 Vector to raster

wbt.vector_polygons_to_raster(
    i = town,
    output = "111_town_raster.tif",
    field="FIPS6",
    nodata=True,
    cell_size=None,
    base=nc,
)

# 1.1.2. Reclassify values to 0 and 1.

wbt.reclass(
    i = "111_town_raster.tif",
    output = "112_town_raster_binary.tif",
    reclass_vals = "0;0;1;255",
    assign_mode=True
)

# 1.1.3 Make background noData value.

wbt.set_nodata_value(
    i = "112_town_raster_binary.tif",
    output = "113_town_raster_binary_0nd.tif",
    back_value=0.0
)

# ------------------------------------------------------------
# 1.2. Compute area of natural communities from soils in town.
# ------------------------------------------------------------

# 1.2.1. Make water community noData.

wbt.set_nodata_value(
    i = nc,
    output = "121_nc_0nd.tif",
    back_value=0.0
)

# 1.2.2. Isolate natural community locations in town.

wbt.multiply(
    input1 = "121_nc_0nd.tif",
    input2 = "113_town_raster_binary_0nd.tif",
    output = "122_nc_in_town.tif"
)

# 1.2.2. Compute area of natural communities in town.

wbt.raster_area(
    i = "122_nc_in_town.tif",
    output="123_nc_in_town_area.tif",
    out_text=False,
    units="map units",
    zero_back=False,
)

# 1.2.3. Convert to acres.

wbt.divide(
    input1 = "123_nc_in_town_area.tif",
    input2 = 4046.86,
    output = "124_nc_in_town_acres.tif"
)

# 1.2.4. Produce table of acres.

wbt.zonal_statistics(
    i = "124_nc_in_town_acres.tif",
    features = "122_nc_in_town.tif",
    output=None,
    stat="max",
    out_table="125_TABLE_nc_in_town_acres.html"
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Compute acres of natural communities in conserved land with natural cover.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 2.1.1 Isolate conservation with natural cover.

wbt.equal_to(
    input1 = pro,
    input2 = 2,
    output = "211_pro_nat_cover.tif"
)

# 2.1.2. Isolate conservation with natural cover in town.

wbt.multiply(
    input1 = "211_pro_nat_cover.tif",
    input2 = "113_town_raster_binary_0nd.tif",
    output = "212_pro_nat_in_town.tif"
)

# 2.1.3. Isolate natural community types in town protected lands.

wbt.multiply(
    input1 = "121_nc_0nd.tif",
    input2 = "212_pro_nat_in_town.tif",
    output = "213_nc_in_pro_nat.tif"
)

# 2.1.4. Compute area of natural communities in blocks.

wbt.raster_area(
    i = "213_nc_in_pro_nat.tif",
    output = "214_nc_in_pro_nat_area.tif",
    out_text=False,
    units="map units",
    zero_back=False,
)

# 2.1.5. Convert to acres.

wbt.divide(
    input1 = "214_nc_in_pro_nat_area.tif",
    input2 = 4046.86,
    output = "215_nc_in_pro_nat_acres.tif"
)

# 2.1.6. Produce table of acres.

wbt.zonal_statistics(
    i = "215_nc_in_pro_nat_acres.tif",
    features = "213_nc_in_pro_nat.tif",
    output=None,
    stat="max",
    out_table="216_TABLE_nc_in_town_pro_lands.html"
)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3. Compute acres of natural communities in town forest blocks.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 3.1.0. Convert no data to 0 in blocks.

wbt.convert_nodata_to_zero(
    i = blocks,
    output = "310_blocks_ndto0.tif"
)

# 3.1.1. Isolate forest blocks in town.

wbt.multiply(
    input1 = "310_blocks_ndto0.tif",
    input2 = "113_town_raster_binary_0nd.tif",
    output = "311_blocks_in_town.tif"
)

# 3.1.2. Combine forest blocks with protected lands in town.

wbt.Or(
    input1 = "311_blocks_in_town.tif",
    input2 = "211_pro_nat_cover.tif",
    output = "312_blocks_in_town_or_pro_lands.tif"
)

# 3.1.3. Isolate natural community types in forest blocks.

wbt.multiply(
    input1 = "121_nc_0nd.tif",
    input2 = "312_blocks_in_town_or_pro_lands.tif",
    output = "313_nc_in_blocks_in_town_or_pro_lands.tif"
)

# 3.1.4. Compute area of natural communities in blocks.

wbt.raster_area(
    i = "313_nc_in_blocks_in_town_or_pro_lands.tif",
    output = "314_nc_in_blocks_in_town_or_pro_lands_area.tif",
    out_text=False,
    units="map units",
    zero_back=False,
)

# 2.1.4. Convert to acres.

wbt.divide(
    input1 = "314_nc_in_blocks_in_town_or_pro_lands_area.tif",
    input2 = 4046.86,
    output = "315_nc_in_blocks_in_town_or_pro_lands_acres.tif"
)

# 2.1.4. Produce table of acres.

wbt.zonal_statistics(
    i = "315_nc_in_blocks_in_town_or_pro_lands_acres.tif",
    features = "313_nc_in_blocks_in_town_or_pro_lands.tif",
    output=None,
    stat="max",
    out_table="316_TABLE_nc_in_blocks_in_town_or_pro_lands.tif.html"
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 4. Compute acres of natural communities in town habitat connectors.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 4.1.0. Isolate non-island habitat connectors.

wbt.not_equal_to(
    input1 = connectors,
    input2 = 10,
    output = "410_connectors_not_islands.tif"
)

# 4.1.1. Convert no data to 0 in connectors.

wbt.convert_nodata_to_zero(
    i = "410_connectors_not_islands.tif",
    output = "411_connectors_not_islands_ndto0.tif"
)

# 4.1.2. Isolate non-island habitat connectors in town.

wbt.multiply(
    input1 = "411_connectors_not_islands_ndto0.tif",
    input2 = "113_town_raster_binary_0nd.tif",
    output = "412_connectors_not_islands_in_town.tif"
)

# 4.1.3. Combine connectors with pro lands and tree blocks.

wbt.Or(
    input1 = "312_blocks_in_town_or_pro_lands.tif",
    input2 = "412_connectors_not_islands_in_town.tif",
    output = "413_pro_or_block_or_connectors.tif"
)

# 4.1.4. Isolate natural community types in connectors.

wbt.multiply(
    input1 = "121_nc_0nd.tif",
    input2 = "413_pro_or_block_or_connectors.tif",
    output = "414_nc_in_pro_or_block_or_connectors.tif"
)

# 4.1.5. Compute area of natural communities in blocks.

wbt.raster_area(
    i = "414_nc_in_pro_or_block_or_connectors.tif",
    output = "415_nc_in_pro_or_block_or_connectors_area.tif",
    out_text=False,
    units="map units",
    zero_back=False,
)

# 4.1.6. Convert to acres.

wbt.divide(
    input1 = "415_nc_in_pro_or_block_or_connectors_area.tif",
    input2 = 4046.86,
    output = "416_nc_in_pro_or_block_or_connectors_acres.tif"
)

# 4.1.7. Produce table of acres.

wbt.zonal_statistics(
    i = "416_nc_in_pro_or_block_or_connectors_acres.tif",
    features = "414_nc_in_pro_or_block_or_connectors.tif",
    output=None,
    stat="max",
    out_table="417_TABLE_nc_in_pro_or_block_or_connectors_acres.html"
)
