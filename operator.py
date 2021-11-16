import bpy

def main(context):
    for ob in context.scene.objects:
        print(ob)


class Operator_01(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.my_first_operator"
    bl_label = "Simple Object Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(Operator_01)


def unregister():
    bpy.utils.unregister_class(Operator_01)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.my_first_operator()
