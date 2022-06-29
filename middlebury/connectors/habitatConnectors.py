#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  name:     habitatConnectors.py
#  purpose:  to identify habitat connectors for conservation planning
#
#  author:   Jeff Howarth
#  update:   06/27/2022
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
wbt.work_dir = "/Volumes/limuw/conservation/outputs/connectors"

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Imported datasets:
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

lc = "/Volumes/limuw/conservation/data/midd/iLandCover_midd_12152021.tif"
nc = "/Volumes/limuw/conservation/data/midd/iNatCom_12222021.tif"
blocks = "/Volumes/limuw/conservation/outputs/tree_blocks/142_C1_blocks_gt10_0nd.tif"
blocks_nd0 = "/Volumes/limuw/conservation/outputs/tree_blocks/144_C1_blocks_gt10_clumps_nd0.tif"
roads = "/Volumes/limuw/conservation/data/midd/rdsFragmenting_12092021.tif"
wet = "/Volumes/limuw/conservation/data/hWetlands/07_allWetlands_reclassed.tif"
hydro = "/Volumes/limuw/conservation/data/midd/iSurfaceWaterDitchRiparian_06282022.tif"
flood = "/Volumes/limuw/conservation/data/midd/iFloodZones_06282022.tif"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Identify potential connectors.
#
# Land covered by water, grass/shrub, or trees,
# that are found outside of tree blocks.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ------------------------------------------------------
# 1.1. Identify low friction land cover.
# ------------------------------------------------------

# 1.1.1. Isolate natural land cover types (including bare).

wbt.reclass(
    i = lc,
    output = "111_natCover.tif",
    reclass_vals = "1;0;1;1;1;2;1;3;0;4;0;5;0;6;1;7;0;8;0;9;0;10",
    assign_mode=True
)

# 1.1.2. Isolate everything that is not bare ground from land cover.

wbt.not_equal_to(
    input1 = lc,
    input2 = 7,
    output = "112_bare_mask.tif"
)

# 1.1.3. Erase small isolated bare spots.

wbt.majority_filter(
    i = "112_bare_mask.tif",
    output = "113_bare_mask_cleaned.tif",
    filterx=5,
    filtery=5
)

# 1.1.4. Intersect nat cover and union.

wbt.And(
    input1 = "111_natCover.tif",
    input2 = "113_bare_mask_cleaned.tif",
    output = "114_intersect_nat_cover_bare.tif"
)

# 1.1.5. Isolate high-confidence wetlands from wetland layer.

wbt.greater_than(
    input1 = wet,
    input2 = 3,
    output = "115_wetlands.tif",
    incl_equals=True,
)

# 1.1.6. Union low friction land cover and wetlands.

wbt.Or(
    input1 = "114_intersect_nat_cover_bare.tif",
    input2 = "115_wetlands.tif",
    output = "116_intersect_low_friction_wetlands.tif"
)

# 1.1.7. Union low friction land cover and FEMA flood zones.

wbt.Or(
    input1 = "116_intersect_low_friction_wetlands.tif",
    input2 = flood,
    output = "117_intersect_low_friction_wetlands_flood.tif"
)

# ------------------------------------------------------
# 1.2. Erase roads from low friction land cover.
# ------------------------------------------------------

# 1.2.1. Expand roads by a pixel.

wbt.maximum_filter(
    i = roads,
    output = "121_rds_buffered.tif",
    filterx=3,
    filtery=3
)

# 1.2.2. Invert roads

wbt.not_equal_to(
    input1 = "121_rds_buffered.tif",
    input2 = 1,
    output = "122_rds_buffered_inverse.tif"
)

# 1.2.3. Isolate natural land cover types

wbt.multiply(
    input1 = "117_intersect_low_friction_wetlands_flood.tif",
    input2 = "122_rds_buffered_inverse.tif",
    output = "123_low_friction_roads_erased.tif",
)

# ------------------------------------------------------
# 1.3. Allow road crossings at road/creek intersections.
# ------------------------------------------------------

# 1.3.1. Isolate creek and ditch lines.

wbt.reclass(
    i = hydro,
    output = "131_creek_ditch.tif",
    reclass_vals = "0;0;1;1;0;2;1;3",
    assign_mode=True
)

# 1.3.2. Intersect creek lines and roads.

wbt.And(
    input1 = "131_creek_ditch.tif",
    input2 = "121_rds_buffered.tif",
    output = "132_creek_road_crossings.tif"
)

# 1.3.3. Buffer intersections by 2 pixels.

wbt.maximum_filter(
    i = "132_creek_road_crossings.tif",
    output = "133_creek_road_crossings_buffered.tif",
    filterx=5,
    filtery=5
)

# 1.3.4. Add road intersections to low friction land cover.

wbt.Or(
    input1 = "133_creek_road_crossings_buffered.tif",
    input2 = "123_low_friction_roads_erased.tif",
    output = "134_low_friction_with_road_crossings.tif"
)

# ------------------------------------------------------
# 1.4. Erase blocks from low friction land cover.
# ------------------------------------------------------

# 1.4.1. Replace nodata with 0.

wbt.convert_nodata_to_zero(
    i = blocks,
    output = "141_blocks_nd0.tif"
)

# 1.3.2. Invert blocks

wbt.reclass(
    i = "141_blocks_nd0.tif",
    output = "142_blocks_inverse.tif",
    reclass_vals = "1;0;0;1",
    assign_mode=True
)

# 1.3.3. Erase forest blocks

wbt.multiply(
    input1 = "134_low_friction_with_road_crossings.tif",
    input2 = "142_blocks_inverse.tif",
    output = "143_low_friction_no_blocks.tif",
)

# 1.3.4. Set zero as no data

wbt.set_nodata_value(
    i = "143_low_friction_no_blocks.tif",
    output = "144_low_friction_no_blocks_0nd.tif",
    back_value = 0,
)

# 1.3.5. Clump open cover.

wbt.clump(
    i = "144_low_friction_no_blocks_0nd.tif",
    output = "145_low_friction_no_blocks_clumps.tif",
    diag=False,
    zero_back=False
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. Define connectivity classes.
#
# Islands = potential connector that is not adjacent to any tree block.
# Holes = potential connector completely encompassed by a single tree block.
# Spurs = potential connector that touches a single tree block, but not enclosed by it.
# Links = potential connector that touches two or more tree blocks.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ------------------------------------------------------
# 2.1. Qualitative test of connectivity.
# ------------------------------------------------------

# 2.1.1. Give tree blocks an external perimeter.

wbt.maximum_filter(
    i = blocks_nd0,
    output = "211_blocks_ex_perimeter.tif",
    filterx=3,
    filtery=3,
)

# 2.1.2. Test of overlap.

wbt.zonal_statistics(
    i = "211_blocks_ex_perimeter.tif",
    features = "145_low_friction_no_blocks_clumps.tif",
    output="212_overlaps_block.tif",
    stat="max",
    out_table=None
)
# 2.1.3. Boolean overlap block image. If max = 0, then connector = island.

wbt.not_equal_to(
    input1 = "212_overlaps_block.tif",
    input2 = 0,
    output = "213_boolean_overlaps_block.tif"
)

# ------------------------------------------------------
# 2.2. Identify islands.
# ------------------------------------------------------

# 2.2.1. Get max of overlap.

wbt.zonal_statistics(
    i = "211_blocks_ex_perimeter.tif",
    features = "145_low_friction_no_blocks_clumps.tif",
    output="221_overlaps_block_max.tif",
    stat="max",
    out_table=None
)

# 2.2.2. Non-equality test. If max overlap = max perimeter, then either island, spur, or link.

wbt.not_equal_to(
    input1 = "221_overlaps_block_max.tif",
    input2 = "211_blocks_ex_perimeter.tif",
    output = "222_overlap_not_equal_test.tif"
)

# ------------------------------------------------------
# 2.3. Identify islands.
# ------------------------------------------------------

# 2.3.1. Erase max from exterior perimeters.

wbt.multiply(
    input1 = "222_overlap_not_equal_test.tif",
    input2 = "211_blocks_ex_perimeter.tif",
    output = "231_erase_max_ex_perim.tif"
)

# 2.3.2. Get max of overlap after removing first max.

wbt.zonal_statistics(
    i = "231_erase_max_ex_perim.tif",
    features = "145_low_friction_no_blocks_clumps.tif",
    output = "232_overlaps_block_max_islands.tif",
    stat = "max",
    out_table = None
)

# 2.3.3 Tag links. If second max > 0, then = link. Else = island or spur.

wbt.not_equal_to(
    input1 = "232_overlaps_block_max_islands.tif",
    input2 = 0,
    output = "233_links.tif"
)

# 2.3.4 Distinguish islands, spurs, and links.

wbt.add(
    input1 = "233_links.tif",
    input2 = "213_boolean_overlaps_block.tif",
    output = "234_overlap_classes.tif"
)

# ------------------------------------------------------
# 2.4. Identify holes.
# ------------------------------------------------------

# 2.4.1. Union of low friction and blocks.

wbt.Or(
    input1 = "143_low_friction_no_blocks.tif",
    input2 = "141_blocks_nd0.tif",
    output = "241_blocks_low_union.tif"
)

# 2.4.2. Invert.

wbt.equal_to(
    input1 = "241_blocks_low_union.tif",
    input2 = 0,
    output = "242_blocks_low_union_invert.tif"
)

# 2.4.3. Buffer negative space.

wbt.maximum_filter(
    i = "242_blocks_low_union_invert.tif",
    output = "243_blocks_low_union_invert_buffer.tif",
    filterx=3,
    filtery=3,
)

#2.4.4. Isolate spurs.

wbt.equal_to(
    input1 = "234_overlap_classes.tif",
    input2 = 1,
    output = "244_spurs_boolean.tif"
)

#2.4.5. Clump spurs.

wbt.clump(
    i = "244_spurs_boolean.tif",
    output = "245_spurs_clumps.tif",
    diag=False,
    zero_back=True
)

#2.4.6. Test for spurs versus holes.

wbt.zonal_statistics(
    i = "243_blocks_low_union_invert_buffer.tif",
    features = "245_spurs_clumps.tif",
    output="246_test_for_holes.tif",
    stat="max",
    out_table=None
)

# ------------------------------------------------------
# 2.5. Final classification.
# ------------------------------------------------------

# 2.5.1. Multiply holes by ten in prep to tag.

wbt.multiply(
    input1 = "246_test_for_holes.tif",
    input2 = 10,
    output = "251_hole_tag.tif"
)

# 2.5.2. Four overlap classes: islands, spurs, links, .

wbt.add(
    input1 = "234_overlap_classes.tif",
    input2 = "251_hole_tag.tif",
    output = "252_connector_classes.tif"
)
