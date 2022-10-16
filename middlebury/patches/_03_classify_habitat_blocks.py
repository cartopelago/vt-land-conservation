#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  name:     _classify_habitat_blocks.py
#  purpose:  Distinguish island, spur, hole, and tombology classes between
#               figure and ground images.
#  author:   Jeff Howarth
#  update:   08/11/2022
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

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Working directories
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

data_repo = "/Volumes/limuw/conservation/outputs/_goods/"
scratch_repo = "/Volumes/limuw/conservation/outputs/_scratch"

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Required datasets:
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Imported datasets

starter = "/Volumes/limuw/conservation/outputs/landscapePatches/_01/154_lc_update.tif"
rc = "/Volumes/limuw/conservation/data/vtShapes/vtRiverCorridors/WaterHydro_RiverCorridors/epsg32145/riverCorridors_epsg32145.shp"
rc_ss = "/Volumes/limuw/conservation/data/vtShapes/vtRiverCorridors/WaterHydro_RiverCorridors/epsg32145/smallStreams_gtp25_epsg32145.shp"
town = "/Volumes/limuw/conservation/data/vtShapes/vtBoundaries/BoundaryTown_TWNBNDS/middlebury.shp"

#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  CODES FOR STARTER LAYER.
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

recovering = 0
reforested = 1
water = 2
clearing = 3
developed = 4
fragmenting = 99

# ------------------------------------------------------------------------------
# FOREST HABITAT BLOCK PROGRESSION
# ------------------------------------------------------------------------------

# -------
# STEP 1: Make reforested and recovering object layers.
# -------

# makeObjects(reforested, '_reforested')
# makeObjects(recovering, '_recovering')

figure = data_repo+'_recovering_objects.tif'
ground = data_repo+'_reforested_objects.tif'

# -------
# STEP 2: Class topology of recovering (figure) and reforested (ground).
# -------

# classTopology(figure, ground, '_recovering_reforested')

forest_topology = data_repo+'_recovering_reforested_topology.tif'

# -------
# STEP 3: Identify forest habitat blocks.
# -------

# makeForestHabitatBlocks(ground, forest_topology, '_forest_habitat')

# -------
# STEP 4: Join forest habitat blocks separated by roads.
# -------

# withRoadXing(data_repo+'_forest_habitat_blocks.tif', '_forest_habitat_blocks')

# ------------------------------------------------------------------------------
# DEFINE OPEN LOWLAND HABITAT
# ------------------------------------------------------------------------------

forest_blocks = data_repo+'_forest_habitat_blocks_withRoadXing.tif'
lowlands_binary = data_repo+'_lowlands.tif'

# -------
# STEP 1: identify lowlands with open cover.
# -------

# openLowlands(lowlands_binary, forest_blocks, starter)

# -------
# STEP 2: class topology of open lowlands and forest habitat blocks.
# -------

# classTopology(data_repo+'_open_lowlands.tif', forest_blocks, '_open_lowlands')


# ------------------------------------------------------------------------------
# FIELD BLOCK PROGRESSION
# ------------------------------------------------------------------------------

# -------
# STEP 1: make object layers
# -------

# makeObjects(clearing, '_clearing')
# makeObjects(recovering, '_recovering')

field_figure = data_repo+'_recovering_objects.tif'
field_ground = data_repo+'_clearing_objects.tif'

# -------
# STEP 2: create topology.
# -------

# classTopology(field_figure, field_ground, '_recovering_clearing')

field_topology = data_repo+'_recovering_clearing_topology.tif'

# -------
# STEP 3: identify field blocks.
# -------

# makeFieldHabitatBlocks(field_ground, field_topology, forest_topology, '_field_habitat')

# -------
# STEP 4: join across roads
# -------

# withRoadXing(data_repo+'_field_habitat_blocks.tif', '_field_habitat_blocks')

# -------
# STEP 5: classify field blocks as scenic, clearing, recovering
# -------

field_blocks = data_repo+'_field_habitat_blocks_withRoadXing.tif'
scenic_viewsheds = '/Volumes/limuw/conservation/lScenicViews/data/roads/14_visibilityByRegion.tif'

# ct.classifyFieldBlocks(field_blocks, scenic_viewsheds, starter)


# ------------------------------------------------------------------------------
# DEFINE HABITAT CONNECTORS
# ------------------------------------------------------------------------------

# 1. Make river corridor binary.

# makeRiverCorridorsAndSmallStreamsBinary()

field_blocks = data_repo+'_field_habitat_blocks_withRoadXing.tif'
recovering_reforested_topology = data_repo+'_recovering_reforested_topology.tif'
lowland_connector_topology = data_repo+'_open_lowlands_topology.tif'
river_corridors = data_repo+'_riverCorridors_with_smallStreamBuffers.tif'

# 2. Make habitat connectors.

# ct.makeHabitatConnectors(forest_blocks, field_blocks, recovering_reforested_topology, lowland_connector_topology, river_corridors)

# ------------------------------------------------------------------------------
# COMPOSITE LAYER
# ------------------------------------------------------------------------------

field = data_repo+'_field_blocks_classed.tif'
connector = data_repo+'_forest_habitat_connectors.tif'
forest = data_repo+'_forest_habitat_blocks_withRoadXing.tif'
base = "/Volumes/limuw/conservation/outputs/landscapePatches/_01/154_lc_update.tif"

ct.makeComposite(forest, connector, field, base)

ct.clipByTown('_conservation_plan', data_repo+'_conservation_plan.tif', town, base)
