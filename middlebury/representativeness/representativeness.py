#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  name:     treeHabitatBlocks.py
#  purpose:  to identify tree canopy habitat blocks for conservation planning
#
#  author:   Jeff Howarth
#  update:   06/24/2022
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
wbt.work_dir = "/Volumes/LaCie/midd_cp_2022/represent"

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Required datasets:
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

nc = "/Volumes/limuw/conservation/data/midd/iNatCom_12222021.tif"
town = "/Volumes/limuw/conservation/data/vtShapes/vtBoundaries/BoundaryTown_TWNBNDS/middlebury.shp"
blocks = "/Volumes/limuw/conservation/outputs/tree_blocks/142_C1_blocks_gt10_0nd.tif"
pro ="/Volumes/limuw/conservation/dataproStackFlat_062621.tif"

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
# 2. Compute acres of  natural communities in town forest blocks.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 2.1.1. Isolate forest blocks in town.

wbt.multiply(
    input1 = blocks,
    input2 = "113_town_raster_binary_0nd.tif",
    output = "211_blocks_in_town.tif"
)

# 2.1.2. Isolate natural community types in forest blocks.

wbt.multiply(
    input1 = "121_nc_0nd.tif",
    input2 = "211_blocks_in_town.tif",
    output = "212_nc_in_blocks.tif"
)

# 2.1.3. Compute area of natural communities in blocks.

wbt.raster_area(
    i = "212_nc_in_blocks.tif",
    output = "213_nc_in_blocks_area.tif",
    out_text=False,
    units="map units",
    zero_back=False,
)

# 2.1.4. Convert to acres.

wbt.divide(
    input1 = "213_nc_in_blocks_area.tif",
    input2 = 4046.86,
    output = "214_nc_in_blocks_acres.tif"
)

# 2.1.4. Produce table of acres.

wbt.zonal_statistics(
    i = "214_nc_in_blocks_acres.tif",
    features = "212_nc_in_blocks.tif",
    output=None,
    stat="max",
    out_table="215_TABLE_nc_in_town_blocks_acres.html"
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3. Compute acres of natural communities in conserved land with natural cover.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 3.1.1 Isolate conservation with natural cover.

wbt.reclass(
    i = pro,
    output = "311_pro_nat_cover.tif",
    reclass_vals = "0;0;0;1;1;2;0;3",
    assign_mode=True
)


# 3.1.2. Isolate conservation with natural cover in town.

wbt.multiply(
    input1 = "311_pro_nat_cover.tif",
    input2 = "113_town_raster_binary_0nd.tif",
    output = "312_pro_nat_in_town.tif"
)

# 3.1.3. Isolate natural community types in town protected lands.

wbt.multiply(
    input1 = "121_nc_0nd.tif",
    input2 = "312_pro_nat_in_town.tif",
    output = "313_nc_in_pro_nat.tif"
)

# 3.1.4. Compute area of natural communities in blocks.

wbt.raster_area(
    i = "313_nc_in_pro_nat.tif",
    output = "314_nc_in_pro_nat_area.tif",
    out_text=False,
    units="map units",
    zero_back=False,
)

# 3.1.5. Convert to acres.

wbt.divide(
    input1 = "314_nc_in_pro_nat_area.tif",
    input2 = 4046.86,
    output = "315_nc_in_pro_nat_acres.tif"
)

# 3.1.6. Produce table of acres.

wbt.zonal_statistics(
    i = "315_nc_in_pro_nat_acres.tif",
    features = "313_nc_in_pro_nat.tif",
    output=None,
    stat="max",
    out_table="316_TABLE_nc_in_town_pro_lands.html"
)
