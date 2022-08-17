#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  name:     _02_prep_landform_classes.py
#  purpose:  classify landforms from DEM and isolate lowlands.
#
#  author:   Jeff Howarth
#  update:   08/12/2022
#  license:  Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# import tools from WBT module

import sys
sys.path.insert(1, '/Users/jhowarth/tools')
from WBT.whitebox_tools import WhiteboxTools

# declare a name for the tools

wbt = WhiteboxTools()

# import conservation tools module.

sys.path.insert(2, '/Users/jhowarth/projects/vt-land-conservation/middlebury')
import conservation_tools as ct
#
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Working directories
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

data_repo = "/Volumes/limuw/conservation/outputs/_goods/"
scratch_repo = "/Volumes/limuw/conservation/outputs/_scratch"

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Required datasets:
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Imported datasets

lc = "/Volumes/limuw/conservation/data/midd/iLandCover_midd_12152021.tif"
dem = "/Volumes/limuw/conservation/data/midd/iDemHF_0p7_12222021.tif"

# ------------------------------------------------------------------------------
# IMPLEMENT
# ------------------------------------------------------------------------------

# 1. Classify landforms from DEM with geomorphons.

# classifyLandforms()

# 2. Extract lowlands from landforms as all valley bottoms and pits.

landforms = data_repo+"_landforms.tif"
ct.makeLowlands(landforms)
