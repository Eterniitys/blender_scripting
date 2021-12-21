import bpy
import random as rd
from math import cos, acos, sin, asin, sqrt, pi

gravitational_const : float = 6.67 * 10**(-11)


# Add a plane
"""
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0), scale=(1, 1, 1))
bpy.ops.rigidbody.object_add()
bpy.context.object.rigid_body.type = 'PASSIVE'
bpy.context.object.rigid_body.restitution = 0.8"""

object_list = []

print("\n"*10)

def debug(func):
    def wrapper(*args, **kwargs):
        print(f"# # # # # # # # #\n{func.__name__} have been call with {args}", end="")
        result = func(*args, **kwargs)
        print(f" and return {result}")
        return result
    return wrapper


class Sphere():
    velocity : tuple[float, float, float]
    mass = 1
    _massVol = 1_000_000
    _volume : int
    
    def __init__(self, volume : int, pos : tuple[int,int,int]):
        bpy.ops.mesh.primitive_uv_sphere_add()
        #bpy.ops.rigidbody.object_add()
        self.model = bpy.context.object
        
        self.model.location = bpy.context.scene.cursor.location.copy()
        self.model.location[0] += pos[0]
        self.model.location[1] += pos[1]
        self.model.location[2] += pos[2]
        
        self.set_volume(volume)
        self._init_volume = volume

        self.velocity = [0,0,0]
        self._set_initial_velocity(volume)

    
    def reset(self):
        """since I can't set keyframe on this value, i need to reset it when computing animation"""
        self.set_volume(self._init_volume)
        self.velocity = self._init_velocity
    

    def computeAttrationInduceBy(self, sphere : 'Sphere'):
        if self == sphere:
            return
        srqt_dist = self.sqrt_distance_to(sphere)
        if srqt_dist == 0:
            return
        distanceBetween = self.distance_to(sphere)
        force = ((gravitational_const * sphere.mass) / srqt_dist * sqrt(srqt_dist))

        self.velocity_add(tuple(map(lambda dist : dist * force, distanceBetween)))
    
    def set_pos(self, pos : tuple[int,int,int]):
        self.model.location[0] = pos[0]
        self.model.location[1] = pos[1]
        self.model.location[2] = pos[2]
    

    def move_by(self, vel : tuple[float, float, float]):
        self.model.location[0] += vel[0]
        self.model.location[1] += vel[1]
        self.model.location[2] += vel[2]
        return self.model.location

    def velocity_add(self, vector : tuple[float, float, float]):
        self.velocity[0] += vector[0]
        self.velocity[1] += vector[1]
        self.velocity[2] += vector[2]
        return self.velocity
        
    def _set_radius(self, radius):
        self.model.scale = [radius/2, radius/2, radius/2]
    
    def set_color(self, referenceValue):
        r = (self._volume - 1) / referenceValue
        b = 1 - (self._volume - 1) / referenceValue
        self.model.color = (r, 0, b, 1)
    
    def isToClose(self, sphere):
        if self == sphere:
            return
        return (sqrt(self.sqrt_distance_to(sphere)) < self.model.scale[0] + sphere.model.scale[0])

    def sqrt_distance_to(self, sphere):
        s1_x = self.model.location[0]
        s1_y = self.model.location[1]
        s1_z = self.model.location[2]
        s2_x = sphere.model.location[0]
        s2_y = sphere.model.location[1]
        s2_z = sphere.model.location[2]
        return (s1_x-s2_x)**2 + (s1_y-s2_y)**2 + (s1_z-s2_z)**2

    def distance_to(self, sphere):
        s1_x = self.model.location[0]
        s1_y = self.model.location[1]
        s1_z = self.model.location[2]
        s2_x = sphere.model.location[0]
        s2_y = sphere.model.location[1]
        s2_z = sphere.model.location[2]
        return((s2_x - s1_x), (s2_y - s1_y), (s2_z - s1_z))
    
    def _set_mass_from_volume(self, volume):
        self.mass = volume * self._massVol
        def radiusFromVolume(volume):
            return ((3*volume)/(4*pi))**(1/3)
        self._set_radius(radiusFromVolume(volume))

    def _set_initial_velocity(self, volume):
        relative_pos = bpy.context.scene.cursor.location.copy()
        relative_pos[0] -= self.model.location[0]
        relative_pos[1] -= self.model.location[1]
        generated_velocity : double = rd.random()* 10 * volume / sqrt(relative_pos[0]**2 + relative_pos[1]**2)
        if(relative_pos[0] >= 0):
            self.velocity[1] = generated_velocity
        else:
            self.velocity[1] = -generated_velocity
        if(relative_pos[1] >= 0):
            self.velocity[0] = -generated_velocity
        else:
            self.velocity[0] = generated_velocity
        self.velocity[2] = rd.random() * 0.5 - 0.5 
        
        self._init_velocity = self.velocity

    def set_volume(self, volume):
        self._volume = volume
        self._set_mass_from_volume(volume)

    def fuse_with(self, sphere):
        s1 = self
        s2 = sphere
        if s1._volume < s2._volume:
            s1, s2 = s2, s1
        s1.set_volume(self._volume + sphere._volume)
        s1.velocity = list(v * 0.8 for v in s1.velocity)
        s2.set_volume(0)
        s2.set_pos((0, 0, 0))

    def delete(self):
        bpy.data.objects.remove(self.model)

    def __repr__(self):
        return f"Sphere : [pos:{self.model.location}]"

def createSphere(count, maxVolume, maxRange):

    for i in range(count):    
        progress : int = round((i/count) * 20)
        sphere = generateGrowingSphere(maxVolume, maxRange, object_list)
        if sphere:
            object_list.append(sphere)
            print(f"Sphere generation: [{'|'*(progress)}{' '*(20-progress)}] , {i+1}/{count}", end="\r")
    print("\n"+str(len(object_list)) + " Spheres on été générée")
            
def generateGrowingSphere(maxVolume, maxRange, lstSphere = []):
    _maxTry = 100
    _inc = 0
    new_sphere = placeSphere(maxVolume, maxRange)
    if len(lstSphere) != 0 :
        isValide = False
        while not isValide and _inc < _maxTry:
            isValide = True
            for sphere in lstSphere:
                if new_sphere.isToClose(sphere):
                    isValide = False
                    new_sphere = placeSphere(maxVolume, maxRange, new_sphere)
                    _inc += 1
                    break
    new_sphere.set_color(maxVolume)
    if _inc >= _maxTry:
        bpy.ops.object.delete()
        new_sphere = None
    return new_sphere

def placeSphere(maxWeight, maxRange, sphere = None):
    _volume = rd.random() * (maxWeight - 1) + 1
    _angle = rd.random() * 2 * pi
    _dist = rd.random() * maxRange
    _x = sin(_angle) * _dist
    _y = cos(_angle) * _dist
    
    if sphere == None:
        sphere = Sphere(_volume, (_x, _y ,0))
    else:
        sphere.set_pos((_x, _y, 0))
        sphere.set_volume(_volume)
        
    return sphere

def animateSphere(lstSphere=[]):
    list_alive_sphere = lstSphere.copy()
    maxFrame = bpy.context.scene.maxFrame
    bpy.context.scene.frame_end = maxFrame
    step = 1
    for frame in range(0, maxFrame, step):
        frame_progress : int = round((frame/maxFrame) * 20)
        bar1 = f"Sphere animation: [{'|'*(frame_progress)}{' '*(20-frame_progress)}]"
        list_dead_sphere = []
        for i, sphere in enumerate(list_alive_sphere):
            if frame == 0:
                sphere.reset()
            alive_progress : int = round((i+1)/len(list_alive_sphere) * 20)
            bar2 = f"{bar1}[{'|'*(alive_progress)}{' '*(20-alive_progress)}]"
            if sphere._volume == 0:
                list_dead_sphere.append(sphere)
                continue
            sphere.model.keyframe_insert('scale', frame=frame)
            for j, other_sphere in enumerate(list_alive_sphere):
                others_progress : int = round(((j+1)/len(list_alive_sphere)) * 20)
                print(f"{bar2}[{'|'*(others_progress)}{' '*(20-others_progress)}] {frame+1}/{maxFrame} {len(list_alive_sphere)}>{j+1}>{i+1}", ' '*5, end="\r")
                if sphere.isToClose(other_sphere):
                    sphere.fuse_with(other_sphere)
                    sphere.model.keyframe_insert('scale', frame=frame)
                    other_sphere.model.keyframe_insert('scale', frame=frame)
                    sphere.model.keyframe_insert('location', frame=frame)
                    other_sphere.model.keyframe_insert('location', frame=frame)

                sphere.computeAttrationInduceBy(other_sphere)
                
            sphere.model.keyframe_insert('location', frame=frame)
            sphere.move_by(sphere.velocity)
        for sphere in list_dead_sphere:
            list_alive_sphere.remove(sphere)
    print()

### above are functionnal methods description
### below are Panel and interaction button description


## PANEL definition
class MySpherePanel(bpy.types.Panel):
    """Creates a Panel for generate Spheres"""
    
    #bl_label = "Sphere Panel"
    bl_label = "Johan Guerrero Panel"
    bl_idname = "OBJECT_PT_GenSphere"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "cnam"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "sphere_count")
        layout.prop(context.scene, "sphere_size")
        layout.prop(context.scene, "sphere_range")
        row = layout.row()
        row.operator("object.sphere_generation")
        row.operator("object.sphere_reset")
        #layout.operator("object.sphere_validate")
        
        layout.prop(context.scene, "maxFrame")
        layout.operator("object.sphere_animation")

## OPERATOR used in above descripted panel
class Destructor(bpy.types.Operator):
    bl_idname = "object.sphere_reset"
    bl_label = "Reset Sphere"

    def execute(self, context):
        for i in range(len(object_list)):
            sphere = object_list[0]
            object_list.remove(sphere)
            sphere.delete()
        return {'FINISHED'}

class SphereBuilder(bpy.types.Operator):
    bl_idname = "object.sphere_generation"
    bl_label = "Generate"

    def execute(self, context):
        _scene = bpy.context.scene
        createSphere(_scene['sphere_count'], _scene['sphere_size'], _scene['sphere_range'])
        return {'FINISHED'}

class SphereAnimator(bpy.types.Operator):
    bl_idname = "object.sphere_animation"
    bl_label = "Animate"

    def execute(self, context):
        for sphere in bpy.data.objects:
            sphere.animation_data_clear()
        animateSphere(object_list)
        return {'FINISHED'}

def register():

    # Register a new scene property used for instanciate spheres
    bpy.types.Scene.sphere_count = bpy.props.IntProperty(
        name="Instances",
        description="Nombre de spheres",
        min=1, max=1000,
        default=30,
    )
    bpy.types.Scene.sphere_size = bpy.props.FloatProperty(
        name="Volume",
        description="Volume maximun d'une sphere",
        min=1, max=100,
        default=5,
    )
    bpy.types.Scene.sphere_range = bpy.props.FloatProperty(
        name="Range",
        description="Distance maximun du curseur",
        min=1, max=1000,
        default=30,
    )
    bpy.types.Scene.maxFrame = bpy.props.IntProperty(
        name="Frame count",
        description="Nombre de frame maximum",
        min=1, max=10000,
        default=1000,
    )
    # count, maxVolume, maxRange

    bpy.context.scene.sphere_count = 50
    bpy.context.scene.sphere_size = 30
    bpy.context.scene.sphere_range = 200
    bpy.context.scene.maxFrame = 500

    bpy.utils.register_class(MySpherePanel)
    bpy.utils.register_class(Destructor)
    bpy.utils.register_class(SphereBuilder)
    bpy.utils.register_class(SphereAnimator)

if __name__ == "__main__":
    register()
