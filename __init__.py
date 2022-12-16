import bpy
import csv
from bpy_extras.io_utils import ExportHelper

def write_csv(context, filepath):
    dg = context.evaluated_depsgraph_get()
    eval_ob = context.object.evaluated_get(dg)
    instances = [i for i in dg.object_instances if i.is_instance and i.parent == eval_ob]

    positions = []

    for instance in dg.object_instances:
        if instance.is_instance and instance.parent == eval_ob:
            positions.append((
        instance.object.name,
        int(((instance.object.matrix_local.translation[0]*2)/eval_ob.scale[0])*round(eval_ob.scale[0])), 
        int(((instance.object.matrix_local.translation[1]*2)/eval_ob.scale[0])*round(eval_ob.scale[1])),
        int(((instance.object.matrix_local.translation[2]*2)/eval_ob.scale[0])*round(eval_ob.scale[2]))))

    with open(filepath, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(positions)

class ExportCSV(bpy.types.Operator, ExportHelper):
    """Export object names and positions to a CSV file"""
    bl_idname = "export_csv.some_data"
    bl_label = "Export CSV"

    filename_ext = ".csv"

    def execute(self, context):
        write_csv(context, self.filepath)
        return {'FINISHED'}

# register the export operator
bpy.utils.register_class(ExportCSV)


def menu_func_export(self, context):
    self.layout.operator(ExportCSV.bl_idname, text="Export CSV")
    
# add to a menu
bpy.types.TOPBAR_MT_file_export.append(menu_func_export)