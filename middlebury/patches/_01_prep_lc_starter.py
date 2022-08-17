#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  name:     _01_prep_lc_starter.py
#  purpose:  Prep datasets:
#              (1) Distinguish small and large patches of bare soils,
#              (2) Burn roads in landcover (to remove tree canopy
#                  that hangs over roads),
#              (3) convert town shapefile into raster.
#  author:   Jeff Howarth
#  update:   08/08/2022
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
wbt.work_dir = "/Volumes/limuw/conservation/outputs/landscapePatches/_01"

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Required datasets:
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Imported datasets

rds = "/Volumes/limuw/conservation/data/midd/rdsFragmenting_12092021.tif"
nhd_connectors = '/Volumes/limuw/conservation/data/midd/middPlan_images/i_hydro_connectors_08082022.tif'
nhd_patches = '/Volumes/limuw/conservation/data/midd/middPlan_images/i_hydro_patches_08082022.tif'
lc = "/Volumes/limuw/conservation/data/midd/iLandCover_midd_12152021.tif"
e911 = "/Volumes/limuw/conservation/data/vtShapes/VT_Data_-_E911_Footprints/e911_footprints.shp"
town = "/Volumes/limuw/conservation/data/vtShapes/vtBoundaries/BoundaryTown_TWNBNDS/middlebury.shp"

# Land cover codes to start

#  0. Conifers
#  1. Deciduous
#  2. Shrub
#  3. Water
#  4. Ag (was #a6a6a6')
#  5. Building Buffers
#  6. Buildings
#  7. Bare soil
#  8. Roads
#  9. 0ther pavement
# 10. Railroads

# ########################################################
#
# # Step 1: Prepare key datasets
#
# ########################################################
#
# ------------------------------------------------------
# 1.0 Burn e911 footprints into land cover layer.
# ------------------------------------------------------

wbt.vector_polygons_to_raster(
    i = e911,
    output = "x01_e911.tif",
    field="CODE",
    nodata=False,
    cell_size=None,
    base=lc,
)

wbt.equal_to(
    input1 = "x01_e911.tif",
    input2 = 0,
    output = "x02_binary_inverse.tif",
)

wbt.raster_calculator(
    output = "x03_lc_update.tif",
    statement = "(('/Volumes/limuw/conservation/data/midd/iLandCover_midd_12152021.tif' * 'x02_binary_inverse.tif') + 'x01_e911.tif')"
)

# ------------------------------------------------------
# 1.0. Burn fragmenting roads into land cover.
# ------------------------------------------------------

# 1.0.1.  Expand roads by a pixel.

wbt.maximum_filter(
    i = rds,
    output = "101_max.tif",
    filterx=3,
    filtery=3
)

# 1.0.2. Invert roads (make roads = 0 and not roads = 1)

wbt.not_equal_to(
    input1 = "101_max.tif",
    input2 = 1,
    output = "102_invert.tif"
)

# 1.6.3. Add roads to land cover layer

wbt.raster_calculator(
    output = "103_lc_update.tif",
    statement = "('x03_lc_update.tif' * '102_invert.tif') + ('101_max.tif' * 99)"
)

# RESULTS

#  0. Conifers
#  1. Deciduous
#  2. Shrub
#  3. Water
#  4. Ag (was #a6a6a6')
#  5. Building Buffers
#  6. Buildings
#  7. Bare soil
#  8. Roads
#  9. 0ther pavement
# 10. Railroads
# 99. Fragmenting roads

# ------------------------------------------------------
# 1.1. Simplify landclasses.
# ------------------------------------------------------

# GOALS

#  0. Conifers              --> 1. Tree canopy
#  1. Deciduous             --> 1. Tree canopy
#  2. Shrub
#  3. Water
#  4. Ag (was #a6a6a6')
#  5. Building Buffers      --> 5. Built
#  6. Buildings             --> 5. Built
#  7. Bare soil
#  8. Roads
#  9. 0ther pavement
# 10. Railroads
# 99. Fragmenting roads

# 1.1.1 Reclass landcover.

wbt.reclass(
    i = "103_lc_update.tif",
    output = "111_reclass.tif",
    reclass_vals = "1;0;1;1;5;5;5;6",
    assign_mode=True,
)

# ------------------------------------------------------
# 1.2. Make objects from land cover.
# ------------------------------------------------------

# 1.2.1. Clump objects.

wbt.clump(
    i = "111_reclass.tif",
    output = "121_clumps.tif",
    diag=False,
    zero_back=False
)

# 1.2.2. Compute area of each clump

wbt.raster_area(
    i = "121_clumps.tif",
    output= "122_clumps_area.tif",
    out_text=False,
    units="map units",
    zero_back=True
)

# 1.2.3. Convert to acres

wbt.divide(
    input1 = "122_clumps_area.tif",
    input2 = 4046.86,
    output = "123_clumps_acres.tif"
)

# 1.2.4. CLassify by area (< 0.25, < 10, > 10).

wbt.reclass(
    i = "123_clumps_acres.tif",
    output = "124_clumps_acres_reclass.tif",
    reclass_vals = "0;0;0.25;100;0.25;10;1000;10;999999999999999999",
    assign_mode = False
)

# 1.2.5. Tag pixels

wbt.add(
    input1 = "111_reclass.tif",
    input2 = "124_clumps_acres_reclass.tif",
    output = "125_lc_add.tif",
)

# RESULTS

# Land cover classified by patch area.

# <0.25             <10             >10

#   1               101             1001        Tree
#   2               102             1002        Shrub
#   3               103             1003        Water
#   4               104             1004        Ag
#   5               105             1005        Built
#   7               107             1007        Bare soil
#   8               108             1008        Roads
#   9               109             1009        0ther pavement
#  10               110             1010        Railroads
#  99               199             1099        Fragmenting roads


# ------------------------------------------------------
# 1.3. Define landscape patches.
# ------------------------------------------------------

# GOAL

# 0     Recovering = 101,102,1002,
# 1     Reforested = 10001
# 2     Water = 103, 1003
# 3     Clearing = 104, 1004
# 4     Developed = 105, 107, 109, 1005, 1007, 1009
# 10    Green Background = 1, 2, 3, 4
# 20    Built background = 5,7,8,9,10, 108, 110, 1008, 1010
# 99    Fragmenting = 99, 199, 1099

# Reclass values
# "10;1;10;2;10;3;10;4;20;5;20;7;20;8;20;9;20;10;99;99;0;101;0;102;2;103;3;104;4;105;4;107;20;108;4;109;20;110;99;199;1;1001;0;1002;2;1003;3;1004;4;1005;4;1007;20;1008;4;1009;20;1010;99;1099"

# 1.3.1 Reclass area objects.

wbt.reclass(
    i = "125_lc_add.tif",
    output = "131_reclass.tif",
    reclass_vals = "10;1;10;2;10;3;10;4;20;5;20;7;20;8;20;9;20;10;99;99;0;101;0;102;2;103;3;104;4;105;4;107;20;108;4;109;20;110;99;199;1;1001;0;1002;2;1003;3;1004;4;1005;4;1007;20;1008;4;1009;20;1010;99;1099",
    assign_mode=True,
)

# 1.3.2. Make a binary of green background.

wbt.equal_to(
    input1 = "131_reclass.tif",
    input2 = 10,
    output = "132_green_binary.tif",
)

# 1.3.3. Make a binary of built background.

wbt.equal_to(
    input1 = "131_reclass.tif",
    input2 = 20,
    output = "133_built_binary.tif",
)

# 1.3.4. Add the two binaries.

wbt.raster_calculator(
    output = "134_backgroun_union.tif",
    statement = "(('132_green_binary.tif' * 10) + ('133_built_binary.tif' * 20))",
)

# ------------------------------------------------------
# 1.4. Replace small patches with neighboring class.
# ------------------------------------------------------

# 1.4.1. Make objects from background union.

wbt.clump(
    i = "134_backgroun_union.tif",
    output = "141_clumps.tif",
    diag=False,
    zero_back=True
)

# 1.4.2. Expand dough classes by 1 pixel.

wbt.minimum_filter(
    i = "131_reclass.tif",
    output = "142_min_filter.tif",
    filterx=3,
    filtery=3
)

# 1.4.3. Overlay objects with land cover to find range.

wbt.zonal_statistics(
    i = "142_min_filter.tif",
    features = "141_clumps.tif",
    output = "143_overlap.tif",
    stat="min",
    out_table=None,
)

# 1.4.4 Create binary of background values.

wbt.Or(
    input1 = "132_green_binary.tif",
    input2 = "133_built_binary.tif",
    output = "144_binary.tif",
)

# 1.4.5. Create inverse of binary.

wbt.equal_to(
    input1 = "144_binary.tif",
    input2 = 0,
    output = "145_binary_inverse.tif",
)

# 1.4.6. Plug holes.

wbt.raster_calculator(
    output = "146_lc_update.tif",
    statement = "(('144_binary.tif' * '143_overlap.tif') + ('145_binary_inverse.tif' * '131_reclass.tif'))",
)

# 1.4.7 Reclass islands from road circles as developed.

wbt.reclass(
    i = "146_lc_update.tif",
    output = "147_lc_patches.tif",
    reclass_vals = "4;10;4;20",
    assign_mode=True,
)

# VISUALIZATion

# Grass =       #FAF87D
# Trees =       #C6E37D
# Water =       #94DAE3
# Ag =          #C67DE3
# Developed     #c8c8c8
# background    #191919
# paths         #E371AD
# fragmenting   #ffffff

# ------------------------------------------------------
# 1.5. Burn hydro features.
# ------------------------------------------------------

# 1.5.1 Replace noData with Zero.

wbt.convert_nodata_to_zero(
    i = nhd_patches,
    output = "151_nd0.tif"
)

# 1.5.2. Make binary.

wbt.not_equal_to(
    input1 = "151_nd0.tif",
    input2 = 0,
    output = "152_binary.tif",
)

# 1.5.3. Invert binary.

wbt.equal_to(
    input1 = "152_binary.tif",
    input2 = 0,
    output = "153_binary_inverse.tif",
)

# 1.5.4 Burn into lc (but without having rivers cross over fragmenting roads).

wbt.raster_calculator(
    output = "154_lc_update.tif",
    statement = "(('152_binary.tif' * '102_invert.tif' * 2) + ('147_lc_patches.tif' * '153_binary_inverse.tif') + ('101_max.tif' * '152_binary.tif' * 99))",
)
