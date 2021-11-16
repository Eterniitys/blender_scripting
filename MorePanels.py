from typing import List
import bpy
import random as rd

def random_horizontal_shift(origin_location: List[float], max_val: float) -> list[float]:
    return [
            origin_location[0]+(rd.random()-.5)*max_val,
            origin_location[1]+(rd.random()-.5)*max_val,
            origin_location[2]
            ]

def reduce_scale_by_factor(origin_scale: List[float], factor: float) -> list[float]:
    return [
            origin_scale[0] * factor,
            origin_scale[1] * factor,
            origin_scale[2] * factor
            ]

def main(context):

    current_frame = bpy.context.scene.frame_current
    last_frame = current_frame + 20

    cube = bpy.context.object
    cube.keyframe_insert("scale", frame=current_frame)
    cube.keyframe_insert("location", frame=current_frame)

    cube.location[2] += cube.scale[2]*5
    cube.scale = reduce_scale_by_factor(cube.scale, 0.5)

    cube.keyframe_insert("scale", frame=last_frame)
    cube.keyframe_insert("location", frame=last_frame)

    for i in range(10):
        loc = random_horizontal_shift(cube.location, 2)
        bpy.ops.mesh.primitive_cube_add(location=loc)
        c = bpy.context.selected_objects[0]
        c.scale = cube.scale

    bpy.context.scene.frame_current = last_frame


class Operator_01(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.my_first_operator"
    bl_label = "My First Operator"
    bl_description = "First Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}
    

class MakeBigBoumPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Explode Panel"
    bl_idname = "OBJECT_PT_Explode"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Make BigBoum", icon='WORLD_DATA')

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.prop(obj, "name")

        row = layout.row()
        row.operator("object.my_first_operator")


def register():
    bpy.utils.register_class(Operator_01)
    bpy.utils.register_class(MakeBigBoumPanel)


def unregister():
    bpy.utils.unregister_class(Operator_01)
    bpy.utils.unregister_class(MakeBigBoumPanel)


if __name__ == "__main__":
    register()
