import itertools
import math
import random
import re
import time

import bpy
from bpy.props import *
from bpy_extras.io_utils import ExportHelper

from . import block_list
from .dependencies import mcschematic

bl_info = {
    "name": "BlockBlender to .schem export",
    "author": "Bryan Valdez",
    "version": (1, 31, 1),
    "blender": (3, 4, 0),
    "location": "File > Export > Minecraft .schem",
    "description": "add-on that converts the selected object affected by the geometry node shown in this video www.youtube.com/watch?v=TUw65gz8nOs",
    "warning": "Requires installation of dependencies",
    "tracker_url": "https://github.com/BryanValc/BlockBlenderCSVExport/issues",
    "category": "Import-Export"
    }

start_time = 0 #NERD STATISTICS
end_time = 0
block_count = 0
dimensions = 0

def errorObjectNotSelected(self, context):
    self.layout.label(text="You have to select an object!")

def errorSliceSize(self, context):
    self.layout.label(text="The input is not valid, there cannot be slices with 0 or less blocks in any axis!")

def warningRotation(self, context):
    self.layout.label(
        text="It's not recommended to rotate the object when exporting to .schem, you should apply all the transforms!")

def exportStatistics(self, context):  #NERD STATISTICS
    global start_time
    global end_time
    global block_count
    global dimensions
    
    self.layout.label(text="Exported " + str(block_count) + " blocks in " + str(round((end_time - start_time),2)) + " seconds!, with a size of " + str(dimensions) + ", " + str(round(block_count/(end_time - start_time),2)) + " blocks per second")

# scale the structure if the user wants to
def scale_schematic(schematic, scaleXYZ, connect_scaled, hollow_scaled):
    global block_count
    if (scaleXYZ != (1, 1, 1)):
        schematic.getStructure().scaleXYZ(anchorPoint=(0, 0, 0), scaleX=scaleXYZ[0], scaleY=scaleXYZ[1], scaleZ=scaleXYZ[2])
        if connect_scaled:
            temp_schematic = mcschematic.MCSchematic()
            temp_block_count = 0

            if hollow_scaled:
                for i, j, k in itertools.product(range(scaleXYZ[0]), range(scaleXYZ[1]), range(scaleXYZ[2])):
                    if(i == 0 or i == scaleXYZ[0]-1 or j == 0 or j == scaleXYZ[1]-1 or k == 0 or k == scaleXYZ[2]-1):
                        temp_schematic.placeSchematic(schematic, (i, j, k))
                        temp_block_count += block_count
            else:
                for i, j, k in itertools.product(range(scaleXYZ[0]), range(scaleXYZ[1]), range(scaleXYZ[2])):
                    temp_schematic.placeSchematic(schematic, (i, j, k))
                    temp_block_count += block_count

            schematic = temp_schematic
            block_count = temp_block_count
    return schematic

def write_variations(schematic, path, name, version, post_edits):
    variations = re.findall(r'\(([^\)]+)\)', post_edits) # find all the variations
    var_count = 0

    for variation in variations:
        var_count += 1
        suboperations = variation.split("&")

        temp_schematic = mcschematic.MCSchematic()
        temp_schematic.placeSchematic(schematic, (0, 0, 0))

        for suboperation in suboperations:

            targets_and_sources = suboperation.split(":")
            target_materials = targets_and_sources[0].split(",")
            target_list = []
            for target_material in target_materials:
                if "%" in target_material:
                    percentages_and_blocks = target_material.split("%")
                    material = [int(percentages_and_blocks[0]), percentages_and_blocks[1]]
                    target_list.append(material)
                else:
                    material = [100, target_material]
                    target_list.append(material)
            source_materials = targets_and_sources[1].split(",")
            source_list = []
            for source_material in source_materials:
                if "%" in source_material:
                    percentages_and_blocks = source_material.split("%")
                    material = [int(percentages_and_blocks[0]), percentages_and_blocks[1]]
                    source_list.append(material)
                else:
                    material = [100, source_material]
                    source_list.append(material)
        
            temp_schematic = replace_blocks(temp_schematic, target_list, source_list)
        temp_schematic.save(path, (name+"_variation"+str(var_count)), version)
    return len(variations)

def replace_blocks(schematic, target_list, source_list):
    mask = []
    for target in target_list:
        mask.append("minecraft:"+target[1])
    bounds = schematic.getStructure().getBounds()
    for dx, dy, dz in itertools.product(range(bounds[0][0], bounds[1][0]+1), range(bounds[0][1], bounds[1][1]+1), range(bounds[0][2], bounds[1][2]+1)):
        block = schematic.getBlockStateAt((dx, dy, dz))
        if block in mask:
            source = random.choices(source_list, weights=[x[0] for x in source_list], k=1)[0]
            schematic.setBlock((dx, dy, dz), source[1])
    return schematic

# export as slices if the user wants to
def slice_schematic(schematic, filepath, version, export_as_slices, slice_naming, individual_origins, post_edits):

    fullPath = filepath.replace("\\", "/").split("/")
    path = "/".join(fullPath[:-1])
    name = fullPath[-1]

    # this is to remove the .schem extension from the name, this is because of the way the save function works
    name = name.replace(".schem", "")
    variations = 0
    if (export_as_slices[0] == 0 and export_as_slices[1] == 0 and export_as_slices[2] == 0):
        schematic.save(path, name, version)
        if(post_edits != ""):
            variations = write_variations(schematic, path, name, version, post_edits)
        if variations == 0:
            return (filepath.replace("\\", "/") + " saved successfully!")
        else:
            return (filepath.replace("\\", "/") + " saved successfully!, " + str(variations) + " extra variations saved!")
        
    else:
        if(export_as_slices[0] == 0 or export_as_slices[1] == 0 or export_as_slices[2] == 0):
            bpy.context.window_manager.popup_menu(
                errorSliceSize, title="Error", icon='ERROR')
            return ""

        bounds = schematic.getStructure().getBounds()
        min_corner = bounds[0]
        max_corner = bounds[1]
        count = 0

        dx=0
        for i in range(min_corner[0], max_corner[0]+1, export_as_slices[0]):
            dx+=1
            dy=0
            for j in range(min_corner[1], max_corner[1]+1, export_as_slices[1]):
                dy+=1
                dz=0
                for k in range(min_corner[2], max_corner[2]+1, export_as_slices[2]):
                    dz+=1
                    count+=1
                    temp_schematic = schematic.getSubSchematic((i, j, k), (i + export_as_slices[0]-1, j + export_as_slices[1]-1, k + export_as_slices[2]-1))
                    if(individual_origins == "individual-centered"):
                        temp_bounds = ((i, j, k), (i + export_as_slices[0]-1, j + export_as_slices[1]-1, k + export_as_slices[2]-1))
                        temp_schematic.getStructure().center(temp_bounds)#center the structure, this is to make sure that the structure is centered in the slice even if it is surrounded by air
                    elif(individual_origins == "individual-corner"):
                        temp_bounds = ((i-export_as_slices[0]+1, j-export_as_slices[1]+1, k-export_as_slices[2]+1), (i + export_as_slices[0]-1, j + export_as_slices[1]-1, k + export_as_slices[2]-1))
                        temp_schematic.getStructure().center(temp_bounds) #translate the structure to the corner of the slice

                    temp_name = ""     
                    if(slice_naming == "number"):
                        temp_name = name + "_" + str(count)
                    elif(slice_naming == "coordinates"):
                        temp_name = name + "_x" + str(dx) + "_y" + str(dy) + "_z" + str(dz)
                    else:
                        temp_name = name + "_" + str(count) + "_x" + str(dx) + "_y" + str(dy) + "_z" + str(dz)
                    
                    temp_schematic.save(path, temp_name, version)
                    
                    if(post_edits != ""):
                        variations = write_variations(temp_schematic, path, temp_name, version, post_edits)
                    
        if variations == 0:
            return (filepath.replace("\\", "/").replace(".schem","") + " batch saved successfully!, " + str(count) + " slices exported!")
        else:
            return (filepath.replace("\\", "/").replace(".schem","") + " batch saved successfully!, " + str(count) + " slices exported!, " + str(variations) + " extra variations saved!")

def write_schematic(context, filepath, version, origin, rotation, scaleXYZ, connect_scaled, hollow_scaled, y_offset_percentage, export_as_slices, slice_naming, individual_origins, strings_below_falling, post_edits):
    global start_time     #NERD STATISTICS
    global end_time
    global block_count
    global dimensions

    dg = context.evaluated_depsgraph_get()
    eval_ob = context.object.evaluated_get(dg)

    # get the material names from the global collection index, this will eventually be useful
    # for collection in bpy.data.collections:
    #     for obj in eval_ob.users_collection:
    #         print(obj.name)

    eval_ob.rotation_euler[0] = 0   #rotation fix for realized instances, doesn't work with non realized instances
    eval_ob.rotation_euler[1] = 0
    eval_ob.rotation_euler[2] = 0

    # we measure the starting time of the export, some NERD STATISTICS
    start_time = time.time()
    block_count = 0

    if (eval_ob is None):
        bpy.context.window_manager.popup_menu(
            errorObjectNotSelected, title="Error", icon='ERROR')
    else:
        schematic = mcschematic.MCSchematic()
        print("Exporting to .schem...")

        if (len(eval_ob.data.vertices) > 0):
            data = eval_ob.data

            uv_layer = data.uv_layers['full palette'].active.data
            print(len(data.uv_layers))
            for poly in data.polygons:
                print("Polygon index: %d, length: %d" % (poly.index, poly.loop_total))

                for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                    print("    Vertex: %d" % data.loops[loop_index].vertex_index)
                    # print("    UV: %r" % uv_layer)
                    # print("    UV: %r" % uv_layer[loop_index].uv)
                    # print("    UV: %r" % uv_layer.items())
                    # print("    UV: %r" % uv_layer.keys())
                    # print("    UV: %r" % uv_layer.values())
            print("Vertices found, using vertex information")
            min_distance = math.dist(data.vertices[0].co, data.vertices[1].co)
            
            for i in range(0,len(data.vertices),8):
                pos = data.attributes["pos"].data[i].vector
                nameId = data.attributes["ID"].data[i].value
                # get the name of the object from the list based on the ID
                name = "minecraft:"+block_list.get_block(nameId)

                schematic.setBlock((
                    int((pos[0]+(min_distance/2))/min_distance),
                    int((pos[2]+(min_distance/2))/min_distance),
                    -int((pos[1]+(min_distance/2))/min_distance)
                ), name)
                block_count += 1 #NERD STATISTICS
        else:
            print("Instances found, using instance index")
            for instance in dg.object_instances:
                if (instance.is_instance and instance.parent == eval_ob):
                    # handling red mushroom blocks that have all of the faces off
                    convertedName = instance.object.name.replace(
                        "[all_faces=off]", "[down=false,up=false,east=false,west=false,north=false,south=false]")
                    translation = instance.object.matrix_world.translation
                    scale = instance.object.matrix_world.to_scale()
                    schematic.setBlock((
                        int((translation[0]+(scale[0]/2))/scale[0]),
                        int((translation[2]+(scale[2]/2))/scale[2]),
                        -int((translation[1]+(scale[1]/2))/scale[1]),
                    ), "minecraft:"+convertedName)
                    block_count += 1

        #center the structure if the user wants to
        if (origin == "local"):
            schematic.getStructure().center(schematic.getStructure().getBounds())

        # rotate the structure if the user wants to
        if (rotation != (0, 0, 0)):	
            schematic.getStructure().rotateDegrees(anchorPoint=(0, 0, 0), pitch=rotation[0], yaw=rotation[1], roll=rotation[2])
        
        # scale the structure if the user wants to
        schematic = scale_schematic(schematic, scaleXYZ, connect_scaled, hollow_scaled)

        if (y_offset_percentage != 0):
            offset = int((schematic.getStructure().getStructureDimensions(schematic.getStructure().getBounds())[1] / 100) * y_offset_percentage)
            schematic.getStructure().translate((0, offset, 0))

        bounds = schematic.getStructure().getBounds()
        dimensions = schematic.getStructure().getStructureDimensions(bounds)

        if (strings_below_falling):
            falling_blocks = ["minecraft:black_concrete_powder" ,
            "minecraft:blue_concrete_powder" ,
            "minecraft:brown_concrete_powder" ,
            "minecraft:cyan_concrete_powder" ,
            "minecraft:gravel",
            "minecraft:gray_concrete_powder",
            "minecraft:green_concrete_powder",
            "minecraft:light_blue_concrete_powder",
            "minecraft:light_gray_concrete_powder",
            "minecraft:lime_concrete_powder",
            "minecraft:magenta_concrete_powder",
            "minecraft:orange_concrete_powder",
            "minecraft:pink_concrete_powder",
            "minecraft:purple_concrete_powder",
            "minecraft:red_concrete_powder",
            "minecraft:red_sand",
            "minecraft:sand",
            "minecraft:white_concrete_powder",
            "minecraft:yellow_concrete_powder"
            ]
            for dx, dy, dz in itertools.product(range(bounds[0][0], bounds[1][0] + 1), range(bounds[0][1], bounds[1][1] + 1), range(bounds[0][2], bounds[1][2] + 1)):
                block = schematic.getBlockStateAt((dx, dy, dz))
                if (block != "minecraft:air"):
                    if (block in falling_blocks):
                        below_block = schematic.getBlockStateAt((dx, dy - 1, dz))
                        if (below_block == "minecraft:air"):
                            schematic.setBlock((dx, dy - 1, dz), "minecraft:tripwire")

        # export the structure as slices if the user wants to, if not, export the whole structure
        message1 = slice_schematic(schematic, filepath, version, export_as_slices, slice_naming, individual_origins, post_edits)

        end_time = time.time() #NERD STATISTICS

        if (message1 != ""):
            bpy.context.window_manager.popup_menu(exportStatistics, title=message1, icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(errorSliceSize, title="Error", icon='ERROR')


class ExportSCHEMATIC(bpy.types.Operator, ExportHelper):
    bl_idname = "export_schematic.some_data"
    bl_label = "Export Minecraft .schem"

    filename_ext = ".schem"

    # Add a new property to hold the selected version
    version: bpy.props.EnumProperty(
        items=[
            ("JE_1_19_2", "JE 1.19.2(works for JE 1.19.3 also)", "Minecraft Java version 1.19.2"),
            ("JE_1_18_2", "JE 1.18.2", "Minecraft Java version 1.18.2"),
            ("JE_1_18", "JE 1.18", "Minecraft Java version 1.18"),
            ("JE_1_17_1", "JE 1.17.1", "Minecraft Java version 1.17.1"),
            ("JE_1_17", "JE 1.17", "Minecraft Java version 1.17"),
            ("JE_1_16_5", "JE 1.16.5", "Minecraft Java version 1.16.5"),
            ("JE_1_16_4", "JE 1.16.4", "Minecraft Java version 1.16.4"),
            ("JE_1_16_3", "JE 1.16.3", "Minecraft Java version 1.16.3"),
            ("JE_1_16_2", "JE 1.16.2", "Minecraft Java version 1.16.2"),
            ("JE_1_16_1", "JE 1.16.1", "Minecraft Java version 1.16.1"),
            ("JE_1_16", "JE 1.16", "Minecraft Java version 1.16"),
            ("JE_1_15_2", "JE 1.15.2", "Minecraft Java version 1.15.2"),
            ("JE_1_15_1", "JE 1.15.1", "Minecraft Java version 1.15.1"),
            ("JE_1_15", "JE 1.15", "Minecraft Java version 1.15"),
            ("JE_1_14_4", "JE 1.14.4", "Minecraft Java version 1.14.4"),
            ("JE_1_14_3", "JE 1.14.3", "Minecraft Java version 1.14.3"),
            ("JE_1_14_2", "JE 1.14.2", "Minecraft Java version 1.14.2"),
            ("JE_1_14_1", "JE 1.14.1", "Minecraft Java version 1.14.1"),
            ("JE_1_14", "JE 1.14", "Minecraft Java version 1.14"),
            ("JE_1_13_2", "JE 1.13.2", "Minecraft Java version 1.13.2"),
            ("JE_1_13_1", "JE 1.13.1", "Minecraft Java version 1.13.1"),
            ("JE_1_13", "JE 1.13", "Minecraft Java version 1.13"),
            ("JE_1_12_2", "JE 1.12.2", "Minecraft Java version 1.12.2"),
            ("JE_1_12_1", "JE 1.12.1", "Minecraft Java version 1.12.1"),
            ("JE_1_12", "JE 1.12", "Minecraft Java version 1.12"),
            ("JE_1_11_2", "JE 1.11.2", "Minecraft Java version 1.11.2"),
            ("JE_1_11_1", "JE 1.11.1", "Minecraft Java version 1.11.1"),
            ("JE_1_11", "JE 1.11", "Minecraft Java version 1.11"),
            ("JE_1_10_2", "JE 1.10.2", "Minecraft Java version 1.10.2"),
            ("JE_1_10_1", "JE 1.10.1", "Minecraft Java version 1.10.1"),
            ("JE_1_10", "JE 1.10", "Minecraft Java version 1.10"),
            ("JE_1_9_4", "JE 1.9.4", "Minecraft Java version 1.9.4"),
            ("JE_1_9_3", "JE 1.9.3", "Minecraft Java version 1.9.3"),
            ("JE_1_9_2", "JE 1.9.2", "Minecraft Java version 1.9.2"),
            ("JE_1_9_1", "JE 1.9.1", "Minecraft Java version 1.9.1"),
            ("JE_1_9", "JE 1.9", "Minecraft Java version 1.9")
        ],
        name="Version",
        default="JE_1_19_2"
    )

    # Add a new property to hold the origin point
    origin: EnumProperty(
        items=[
            ("world", "World origin", "Origin point relative to blender global coordinates(this is the way it was working before)"),
            ("local", "Centered", "Origin point to the center of the volume of the schematic in all 3 axis"),
        ],
        name="Origin",
        default="world"
    )

    rotation: FloatVectorProperty(
        name="Rotation",
        default=(0, 0, 0),
        min=-360,
        max=360,
        description="Rotation around X, Y and Z axis, inside minecraft X is the red \n axis, Y is the green axis and Z is the blue axis"
    )

    scale: IntVectorProperty(
        name="Scale",
        default=(1, 1, 1),
        min=1,
        max=100,
        description="Scale for X, Y and Z axis, inside minecraft X is the red axis, \n Y is the green axis and Z is the blue axis"
    )

    connect_scaled: BoolProperty(
        name="Connect scaled blocks",
        default=True,
        description="Fill scale for X, Y and Z axis with the same value, otherwise \n if the scales are different from 1, blocks will be flying"
    )

    hollow_scaled: BoolProperty(
        name="Hollow scaled blocks",
        default=False,
        description="Hollow the scaled blocks, so for example, 10x10x10 blocks will \n have a hollow of 8x8x8(this is quicker)"
    )

    y_percentage_offset: FloatProperty(
        name="Y percentage offset",
        default=0,
        min=-10000,
        max=10000,
        description="Percentage of the Y axis to offset the origin point, \n 50% will be bottom of the schematic, if the origin is \n marked as local, it will be bottom centered"
    )

    export_as_slices: IntVectorProperty(
        name="Export as slices",
        default=(0, 0, 0),
        min=0,
        max=10000,
        description="Export the schematic as slices, the first value is for the X-length, \n the second value is for the Y-length and the third value is for the Z-length, \n leave as 0,0,0 to export just one schematic"
    )

    slice_naming: EnumProperty(
        items=[
            ("number", "Number", "Number of the slice, example: slice_1, slice_2, slice_3"),
            ("coordinates", "Coordinate", "Coordinate of the slice, example slice_x0_y0_z0, slice_x0_y0_z1, slice_x0_y0_z2"),
            ("both", "Both", "Number and coordinate of the slice, example: slice_1_x0_y0_z0, slice_2_x0_y0_z1, slice_3_x0_y0_z2")
        ],
        name="Slice naming",
        default="number"
    )

    individual_origins: EnumProperty(
        items=[
            ("shared", "Shared", "All the slices will have the same origin point, meaning that you can paste them without you having to move"),
            ("individual-centered", "Individual centered", "Each slice will have its own origin point at its center"),
            ("individual-corner", "Individual corner", "Each slice will have its origin at its own corner")
        ],
        name="Individual origins",
        default="shared"
    )

    strings_below_falling: BoolProperty(
        name="Strings below falling",
        default=False,
        description="If there are air blocks below a falling block, it will be replaced with a string"
    )

    post_edits: StringProperty(
        name="Post edits",
        default="",
        description="You can replace blocks before exporting and create different variations,e for instance: (stone,dirt,grass_block:andesite) will replace stone, dirt and grass_block with andesite, (red_concrete:blue_concrete&red_wool:blue_wool), will replace red concrete with blue concrete, and red wool with blue wool, (red_concrete:50%blue_concrete,100%green_concrete) will replace red concrete, with 33.3% chance of turning into blue concrete, and 66.6% chance of turning into green concrete for every individual block, creating a noise, you can also skip the percentages, (red_concrete:blue_concrete),(red_concrete:green_concrete) will create two variations in different .schem files"
    )
    def execute(self, context):
        # Use the selected version when saving the schematic
        write_schematic(
            context, 
            self.filepath,
            mcschematic.Version[self.version], 
            self.origin, 
            self.rotation, 
            self.scale, 
            self.connect_scaled, 
            self.hollow_scaled, 
            self.y_percentage_offset, 
            self.export_as_slices, 
            self.slice_naming, 
            self.individual_origins,
            self.strings_below_falling,
            self.post_edits
            )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        # Add properties to the export window
        layout.prop(self, "version")
        layout.prop(self, "origin")
        layout.prop(self, "rotation")
        layout.prop(self, "scale")
        layout.prop(self, "connect_scaled")
        layout.prop(self, "hollow_scaled")
        layout.prop(self, "y_percentage_offset")
        layout.prop(self, "export_as_slices")
        layout.prop(self, "slice_naming")
        layout.prop(self, "individual_origins")
        layout.prop(self, "strings_below_falling")
        layout.prop(self, "post_edits")

def menu_func_export(self, context):
    self.layout.operator(ExportSCHEMATIC.bl_idname,
                         text="Minecraft .schem")


def register():
    bpy.utils.register_class(ExportSCHEMATIC)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSCHEMATIC)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
