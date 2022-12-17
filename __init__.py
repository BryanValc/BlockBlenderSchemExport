import bpy

import subprocess
from bpy.props import EnumProperty

from bpy_extras.io_utils import ExportHelper

from . import mcschematic, nbtlib, immutable_views


bl_info = {
    "name": "BlockBlender to .schem export",
    "author": "Bryan Valdez",
    "version": (1, 0, 0),
    "blender": (3, 4, 0),
    "location": "File > Export > Export Minecraft .schem",
    "description": "add-on that converts the selected object affected by the geometry node shown in this video www.youtube.com/watch?v=TUw65gz8nOs",
    "warning": "Requires installation of dependencies",
    "tracker_url": "https://github.com/BryanValc/BlockBlenderCSVExport/issues",
    "category": "Import-Export"}


def write_schematic(context, filepath, version):
    dg = context.evaluated_depsgraph_get()
    eval_ob = context.object.evaluated_get(dg)

    schematic = mcschematic.MCSchematic()

    for instance in dg.object_instances:
        if instance.is_instance and instance.parent == eval_ob:
            schematic.setBlock((
                int(((instance.object.matrix_local.translation[0]+(
                    instance.object.scale[0]/2))/instance.object.scale[0])/eval_ob.scale[0]),
                int(((instance.object.matrix_local.translation[2]+(
                    instance.object.scale[2]/2))/instance.object.scale[2])/eval_ob.scale[2]),
                -int(((instance.object.matrix_local.translation[1]+(
                    instance.object.scale[1]/2))/instance.object.scale[1])/eval_ob.scale[1]),
            ), "minecraft:"+instance.object.name)

    fullPath = filepath.replace("\\", "/").split("/")
    path = "/".join(fullPath[:-1])
    name = fullPath[-1]

    name = name.replace(".schem", "")

    schematic.save(path, name, version)


class ExportSCHEMATIC(bpy.types.Operator, ExportHelper):
    bl_idname = "export_schematic.some_data"
    bl_label = "Export Minecraft .schem"

    filename_ext = ".schem"

    # Add a new property to hold the selected version
    version: EnumProperty(
        items=[
            ("JE_1_19_2", "JE 1.19.2", "Minecraft version 1.19.2"),
            ("JE_1_18_2", "JE 1.18.2", "Minecraft version 1.18.2"),
            ("JE_1_18", "JE 1.18", "Minecraft version 1.18"),
            ("JE_1_17_1", "JE 1.17.1", "Minecraft version 1.17.1"),
            ("JE_1_17", "JE 1.17", "Minecraft version 1.17"),
            ("JE_1_16_5", "JE 1.16.5", "Minecraft version 1.16.5"),
            ("JE_1_16_4", "JE 1.16.4", "Minecraft version 1.16.4"),
            ("JE_1_16_3", "JE 1.16.3", "Minecraft version 1.16.3"),
            ("JE_1_16_2", "JE 1.16.2", "Minecraft version 1.16.2"),
            ("JE_1_16_1", "JE 1.16.1", "Minecraft version 1.16.1"),
            ("JE_1_16", "JE 1.16", "Minecraft version 1.16"),
            ("JE_1_15_2", "JE 1.15.2", "Minecraft version 1.15.2"),
            ("JE_1_15_1", "JE 1.15.1", "Minecraft version 1.15.1"),
            ("JE_1_15", "JE 1.15", "Minecraft version 1.15"),
            ("JE_1_14_4", "JE 1.14.4", "Minecraft version 1.14.4"),
            ("JE_1_14_3", "JE 1.14.3", "Minecraft version 1.14.3"),
            ("JE_1_14_2", "JE 1.14.2", "Minecraft version 1.14.2"),
            ("JE_1_14_1", "JE 1.14.1", "Minecraft version 1.14.1"),
            ("JE_1_14", "JE 1.14", "Minecraft version 1.14"),
            ("JE_1_13_2", "JE 1.13.2", "Minecraft version 1.13.2"),
            ("JE_1_13_1", "JE 1.13.1", "Minecraft version 1.13.1"),
            ("JE_1_13", "JE 1.13", "Minecraft version 1.13"),
            ("JE_1_12_2", "JE 1.12.2", "Minecraft version 1.12.2"),
            ("JE_1_12_1", "JE 1.12.1", "Minecraft version 1.12.1"),
            ("JE_1_12", "JE 1.12", "Minecraft version 1.12"),
            ("JE_1_11_2", "JE 1.11.2", "Minecraft version 1.11.2"),
            ("JE_1_11_1", "JE 1.11.1", "Minecraft version 1.11.1"),
            ("JE_1_11", "JE 1.11", "Minecraft version 1.11"),
            ("JE_1_10_2", "JE 1.10.2", "Minecraft version 1.10.2"),
            ("JE_1_10_1", "JE 1.10.1", "Minecraft version 1.10.1"),
            ("JE_1_10", "JE 1.10", "Minecraft version 1.10"),
            ("JE_1_9_4", "JE 1.9.4", "Minecraft version 1.9.4"),
            ("JE_1_9_3", "JE 1.9.3", "Minecraft version 1.9.3"),
            ("JE_1_9_2", "JE 1.9.2", "Minecraft version 1.9.2"),
            ("JE_1_9_1", "JE 1.9.1", "Minecraft version 1.9.1"),
            ("JE_1_9", "JE 1.9", "Minecraft version 1.9")
        ],
        name="Version",
        default="JE_1_19_2"
    )

    def execute(self, context):
        # Use the selected version when saving the schematic
        write_schematic(context, self.filepath,
                        mcschematic.Version[self.version])
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        # Add the enum property to the panel
        layout.prop(self, "version")


def menu_func_export(self, context):
    self.layout.operator(ExportSCHEMATIC.bl_idname,
                         text="Export Minecraft .schem")


def register():
    bpy.utils.register_class(ExportSCHEMATIC)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSCHEMATIC)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
