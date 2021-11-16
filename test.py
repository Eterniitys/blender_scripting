import bpy

def main(context):
    pass

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
    bl_label = "Hello World Panel"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Make BigBoum", icon='WORLD_DATA')

#        row = layout.row()
#        row.label(text="Active object is: " + obj.name)
#        row = layout.row()
#        row.prop(obj, "name")

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
