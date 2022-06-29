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
wbt.work_dir = "/Volumes/limuw/conservation/outputs/tree_blocks"

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Required datasets:
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Imported datasets

rds = "/Volumes/limuw/conservation/data/midd/rdsFragmenting_12092021.tif"        # Highways and Class 3 roads
lc = "/Volumes/limuw/conservation/data/midd/iLandCover_midd_12152021.tif"        # 2016 Vermont base land cover
nc = "/Volumes/limuw/conservation/data/midd/iNatCom_12222021.tif"
wet = "/Volumes/limuw/conservation/data/hWetlands/07_allWetlands_reclassed.tif"            # NC from soils

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CRITERION 1
# Do tree canopy locations form blocks that are larger than 10 acres?
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ------------------------------------------------------
# 1.1. Create fragmentation layer from roads
# ------------------------------------------------------

# 1.1.1.  Expand roads by a pixel.

wbt.maximum_filter(
    i = rds,
    output = "111_rds_buffered.tif",
    filterx=3,
    filtery=3
)

# 1.1.2. Invert roads (make roads = 0 and not roads = 1)

wbt.not_equal_to(
    input1 = "111_rds_buffered.tif",
    input2 = 1,
    output = "112_rds_buffered_inverse.tif"
)

# ------------------------------------------------------
# 1.2. Identify forest blocks
# ------------------------------------------------------

# 1.2.1. Isolate tree canopy

wbt.reclass(
    i = lc,
    output = "121_treeCanopy.tif",
    reclass_vals = "1;0;1;1;0;2;0;3;0;4;0;5;0;6;0;7;0;8;0;9;0;10",
    assign_mode=True
)

# 1.2.2. Remove noise from tree canopy

wbt.majority_filter(
    i = "121_treeCanopy.tif",
    output = "122_treeCanopy_majorityFilter.tif",
    filterx=9,
    filtery=9,
)

# 1.2.3. Erase roads from tree canopy

wbt.multiply(
    input1 = "112_rds_buffered_inverse.tif",
    input2 = "122_treeCanopy_majorityFilter.tif",
    output = "123_treeCanopy_eraseRoads.tif",
)

# 1.2.4. Find contiguous regions of habitat

wbt.clump(
    i = "123_treeCanopy_eraseRoads.tif",
    output = "124_treeCanopy_clumps.tif",
    diag=True,
    zero_back=True
)

# 1.2.5. Set zero as no data

wbt.set_nodata_value(
    i = "124_treeCanopy_clumps.tif",
    output = "125_treeCanopy_clumps_nd0.tif",
    back_value = 0,
)

# ------------------------------------------------------
# 1.3. Compute area of blocks.
# ------------------------------------------------------

# 1.3.1. Compute area of each clump

wbt.raster_area(
    i = "125_treeCanopy_clumps_nd0.tif",
    output= "131_treeCanopy_clumps_nd0_area.tif",
    out_text=False,
    units="map units",
    zero_back=True
)

# 1.3.2. Convert to acres

wbt.divide(
    input1 = "131_treeCanopy_clumps_nd0_area.tif",
    input2 = 4046.86,
    output = "132_treeCanopy_clumps_nd0_area_acres.tif"
)

# ------------------------------------------------------
# 1.4. Apply area threshold (>= 10 acres).
# ------------------------------------------------------

# 1.4.1. Identify blocks with area >= 10 acres

wbt.greater_than(
    input1 = "132_treeCanopy_clumps_nd0_area_acres.tif",
    input2 = 10,
    output = "141_C1_blocks_gt10.tif",
    incl_equals=True
)

# 1.4.2. Set zero as no data

wbt.set_nodata_value(
    i =  "141_C1_blocks_gt10.tif",
    output = "142_C1_blocks_gt10_0nd.tif",
    back_value = 0,
)

# 1.4.3. Find contiguous regions of habitat

wbt.clump(
    i = "142_C1_blocks_gt10_0nd.tif",
    output = "143_C1_blocks_gt10_clumps.tif",
    diag=True,
    zero_back=False
)

# 1.4.4. Replace nodata with 0.

wbt.convert_nodata_to_zero(
    i =  "143_C1_blocks_gt10_clumps.tif",
    output = "144_C1_blocks_gt10_clumps_nd0.tif"
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CRITERION 2
#
# Is block large (>100 acres)?
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 2.4.1. Identify blocks with area >= 100 acres

wbt.greater_than(
    input1 = "132_treeCanopy_clumps_nd0_area_acres.tif",
    input2 = 100,
    output = "241_C1_blocks_gt10.tif",
    incl_equals=True
)

# 2.4.2. Set zero as no data

wbt.set_nodata_value(
    i =  "241_C1_blocks_gt10.tif",
    output = "242_C1_blocks_gt10_0nd.tif",
    back_value = 0,
)

# 2.4.3. Find contiguous regions of habitat

wbt.clump(
    i = "242_C1_blocks_gt10_0nd.tif",
    output = "243_C1_blocks_gt10_clumps.tif",
    diag=True,
    zero_back=False
)

# 2.4.4. Replace nodata with 0.

wbt.convert_nodata_to_zero(
    i =  "243_C1_blocks_gt10_clumps.tif",
    output = "244_C1_blocks_gt10_clumps_nd0.tif"
)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CRITERION 3
#
# Does block represent rare community (floodplain forest or clayplain)?
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# --------------------------------------------------------
# 3.1. Isolate rare communities (floodplain or clayplain).
# --------------------------------------------------------

# 3.1.1. Make binary of under-represented communities.

wbt.reclass(
    i = nc,
    output = "311_underRepresentedNatCom.tif",
    reclass_vals = "0;0;0;1;1;2;1;3;1;4;0;5;0;6;0;7;0;8",
    assign_mode=True
)

# --------------------------------------------------------
# 3.2. Compute proportion of block.
# --------------------------------------------------------

# 3.2.1. Intersect block clumps and UR communities.

wbt.multiply(
    input1 = "143_C1_blocks_gt10_clumps.tif",
    input2 = "311_underRepresentedNatCom.tif",
    output = "321_ur_clumps.tif"
)

# 3.2.2. Compute area of intersection.

wbt.raster_area(
    i = "321_ur_clumps.tif",
    output = "322_ur_clumps_area.tif",
    out_text = False,
    units = "map units",
    zero_back = True
)

# 3.2.3. Divide area of intersection by original block area.

wbt.divide(
    input1 = "322_ur_clumps_area.tif",
    input2 = "131_treeCanopy_clumps_nd0_area.tif",
    output = "323_ur_clumps_percent.tif"
)

# 3.2.4. Apply 50% minimum threshold.

wbt.reclass(
    i = "323_ur_clumps_percent.tif",
    output = "324_ur_clumps_percent_threshold.tif",
    reclass_vals = "0;0.0;0.5;1;0.5;99.0",
    assign_mode=False
)

# 3.2.5. Fill noData to 0 to avoid erasing.

wbt.convert_nodata_to_zero(
    i = "324_ur_clumps_percent_threshold.tif",
    output = "325_ur_clumps_percent_threshold_0nd.tif"
)

# 3.2.6. Identify blocks that meet threshold.

wbt.zonal_statistics(
    i = "325_ur_clumps_percent_threshold_0nd.tif",
    features = "143_C1_blocks_gt10_clumps.tif",
    output="326_ur_clumps_percent_threshold_met.tif",
    stat="max",
    out_table=None
)

# 3.2.7. Remove blocks that do not satisify criteria.

wbt.set_nodata_value(
    i = "326_ur_clumps_percent_threshold_met.tif",
    output = "327_C3_ur_majority_blocks.tif",
    back_value=0.0
)

# 3.2.8. Clump blocks that satisify criterion.

wbt.clump(
    i = "327_C3_ur_majority_blocks.tif",
    output = "328_C3_ur_majority_blocks_clumps.tif",
    diag=True,
    zero_back=True
)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CRITERION 4
#
# Does block represent wetland or aquatic habitat?
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# -----------------------------------------------------------------------
# 4.1. Isolate wet communities (water, swamp, floodplain, wet clayplain).
# -----------------------------------------------------------------------

# 4.1.1. Make binary of wet communities.

wbt.reclass(
    i = nc,
    output = "411_wetNatCom.tif",
    reclass_vals = "1;0;1;1;1;2;1;3;0;4;0;5;0;6;0;7;0;8",
    assign_mode=True
)

# 4.1.2. Make binary of water from land cover.

wbt.reclass(
    i = lc,
    output = "412_water_lc.tif",
    reclass_vals = "0;0;0;1;0;2;1;3;0;4;0;5;0;6;0;7;0;8;0;9;0;10",
    assign_mode=True
)

# 4.1.3. Make binary of wetlands.

wbt.reclass(
    i = wet,
    output = "413_wetlands.tif",
    reclass_vals = "0;0;0;1;1;2;1;3;1;4",
    assign_mode=True
)

# 4.1.4. Combine wet nc and lc layers.

wbt.Or(
    input1 = "411_wetNatCom.tif",
    input2 = "412_water_lc.tif",
    output = "414_wet_cover.tif"
)

# 4.1.5. Combine wet union and wetlands layers.

wbt.Or(
    input1 = "413_wetlands.tif",
    input2 = "414_wet_cover.tif",
    output = "415_wet_combo.tif"
)

# --------------------------------------------------------
# 4.2. Compute proportion of block.
# --------------------------------------------------------

# 4.2.1. Intersect block clumps and UR communities.

wbt.multiply(
    input1 = "143_C1_blocks_gt10_clumps.tif",
    input2 = "415_wet_combo.tif",
    output = "421_wet_clumps.tif"
)

# 4.2.2. Compute area of intersection.

wbt.raster_area(
    i = "421_wet_clumps.tif",
    output = "422_wet_clumps_area.tif",
    out_text = False,
    units = "map units",
    zero_back = True
)

# 4.2.3. Divide area of intersection by original block area.

wbt.divide(
    input1 = "422_wet_clumps_area.tif",
    input2 = "131_treeCanopy_clumps_nd0_area.tif",
    output = "423_wet_clumps_percent.tif"
)

# 4.2.4. Apply 50% minimum threshold.

wbt.reclass(
    i = "423_wet_clumps_percent.tif",
    output = "424_wet_clumps_percent_threshold.tif",
    reclass_vals = "0;0.0;0.5;1;0.5;99.0",
    assign_mode=False
)

# 4.2.5. Fill noData to 0 to avoid erasing.

wbt.convert_nodata_to_zero(
    i = "424_wet_clumps_percent_threshold.tif",
    output = "425_wet_clumps_percent_threshold_0nd.tif"
)

# 4.2.6. Identify blocks that meet threshold.

wbt.zonal_statistics(
    i = "425_wet_clumps_percent_threshold_0nd.tif",
    features = "143_C1_blocks_gt10_clumps.tif",
    output="426_wet_clumps_percent_threshold_met.tif",
    stat="max",
    out_table=None
)

# 4.2.7. Remove blocks that do not satisify criteria.

wbt.set_nodata_value(
    i = "426_wet_clumps_percent_threshold_met.tif",
    output = "427_C3_wet_majority_blocks.tif",
    back_value=0.0
)

# 4.2.8. Clump blocks that satisify criterion.

wbt.clump(
    i = "427_C3_wet_majority_blocks.tif",
    output = "428_C3_wet_majority_blocks_clumps.tif",
    diag=True,
    zero_back=True
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CRITERION 5
#
# Is block near a large block.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
