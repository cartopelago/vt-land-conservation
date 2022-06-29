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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. Identify potential undeveloped connectors.
#
# Land covered by water, grass/shrub, or trees,
# that are found outside of tree blocks.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ------------------------------------------------------
# 1.1. Create tree block eraser.
# ------------------------------------------------------

# 1.1.1. Replace nodata with 0.

wbt.convert_nodata_to_zero(
    i = blocks,
    output = "111_blocks_nd0.tif"
)

# 1.1.2. Invert blocks

wbt.reclass(
    i = "111_blocks_nd0.tif",
    output = "112_blocks_inverse.tif",
    reclass_vals = "1;0;0;1",
    assign_mode=True
)

# ------------------------------------------------------
# 1.2. Erase small ag from land cover
# ------------------------------------------------------

# 1.2.1. Isolate ag from land cover.

wbt.equal_to(
    input1 = lc,
    input2 = 4,
    output = "121_ag.tif"
)

# 1.2.2. Clump ag fields.

wbt.clump(
    i = "121_ag.tif",
    output = "122_ag_clumps.tif",
    diag=True,
    zero_back=True
)

# 1.2.3. Compute area of ag fields.

wbt.raster_area(
    i="122_ag_clumps.tif",
    output="123_ag_clumps_area.tif",
    out_text=False,
    units="map units",
    zero_back=True
)


wbt.raster_area(
    i = "122_ag_clumps.tif",
    output="123_ag_clumps_area.tif",
    out_text=False,
    units="map units",
    zero_back=True,
)

# 1.2.4. Convert to acres.

wbt.divide(
    input1 = "123_ag_clumps_area.tif",
    input2 = 4046.86,
    output = "124_ag_clumps_acres.tif"
)

# 1.2.5. Threshold small fields (<0.5 acres)

wbt.greater_than(
    input1 = "124_ag_clumps_acres.tif",
    input2 = 0.5,
    output = "125_ag_fields_cleaned.tif",
    incl_equals=False
)

# 1.2.6. Threshold small fields (<0.5 acres)

wbt.convert_nodata_to_zero(
    i="125_ag_fields_cleaned.tif",
    output="126_ag_fields_cleaned_nd0.tif"
)

# ------------------------------------------------------
# 1.3. Identify low friction land cover
# ------------------------------------------------------

# 1.3.1. Isolate bare ground from land cover.

wbt.equal_to(
    input1 = lc,
    input2 = 7,
    output = "131_bare.tif"
)

# 1.3.2. Erase small isolated bare.

wbt.majority_filter(
    i = "131_bare.tif",
    output = "132_bare_cleaned.tif",
    filterx=5,
    filtery=5
)

# 1.3.3. Union ag and bare scrubs.

wbt.Or(
    input1 = "126_ag_fields_cleaned_nd0.tif",
    input2 = "132_bare_cleaned.tif",
    output = "133_union_ag_bare_cleaned.tif"
)

# 1.3.4. Inverse union.

wbt.not_equal_to(
    input1 = "133_union_ag_bare_cleaned.tif",
    input2 = 1,
    output = "134_union_ag_bare_cleaned_inverse.tif"
)

# 1.3.5. Isolate natural land cover types (include ag and bare)

wbt.reclass(
    i = lc,
    output = "135_natCover.tif",
    reclass_vals = "1;0;1;1;1;2;1;3;1;4;0;5;0;6;1;7;0;8;0;9;0;10",
    assign_mode=True
)

# 1.3.6. Intersect nat cover and union.

wbt.And(
    input1 = "134_union_ag_bare_cleaned_inverse.tif",
    input2 = "135_natCover.tif",
    output = "136_union_nat_cover_ag_bare.tif"
)

# 1.3.7. Remove noise (largely bare ground pixels) from natural land cover.

wbt.majority_filter(
    i = "136_union_nat_cover_ag_bare.tif",
    output = "137_union_nat_cover_ag_bare_cleaned.tif",
    filterx=5,
    filtery=5
)

# ------------------------------------------------------
# 1.4. Erase roads from low friction land cover.
# ------------------------------------------------------

# 1.4.1. Expand roads by a pixel.

wbt.maximum_filter(
    i = roads,
    output = "141_rds_buffered.tif",
    filterx=3,
    filtery=3
)

# 1.4.2. Invert roads

wbt.not_equal_to(
    input1 = "141_rds_buffered.tif",
    input2 = 1,
    output = "142_rds_buffered_inverse.tif"
)

# 1.4.3. Isolate natural land cover types

wbt.multiply(
    input1 = "137_union_nat_cover_ag_bare_cleaned.tif",
    input2 = "142_rds_buffered_inverse.tif",
    output = "143_nat_cover_no_roads.tif",
)

# ------------------------------------------------------
# 1.5. Erase blocks from low friction land cover.
# ------------------------------------------------------

# 1.5.1. Erase forest blocks

wbt.multiply(
    input1 = "143_nat_cover_no_roads.tif",
    input2 = "112_blocks_inverse.tif",
    output = "151_nat_cover_no_blocks.tif",
)

# 1.5.2. Set zero as no data

wbt.set_nodata_value(
    i = "151_nat_cover_no_blocks.tif",
    output = "152_nat_cover_no_blocks_0nd.tif",
    back_value = 0,
)

# 1.5.3. Clump open cover.

wbt.clump(
    i = "152_nat_cover_no_blocks_0nd.tif",
    output = "153_nat_cover_no_blocks_clumps.tif",
    diag=True,
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
    features = "153_nat_cover_no_blocks_clumps.tif",
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
    features = "153_nat_cover_no_blocks_clumps.tif",
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
    features = "153_nat_cover_no_blocks_clumps.tif",
    output="232_overlaps_block_max_islands.tif",
    stat="max",
    out_table=None
)

# 2.3.3 Tag links. If second max > 0, then = link. Else = island or spur.

wbt.not_equal_to(
    input1 = "232_overlaps_block_max_islands.tif",
    input2 = 0,
    output = "233_links.tif"
)

# ------------------------------------------------------
# 2.4. Identify holes.
# ------------------------------------------------------


# 2.4.1 Invert potential connectors.

wbt.equal_to(
    input1 = "151_nat_cover_no_blocks.tif",
    input2 = 0,
    output = "241_connectors_inverted.tif"
)

# 2.4.2 Create internal perimeter of potential connectors.

wbt.maximum_filter(
    i = "241_connectors_inverted.tif",
    output = "242_connectors_internal_perimeter.tif",
    filterx=3,
    filtery=3,
)

# 2.4.3. Isolate internal perimeters.

wbt.multiply(
    input1 = "242_connectors_internal_perimeter.tif",
    input2 = "151_nat_cover_no_blocks.tif",
    output = "243_internal_perimeters_isolated.tif"
)

# 2.4.4. Clump internal perimeters.

wbt.clump(
    i = "243_internal_perimeters_isolated.tif",
    output = "244_internal_perimeters_isolated_clumps.tif",
    diag=True,
    zero_back=True
)

# 2.4.5. Test clumps for overlap.

wbt.zonal_statistics(
    i = "211_blocks_ex_perimeter.tif",
    features = "244_internal_perimeters_isolated_clumps.tif",
    output="245_test_for_holes.tif",
    stat="min",
    out_table=None
)

# 2.4.6. Threshold overlaps > 0 (if true, then = holes).

wbt.not_equal_to(
    input1 = "245_test_for_holes.tif",
    input2 = 0,
    output = "246_perimeter_holes_threshold.tif"
)

# 2.4.7. Tag potential connectors as holes.

wbt.zonal_statistics(
    i = "246_perimeter_holes_threshold.tif",
    features = "153_nat_cover_no_blocks_clumps.tif",
    output="247_holes.tif",
    stat="max",
    out_table=None
)

# ------------------------------------------------------
# 2.5. Classify connectors (islands, spurs, holes, links)
# ------------------------------------------------------

# 2.5.1 Distinguish islands, spurs, and links.

wbt.add(
    input1 = "233_links.tif",
    input2 = "213_boolean_overlaps_block.tif",
    output = "251_overlap_classes.tif"
)
