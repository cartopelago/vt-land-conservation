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
rc = "/Volumes/limuw/conservation/data/vtShapes/vtRiverCorridors/WaterHydro_RiverCorridors/epsg32145/riverCorridors_epsg32145.shp"
rc_ss = "/Volumes/limuw/conservation/data/vtShapes/vtRiverCorridors/WaterHydro_RiverCorridors/epsg32145/smallStreams_gtp25_epsg32145.shp"


# ------------------------------------------------------------------------------
# CLASSIFY LANDFORMS
# ------------------------------------------------------------------------------

def classifyLandforms():
    "To classify landforms with geomorphons."
    wbt.work_dir = scratch_repo
    wbt.resample(inputs = dem, output = "_dem_3m.tif", cell_size=None, base=lc, method="cc")
    wbt.geomorphons(dem = "_dem_3m.tif", output = data_repo+"_landforms.tif", search=5000, threshold=0.0, tdist=0, forms=True,)
    return;

# ------------------------------------------------------------------------------
# MAKE LOWLANDS BINARY
# ------------------------------------------------------------------------------

def makeLowlands(landforms):
    "To classify lowlands from geomorphon landforms."
    wbt.work_dir = scratch_repo
    # threshold landform classes
    wbt.greater_than(input1 = landforms, input2 = 9,output = '_01.tif',incl_equals=True,)
    # take majority class within 50 feet
    wbt.majority_filter(i = "_01.tif", output = data_repo+"_lowlands.tif",filterx=11,filtery=11)

# ------------------------------------------------------------------------------
# MAKE BINARY LAYERS
# ------------------------------------------------------------------------------

def makeBinary(code, label):
    "To make binary layer from a selected category."
    wbt.work_dir = scratch_repo
    wbt.equal_to(input1 = starter, input2 = code, output = data_repo+label+'_binary.tif')
    wbt.set_nodata_value(i = data_repo+label+'_binary.tif', output = label+'_binary_0nd.tif',back_value=0)
    wbt.clump(i = label+'_binary_0nd.tif', output = data_repo+label+'_objects.tif', diag=True, zero_back=False)
    return;

# ------------------------------------------------------------------------------
# MAKE OBJECTS LAYERS
# ------------------------------------------------------------------------------

def makeObjects(code, label):
    "To create objects from a selected category."
    wbt.work_dir = scratch_repo
    wbt.equal_to(input1 = starter, input2 = code, output = label+'_01.tif')
    wbt.clump(i = label+'_01.tif', output = data_repo+label+'_objects.tif', diag = False, zero_back = True)
    return;

# ------------------------------------------------------------------------------
# WITH ROAD CROSSINGS
# ------------------------------------------------------------------------------

def withRoadXing(base, label):
    "To find road crossings with a selected category."
    wbt.work_dir = scratch_repo
    wbt.not_equal_to(input1 = base, input2 = 0, output = '_01.tif')
    wbt.maximum_filter(i = '_01.tif', output = '_02.tif', filterx=5, filtery=5)
    wbt.equal_to(input1 = starter, input2 = 99, output = '_03.tif')
    wbt.multiply(input1 = '_03.tif', input2 = '_02.tif', output='_04.tif')
    wbt.Or(input1 ='_04.tif', input2='_01.tif', output='_05.tif')
    wbt.clump(i = '_05.tif', output = data_repo+label+'_withRoadXing.tif', diag=True, zero_back=True)
    return;

# ------------------------------------------------------------------------------
# CLASSIFY TOPOLOGY FUNCTION
# ------------------------------------------------------------------------------

def classTopology(figure, ground, label):
    "To create topology classes for figure and ground object layers with 0 as background."
    wbt.work_dir = scratch_repo
    # Convert figure background 0 into noData.
    wbt.set_nodata_value(i = figure, output = 'a.tif', back_value = 0)

    # Grow ground edge by one pixel.
    wbt.maximum_filter(i = ground, output = 'b.tif', filterx=3, filtery=3)
    # Test for overlap.
    wbt.zonal_statistics(i = 'b.tif', features = 'a.tif', output = 'c.tif', stat = "max", out_table = None)
    # Test for inequality
    wbt.not_equal_to(input1 = 'c.tif', input2 = 'b.tif', output = 'd.tif')

    # ISLAND TEST
    # if max is 0 then island.
    wbt.zonal_statistics(i = 'd.tif', features = 'a.tif', output = 'e.tif', stat = "max", out_table = None)
    wbt.equal_to(input1 = 'e.tif', input2 = 0, output = '_islands.tif')

    # Erase equal overlap
    wbt.multiply(input1 = 'd.tif', input2 = 'b.tif', output = 'e.tif')
    # Test for overlap again.
    wbt.zonal_statistics(i = 'e.tif', features = 'a.tif', output = 'f.tif', stat = "max", out_table = None)

    # TOMBOLO TEST
    # If greater than 0, then figure connects at least two ground patches.
    wbt.greater_than(input1 = 'f.tif', input2 = 0, output = '_tombolos.tif', incl_equals=False)

    # Assemble figure objects that have been classed thus far.
    wbt.Or(input1 = '_islands.tif', input2 = '_tombolos.tif', output='g.tif')
    wbt.equal_to(input1 = 'g.tif', input2 = 0, output = 'h.tif')

    # Convert ground into a binary.
    wbt.not_equal_to(input1 = ground, input2 = 0, output = 'aa.tif')
    # Convert figure into binary
    wbt.not_equal_to(input1 = figure, input2 = 0, output = 'bb.tif')
    # Union figure and ground binaries.
    wbt.Or(input1 = 'aa.tif', input2 = 'bb.tif', output='cc.tif')
    # Invert union
    wbt.equal_to(input1 = 'cc.tif', input2 = 0, output = 'dd.tif')
    # Grow ground edge by one pixel.
    wbt.maximum_filter(i = 'dd.tif', output = 'ee.tif', filterx=3, filtery=3)

    # TEST HOLES VERSUS SPITS
    wbt.zonal_statistics(i = 'ee.tif', features = 'a.tif', output = 'gg.tif', stat = "max", out_table = None)
    # If test = 0, then hole, else spit.
    wbt.equal_to(input1 = 'gg.tif', input2 = 0, output = 'hh.tif')
    wbt.not_equal_to(input1 = 'gg.tif', input2 = 0, output = 'ii.tif')
    # Remove previously classed patches from outputs
    wbt.multiply(input1 = 'hh.tif', input2 = 'h.tif', output = '_holes.tif')
    wbt.multiply(input1 = 'ii.tif', input2 = 'h.tif', output = '_spits.tif')
    # compile topology class layer where islands = 1, spits = 2, holes = 3 and tombolos = 4
    address = label+"_topology.tif"
    wbt.raster_calculator(output = address, statement="('_islands.tif') + ('_spits.tif' * 2) + ('_holes.tif' * 3) + ('_tombolos.tif' * 4)")
    wbt.convert_nodata_to_zero(i = label+"_topology.tif", output = data_repo+label+'_topology.tif')
    return;

# ------------------------------------------------------------------------------
# FOREST HABITAT BLOCK FUNCTION
# ------------------------------------------------------------------------------

# Make forest habitat blocks by combining reforested with recovering-reforested holes.

def makeForestHabitatBlocks(blocks, topology, label):
    "To make habitat blocks by filling holes."
    wbt.work_dir = scratch_repo
    # Select holes from topology.
    wbt.equal_to(input1 = topology, input2 = 3, output = '_01.tif')
    # Union holes with ground.
    wbt.Or(input1 = blocks, input2 = '_01.tif', output = '_02.tif')
    # Identify objects.
    wbt.clump(i = '_02.tif', output = data_repo+label+'_blocks.tif', diag=True, zero_back=True)
    return;

# ------------------------------------------------------------------------------
# FIELD HABITAT BLOCK FUNCTION
# ------------------------------------------------------------------------------

def makeFieldHabitatBlocks(ground, topology1, topology2, label):
    "To make field habitat blocks with recovering-clearing holes and recovering-forest islands."
    wbt.work_dir = scratch_repo
    # Select recovering holes in clearing ground from topology1.
    wbt.equal_to(input1 = topology1, input2 = 3, output = '_01.tif')
    # Select recovering islands in forest ground from topology2.
    wbt.equal_to(input1 = topology2, input2 = 1, output = '_02.tif')
    # Union holes and islands .
    wbt.Or(input1 = '_01.tif', input2 = '_02.tif', output = '_03.tif')
    # Make binary from field ground
    wbt.not_equal_to(input1 = ground, input2 = 0, output = '_04.tif')
    # Union topology features with ground binary.
    wbt.Or(input1 = '_03.tif', input2 = '_04.tif', output = '_05.tif')
    # Identify objects.
    wbt.clump(i = '_05.tif', output = data_repo+label+'_blocks.tif', diag=True, zero_back=True)
    return;

# ------------------------------------------------------------------------------
# MAKE RIVER CORRIDORS AND SMALL STREAMS BINARY
# ------------------------------------------------------------------------------

def makeRiverCorridorsAndSmallStreamsBinary():
    wbt.work_dir = scratch_repo
    wbt.vector_polygons_to_raster(i=rc, output='_01.tif', field="OBJECTID", nodata=False, cell_size=None, base=starter)
    wbt.vector_lines_to_raster(i=rc_ss, output='_02.tif', field="OBJECTID", nodata=False, cell_size=None, base=starter)
    wbt.buffer_raster(i='_02.tif', output='_03.tif', size=15, gridcells=False)
    wbt.Or(input1='_01.tif', input2='_03.tif', output=data_repo+'_riverCorridors_with_smallStreamBuffers.tif')
    return;

# ------------------------------------------------------------------------------
# BLOCKS WITH RIVER CORRIDORS
# ------------------------------------------------------------------------------

def withRiverCorridors(base, label):
    wbt.work_dir = scratch_repo
    wbt.vector_polygons_to_raster(i=rc, output=data_repo+'_riverCorridors.tif', field="OBJECTID", nodata=False, cell_size=None, base=starter)
    wbt.not_equal_to(input1 = base, input2 = 0, output = '_01.tif')
    wbt.Or(input1=data_repo+'_riverCorridors.tif', input2='_01.tif', output='_02.tif')
    wbt.clump(i = '_02.tif', output = data_repo+label+'_with_river_corridors.tif', diag=True, zero_back=True)
    return;

# ------------------------------------------------------------------------------
# BLOCKS WITH RIVER CORRIDORS AND SMALL STREAMS
# ------------------------------------------------------------------------------

def withRiverCorridorsAndSmallStreams(base, label):
    wbt.work_dir = scratch_repo
    wbt.vector_polygons_to_raster(i=rc, output='_01.tif', field="OBJECTID", nodata=False, cell_size=None, base=starter)
    wbt.vector_lines_to_raster(i=rc_ss, output='_02.tif', field="OBJECTID", nodata=False, cell_size=None, base=starter)
    wbt.buffer_raster(i='_02.tif', output='_03.tif', size=15, gridcells=False)
    wbt.Or(input1='_01.tif', input2='_03.tif', output=data_repo+'_riverCorridors.tif')
    wbt.not_equal_to(input1 = base, input2 = 0, output = '_04.tif')
    wbt.Or(input1=data_repo+'_riverCorridors.tif', input2='_04.tif', output='_05.tif')
    wbt.clump(i = '_05.tif', output = data_repo+label+'_with_river_corridors_and_small_streams.tif', diag=True, zero_back=True)
    return;

# ------------------------------------------------------------------------------
# DEFINE OPEN LOWLAND HABITAT
# ------------------------------------------------------------------------------

def openLowlands(lowlands, blocks, starter):
    # tag lowlands with forest habitat patches.
    wbt.multiply(input1 = lowlands, input2 = blocks, output = '_01.tif')
    # isolate the forest block negative space.
    wbt.equal_to(input1 = '_01.tif', input2 = 0, output = '_02.tif')
    # make inverse developed binary layer (0 if developed, 1 if not developed).
    wbt.not_equal_to(input1 = starter, input2 = 4, output = '_03.tif')
    # grow inversed developed binary layer to remove fragmenting roads.
    wbt.minimum_filter(i = '_03.tif', output = '_04.tif', filterx=5, filtery=5)
    # intersect inverse developed binary layer and forest block negative space to identify open, undeveloped space.
    wbt.And(input1='_02.tif', input2='_04.tif', output='_05.tif')
    # intersect green negative space and lowlands to identify potential connectors.
    wbt.And(input1=lowlands, input2='_05.tif', output='_06.tif')
    # Make objects
    wbt.clump(i = '_06.tif', output = data_repo+'_open_lowlands.tif', diag=False, zero_back=True)
    return;

# ------------------------------------------------------------------------------
# DEFINE HABITAT CONNECTORS
# ------------------------------------------------------------------------------

def makeHabitatConnectors(forest_blocks, field_blocks, forest_topology, lowland_topology, rivers):
    wbt.work_dir = scratch_repo
    # Criteria 1 - where recovering patches spur forest blocks --> habitat connectors
    wbt.equal_to(input1 = forest_topology, input2 = 2, output = '_01.tif')
    # Criteria 2 - where recovering patches tombolo forest blocks --> habitat connectors
    wbt.equal_to(input1 = forest_topology, input2 = 4, output = '_02.tif')
    # Criteria 3 - where open lowlands touch one or more forest block
    wbt.equal_to(input1 = lowland_topology, input2 = 4, output = '_03.tif')
    # Criteria 4: where river and small stream corridors intersect field blocks
    wbt.And(input1 = rivers, input2 = field_blocks, output = '_04.tif')
    # Union criteria
    wbt.raster_calculator(output = data_repo+'_forest_habitat_connectors.tif', statement="'_01.tif' || '_02.tif' || '_03.tif' || '_04.tif'")
    return;

# ------------------------------------------------------------------------------
# IDENTIFY FIELD BLOCKS IN SCENIC FOREGROUNDS
# ------------------------------------------------------------------------------

def identifyScenicForegrounds(blocks, scenic, label):
    wbt.work_dir = scratch_repo
    # Criteria 1 - where field blocks intersect scenic foregrounds
    # Make field blocks binary.
    wbt.not_equal_to(input1 = blocks, input2 = 0, output = '_01.tif')
    # Make scenic blocks binary for foreground visibility.
    wbt.equal_to(input1 = scenic, input2 = 2, output = '_02.tif')
    # Intersect field blocks and scenic foregrounds.
    wbt.And(input1 = '_01.tif', input2 = '_02.tif', output = data_repo+label+'_block_scenic_foregrounds.tif')
    return;

# ------------------------------------------------------------------------------
# IDENTIFY FIELD BLOCKS IN CLEARINGS
# ------------------------------------------------------------------------------

def identifyClearings(blocks, starter, label):
    wbt.work_dir = scratch_repo
    # Criteria 1 - where field blocks intersect scenic foregrounds
    # Make field blocks binary.
    wbt.not_equal_to(input1 = blocks, input2 = 0, output = '_01.tif')
    # Make clearing binary .
    wbt.equal_to(input1 = starter, input2 = 3, output = '_02.tif')
    # Intersect field blocks and clearings.
    wbt.And(input1 = '_01.tif', input2 = '_02.tif', output = data_repo+label+'_block_clearings.tif')
    return;

# ------------------------------------------------------------------------------
# CLASSIFY FIELD BLOCKS
# ------------------------------------------------------------------------------

def classifyFieldBlocks(blocks, scenic, starter):
    wbt.work_dir = scratch_repo
    # Make field blocks binary.
    wbt.not_equal_to(input1 = blocks, input2 = 0, output = '_01.tif')
    # Criteria 1 - where field blocks intersect scenic foregrounds
    # Make scenic blocks binary for foreground visibility.
    wbt.equal_to(input1 = scenic, input2 = 2, output = '_02.tif')
    # Remove noise from scenic layer.
    wbt.maximum_filter(i = '_02.tif', output = '_03.tif', filterx=3, filtery=3)
    # SCENIC FOREGROUNDS: Intersect field blocks and scenic foregrounds.
    wbt.And(input1 = '_01.tif', input2 = '_03.tif', output = '_04.tif')
    # Criteria 2 - where field blocks intersect recovering
    # Make clearing binary .
    wbt.equal_to(input1 = starter, input2 = 0, output = '_05.tif')
    # RECOVERING: Intersect field blocks and clearings.
    wbt.And(input1 = '_01.tif', input2 = '_05.tif', output = '_06.tif')
    # Criteria 3 - where field blocks intersect clearing
    # Make clearing binary .
    wbt.equal_to(input1 = starter, input2 = 3, output = '_07.tif')
    # CLEARINGS: Intersect field blocks and clearings.
    wbt.And(input1 = '_01.tif', input2 = '_07.tif', output = '_08.tif')
    # Tag composite classes: 1 FIELD, 1000 SCENIC, 10 RECOVERING, 100 CLEARING
    statement = "(('_04.tif' * 1000) + ('_06.tif' * 10) + ('_08.tif' * 100) + '_01.tif')"
    wbt.raster_calculator(output = '_09.tif', statement = statement)
    # COMPOSITE LAYER: 0 background, 1 old field, 2 working field, 3 field in scenic foreground
    reclass = "0;0;1;1;1;11;2;101;3;1001;3;1011;3;1101"
    wbt.reclass(i = '_09.tif', output = data_repo+'_field_blocks_classed.tif', reclass_vals = reclass, assign_mode=True)
    return;

# ------------------------------------------------------------------------------
# COMPOSITE LAYER
# ------------------------------------------------------------------------------

def makeComposite():
    # Make binary of FOREST BLOCKS.
    wbt.not_equal_to(input1 = forest_block, input2 = 0, output = '_01.tif')
    # Make binary of HABITAT CONNECTORS.
    wbt.not_equal_to(input1 = habitat_connector, input2 = 0, output = '_02.tif')
    # Union forest blocks and habitat connectors.
    wbt.Or(input1 = '_01.tif', input2 = '_02.tif', output = '_03.tif')
    # Make binary of scenic field blocks.
    wbt.not_equal_to(input1 = scenic_field_block, input2 = 0, output = '_04.tif')
    # Make SCENIC FIELD FLOCKS by removing forest block - habitat connector union from scenic field blocks.
    wbt.Not(input1 = '_04.tif', input2 = '_03.tif', output = '_05.tif')
    # Union forest blocks, habitat connectors, and scenic field blocks.
    wbt.Or(input1 = '_03.tif', input2 = '_05.tif', output = '_06.tif')
    # Make binary of clearing field blocks.
    wbt.not_equal_to(input1 = clearing_field_block, input2 = 0, output = '_07.tif')
    # Make CLEARING by removing scenic feld blocks from union.
    wbt.Not(input1 = '_07.tif', input2 = '_06.tif', output = '_08.tif')
    # Union forest blocks, habitat connectors, scenic fields, and clearing field blocks.
    wbt.Or(input1 = '_06.tif', input2 = '_07.tif', output = '_09.tif')
    # Make binary of field blocks.
    wbt.not_equal_to(input1 = recovering_field_block, input2 = 0, output = '_10.tif')
    # Make RECOVERING FIELDS by removing forest blocks, habitat connectors, scenic, and clearing from field blocks.
    wbt.Not(input1 = '_10.tif', input2 = '_09.tif', output = '_11.tif')
    # Assign codes
    statement = "(('_01.tif' * 5) + ('_02.tif' * 4) + ('_05.tif' * 3) + ('_11.tif' * 2) + '_08.tif')"
    wbt.raster_calculator(output = data_repo+'_conservation_plan.tif', statement = statement)
    return;
