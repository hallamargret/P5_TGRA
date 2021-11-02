from Base3DObjects import Vector

class GameObject:

    def __init__(self, translation: Vector, rotation: Vector, scale: Vector, color):
        self.translation = translation
        self.rotation = rotation
        self.scale = scale
        self.color = Color(color[0], color[1], color[2])
        self.behaviors = []

        self.min_x = self.translation.x - (self.scale.x)/2
        self.max_x = self.translation.x + (self.scale.x)/2
        self.min_z = self.translation.z - (self.scale.z)/2
        self.max_z = self.translation.z + (self.scale.z)/2

    def draw(self, drawable, shader, model_matrix):
        model_matrix.push_matrix()
        model_matrix.add_translation(self.translation.x, self.translation.y, self.translation.z)  ### --- ADD PROPER TRANSFORMATION OPERATIONS --- ###
        model_matrix.add_rotate_x(self.rotation.x)
        model_matrix.add_rotate_y(self.rotation.y)
        model_matrix.add_rotate_z(self.rotation.z)
        model_matrix.add_scale(self.scale.x, self.scale.y, self.scale.z)
        shader.set_model_matrix(model_matrix.matrix)
        shader.set_material_diffuse(self.color)
        drawable.set_verticies(shader)
        drawable.draw()
        model_matrix.pop_matrix()
    
    def update(self, delta_time):
        self.min_x = self.translation.x - (self.scale.x)/2
        self.max_x = self.translation.x + (self.scale.x)/2
        self.min_z = self.translation.z - (self.scale.z)/2
        self.max_z = self.translation.z + (self.scale.z)/2
        for behavior in self.behaviors:
            behavior.update(delta_time)
    
    def add_behavior(self, behavior_instance):
        self.behaviors.append(behavior_instance)

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

