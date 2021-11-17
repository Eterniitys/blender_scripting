import bpy
import random as rd
from math import cos, sin, sqrt, pi

# Add a plane
"""
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0), scale=(1, 1, 1))
bpy.ops.rigidbody.object_add()
bpy.context.object.rigid_body.type = 'PASSIVE'
bpy.context.object.rigid_body.restitution = 0.8"""

object_list = []

def createBubble(count, maxRadius, maxRange):

    for i in range(count):    
        bubble = generateGrowingBubble(maxRadius, maxRange, object_list)
        if bubble:
            object_list.append(bubble)
        else:
            print("Plus de place. "+str(len(object_list)) + " bulles on été générée")
            break
    #animateBubble(object_list)
            
def generateGrowingBubble(maxRadius, maxRange, lstBubble = []):
    _maxTry = 200
    _inc = 0
    sphere = genBubble(maxRadius, maxRange)
    if len(lstBubble) != 0 :
        isValide = False
        while not isValide and _inc < _maxTry:
            isValide = True
            _suppressed_bubble = []
            for bubble in lstBubble:
                try:
                    if isToClose(bubble, sphere):
                        isValide = False
                        sphere = genBubble(maxRadius, maxRange, sphere)
                        _inc += 1
                        break
                except ReferenceError as e:
                    _suppressed_bubble.append(bubble)
            for b in _suppressed_bubble:
                lstBubble.remove(b)

    sphere.color = ((sphere.scale[0]-1)/maxRadius, 0, 1 - (sphere.scale[0]-1)/maxRadius, 1)
    if _inc >= _maxTry:
        bpy.ops.object.delete()
        sphere = None
    return sphere

def genBubble(maxRadius, maxRange, bubble = None):
    if bubble == None :
        bpy.ops.mesh.primitive_uv_sphere_add()
        bpy.ops.rigidbody.object_add()
        bubble = bpy.context.object
        
    bubble.rigid_body.restitution = 0.7

    _radius = rd.random()*(maxRadius-1)+1
    _angle = rd.random()*2*pi
    _dist = rd.random()*maxRange
    _x = sin(_angle)*_dist
    _y = cos(_angle)*_dist
    
    bubble.location = bpy.context.scene.cursor.location

    bubble.location[0] += _x
    bubble.location[1] += _y
    bubble.location[2] -= _radius
    bubble.scale = [_radius,_radius,_radius]


    return bubble

def bubbleFusing(b1, b2):
    if isToClose(b1, b2):
        b1.scale = (0,0,0)
        b2.scale = (0,0,0)

def isToClose(bubble1, bubble2):
    s1_x = bubble1.location[0]
    s1_y = bubble1.location[1]
    s1_z = bubble1.location[2]
    s2_x = bubble2.location[0]
    s2_y = bubble2.location[1]
    s2_z = bubble2.location[2]
    return(sqrt((s1_x-s2_x)**2 + (s1_y-s2_y)**2 + (s1_z-s2_z)**2) < bubble1.scale[0] + bubble2.scale[0])
    

def distBetweenTwoSphere2D(s1,s2):
    s1_x = s1[0]
    s1_y = s1[1]
    s1_z = s1[2]
    s2_x = s2[0]
    s2_y = s2[1]
    s2_z = s2[2]
    return sqrt((s1_x-s2_x)**2 + (s1_y-s2_y)**2)


def animateBubble(lstBubble=[]):
    # growing frames
    maxFrame = 300
    bpy.context.scene.frame_end = maxFrame
    step = 2
    for f in range(0, maxFrame, step):
        for bubble in lstBubble:
            if bubble.location[2] + bubble.scale[0] >= 200 :
                bubble.scale *= 0
                bubble.keyframe_insert('scale', frame=f-step)
                bubble.keyframe_insert('location', frame=f-step)
            else:
                bubble.scale *= 1 + 0.002 * step
                bubble.location[2] *= 1 + 0.02 * step
                bubble.keyframe_insert('location', frame=f)
                bubble.keyframe_insert('scale', frame=f)
            """for b in lstBubble:
                if b != bubble:
                    if isToClose(b, bubble):
                        b.scale*=0.90
                        bubble.scale*=1.05
                        bubble.keyframe_insert('scale', frame=f)"""

def isBiggerBubble(b1,b2):
    return b1 if b1.scale > b2.scale else b2


# Not use yet
def createTentacle(nbCube=7, firstCubeSize=3, lastCubeSize=0.5, firstColor=[1,1,1,1], lastColor=[0,0,0,1], eulerAngle=[0,0,0]):
    offset = firstCubeSize/2
    parent = None
    for i in range (nbCube):
        #size
        size = firstCubeSize - (firstCubeSize - lastCubeSize)*i/(nbCube-1)
        #color
        color = firstColor
        for j in range(4):
            color[j] = firstColor[j] - (firstColor[j] - lastColor[j])*i/(nbCube-1)
        
        #color = [
        #    firstColor[j] - (firstColor[j] - lastColor[j])*i/(nbCube-1)
        #    for j in range(4)
        #]
        #angle
        
        #set
        bpy.ops.mesh.primitive_cube_add(size=size, location=(0, 0, size if i!=0 else size/2))
        cube = bpy.context.object
        cube.color = color
        if i != 0 :
            cube.rotation_euler = eulerAngle
            cube.parent = parent
        parent = cube
        offset = size

### above are functionnal methods description
### below are Panel and interaction button description


## PANEL definition
class MyBubblePanel(bpy.types.Panel):
    """Creates a Panel for generate Bubbles"""
    
    bl_label = "Bubble Panel"
    bl_idname = "OBJECT_PT_GenBubble"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bubble"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "bubble_count")
        layout.prop(context.scene, "bubble_size")
        layout.prop(context.scene, "bubble_range")
        row = layout.row()
        row.operator("object.bubble_reset")
        row.operator("object.bubble_generation")

## OPERATOR used as above descripbed panel button
class Destructor(bpy.types.Operator):
    bl_idname = "object.bubble_reset"
    bl_label = "Reset Scene"

    def execute(self, context):
        for i in range(len(object_list)):
            bubble = object_list[0]
            try:
                bpy.data.objects.remove(bubble)
                object_list.remove(bubble)
            except:
                pass
        return {'FINISHED'}

class BubbleBuilder(bpy.types.Operator):
    bl_idname = "object.bubble_generation"
    bl_label = "Generate"

    def execute(self, context):
        _scene = bpy.context.scene
        createBubble(_scene['bubble_count'], _scene['bubble_size'], _scene['bubble_range'])
        return {'FINISHED'}

def register():

    # Register a new scene property used for instanciate bubbles
    bpy.types.Scene.bubble_count = bpy.props.IntProperty(
        name="Instances",
        description="Nombre de bulles",
        min=1, max=1000,
        default=30,
    )
    bpy.types.Scene.bubble_size = bpy.props.FloatProperty(
        name="Radius",
        description="Rayon max d'une bulle",
        min=1, max=100,
        default=5,
    )
    bpy.types.Scene.bubble_range = bpy.props.FloatProperty(
        name="Range",
        description="Distance maximun du curseur",
        min=1, max=300,
        default=30,
    )
    # count, maxRadius, maxRange

    bpy.utils.register_class(MyBubblePanel)
    bpy.utils.register_class(Destructor)
    bpy.utils.register_class(BubbleBuilder)


if __name__ == "__main__":
    register()