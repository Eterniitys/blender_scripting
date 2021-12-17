import bpy
import sys

from random import random, randint


def get_random_location(location, size=10):
    return (
        location.x + size - 2*size*random(),
        location.y + size - 2*size*random(),
        location.z + size*random(),
    )

def get_random_scale(scale):
    random_scale = 0.05 + 0.25*random()
    return (
        scale.x * random_scale,
        scale.y * random_scale,
        scale.z * random_scale,
    )


def explode(context):
    obj = context.object

    start_frame = context.scene.frame_current

    for i in range(randint(5, 15)):
        c = obj.copy()
        context.collection.objects.link(c)

        c.keyframe_insert('location', frame=start_frame)
        c.keyframe_insert('scale', frame=start_frame)

        end_frame = start_frame + 10 + randint(0, 5)

        c.location = get_random_location(obj.location)
        c.scale = get_random_scale(obj.scale)

        c.keyframe_insert('location', frame=end_frame)
        c.keyframe_insert('scale', frame=end_frame)

    obj.keyframe_insert('scale', frame=start_frame)
    obj.scale = (0, 0, 0)
    obj.keyframe_insert('scale', frame=start_frame + 1)



class ExplodeOperator(bpy.types.Operator):
    """The Explode Operator"""
    bl_idname = "object.explode_operator"
    bl_label = "Explode Object"
    bl_description = "Boom!"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        explode(context)
        return {'FINISHED'}


class ExplodePanel(bpy.types.Panel):
    """Creates a Panel in the Tool panels in View_3D"""
    bl_label = "Explode Tool"
    bl_idname = "OBJECT_PT_explode"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        return (not context.active_object or context.active_object.mode == 'OBJECT')

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Boom!", icon='WORLD_DATA')

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.prop(obj, "name")

        row = layout.row()
        row.operator("object.explode_operator")


def register():
    bpy.utils.register_class(ExplodeOperator)
    bpy.utils.register_class(ExplodePanel)


def unregister():
    bpy.utils.unregister_class(ExplodeOperator)
    bpy.utils.unregister_class(ExplodePanel)


if __name__ == "__main__":
    register()
