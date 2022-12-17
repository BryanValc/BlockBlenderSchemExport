import bpy
import math  
import subprocess

from bpy_extras.io_utils import ExportHelper

python_path = bpy.app.binary_path.replace("blender.exe", "3.4\\python\\bin\\python.exe")
subprocess.call([python_path, "-m", "ensurepip"])
subprocess.call([python_path, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.call([python_path, "-m", "pip", "install", "mcschematic"])

from mcschematic import mcschematic

def write_schematic(context, filepath):
    dg = context.evaluated_depsgraph_get()
    eval_ob = context.object.evaluated_get(dg)

    schematic = mcschematic.MCSchematic()

    for instance in dg.object_instances:
        if instance.is_instance and instance.parent == eval_ob:
            schematic.setBlock((
            int((instance.object.matrix_local.translation[0]+(instance.object.scale[0]/2))/instance.object.scale[0]),
            int((instance.object.matrix_local.translation[2]+(instance.object.scale[2]/2))/instance.object.scale[2]),
            int((instance.object.matrix_local.translation[1]+(instance.object.scale[1]/2))/instance.object.scale[1]),
            ), "minecraft:"+instance.object.name)

    fullPath = filepath.replace("\\", "/").split("/")
    path = "/".join(fullPath[:-1])
    name = fullPath[-1]

    name = name.replace(".schem", "")

    schematic.save(path, name, mcschematic.Version.JE_1_18_2)

class ExportSCHEMATIC(bpy.types.Operator, ExportHelper):
    """Export object names and positions to a CSV file"""
    bl_idname = "export_schematic.some_data"
    bl_label = "Export Schematic"

    filename_ext = ".schem"

    def execute(self, context):
        write_schematic(context, self.filepath)
        return {'FINISHED'}

# register the export operator
bpy.utils.register_class(ExportSCHEMATIC)


def menu_func_export(self, context):
    self.layout.operator(ExportSCHEMATIC.bl_idname, text="Export schematic")
    
# add to a menu
bpy.types.TOPBAR_MT_file_export.append(menu_func_export)