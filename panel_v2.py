import bpy
from math import cos, sin, pi, sqrt
from random import random

object_list = []


def delete_objects():
    """Delete all objects in the object list.
    """
    for obj in object_list:
        try:
            bpy.data.objects.remove(obj)
        except ReferenceError:
            pass
    del object_list[:]


def generate_objects(count, spawn_radius):
    """Generate cubes.
    """

    for i in range(count):
        a = 2 * pi * random()
        r = spawn_radius * random()
        x = cos(a) * r
        y = sin(a) * r
        size = 1 + 4 * random()
        bpy.ops.mesh.primitive_cube_add(size=size)
        obj = bpy.context.object
        obj.location = (x, y, 0)
        obj.color = (random(), random(), 0, 1)
        object_list.append(obj)


def animate_objects(max_elevation):
    """Animate cubes.
    """

    for obj in object_list:
        try:
            obj.name
        except ReferenceError:
            continue
        obj.location.z = 0
        obj.scale = (1, 1, 1)
        obj.keyframe_insert('location', frame=0)
        obj.keyframe_insert('scale', frame=0)
        obj.location.z = max_elevation * (0.1 + random())
        obj.scale = (0, 0, 0)
        end_frame = 50 + 200 * random()
        obj.keyframe_insert('location', frame=end_frame)
        obj.keyframe_insert('scale', frame=end_frame)


class Generator(bpy.types.Operator):
    bl_idname = "object.cube_generate"
    bl_label = "Generate"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # clear old instances
        delete_objects()
        # generate new instances
        generate_objects(
            bpy.context.scene.cube_count,
            bpy.context.scene.cube_spawn_area,
        )
        return {'FINISHED'}


class Animator(bpy.types.Operator):
    bl_idname = "object.cube_animate"
    bl_label = "Animate"

    @classmethod
    def poll(cls, context):
        return len(object_list) > 0

    def execute(self, context):
        animate_objects(bpy.context.scene.cube_spawn_area)
        return {'FINISHED'}


class Destructor(bpy.types.Operator):
    bl_idname = "object.cube_reset"
    bl_label = "Reset"

    @classmethod
    def poll(cls, context):
        return len(object_list) > 0

    def execute(self, context):
        delete_objects()
        return {'FINISHED'}


class Validator(bpy.types.Operator):
    bl_idname = "object.cube_validate"
    bl_label = "Validate"

    @classmethod
    def poll(cls, context):
        return len(object_list) > 0

    def execute(self, context):
        del object_list[:]
        return {'FINISHED'}


class MyPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_MYPANEL"
    bl_label = "My Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        return (
            not bpy.context.active_object
            or bpy.context.active_object.mode == 'OBJECT'
        )

    def draw(self, context):
        self.layout.label(text="My Panel")
        self.layout.prop(context.scene, "cube_count")
        self.layout.prop(context.scene, "cube_spawn_area")
        self.layout.operator("object.cube_generate")
        self.layout.operator("object.cube_animate")
        row = self.layout.row()
        row.operator("object.cube_validate")
        row.operator("object.cube_reset")


def register():

    bpy.types.Scene.cube_count = bpy.props.IntProperty(
        name="Instances",
        description="Nombre de cubes",
        min=1, max=100000,
        default=10,
    )
    bpy.types.Scene.cube_spawn_area = bpy.props.FloatProperty(
        name="Spawn Area",
        description="Aire de distribution",
        min=1.0, max=100000.0,
        default=100.0,
    )

    bpy.utils.register_class(Generator)
    bpy.utils.register_class(Animator)
    bpy.utils.register_class(Validator)
    bpy.utils.register_class(Destructor)
    bpy.utils.register_class(MyPanel)


def unregister():
    bpy.utils.unregister_class(Generator)
    bpy.utils.unregister_class(Animator)
    bpy.utils.unregister_class(Validator)
    bpy.utils.unregister_class(Resetator)
    bpy.utils.unregister_class(MyPanel)


if __name__ == "__main__":
    register()
