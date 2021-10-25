from Base3DObjects import Vector

class GameObject:

    def __init__(self, drawable, shader, model_matrix, translation: Vector, rotation: Vector, scale: Vector, color):
        self.drawable = drawable
        self.shader = shader
        self.model_matrix = model_matrix
        self.translation = translation
        self.rotation = rotation
        self.scale = scale
        self.color = color
        self.behaviors = []

        self.min_x = self.translation.x - (self.scale.x)/2
        self.max_x = self.translation.x + (self.scale.x)/2
        self.min_z = self.translation.z - (self.scale.z)/2
        self.max_z = self.translation.z + (self.scale.z)/2

    def draw(self):
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(self.translation.x, self.translation.y, self.translation.z)  ### --- ADD PROPER TRANSFORMATION OPERATIONS --- ###
        self.model_matrix.add_rotate_x(self.rotation.x)
        self.model_matrix.add_rotate_y(self.rotation.y)
        self.model_matrix.add_rotate_z(self.rotation.z)
        self.model_matrix.add_scale(self.scale.x, self.scale.y, self.scale.z)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.shader.set_material_diffuse(*self.color)
        self.drawable.set_verticies(self.shader)
        self.drawable.draw()
        self.model_matrix.pop_matrix()
    
    def update(self, delta_time):
        self.min_x = self.translation.x - (self.scale.x)/2
        self.max_x = self.translation.x + (self.scale.x)/2
        self.min_z = self.translation.z - (self.scale.z)/2
        self.max_z = self.translation.z + (self.scale.z)/2
        for behavior in self.behaviors:
            behavior.update(delta_time)
    
    def add_behavior(self, behavior_instance):
        self.behaviors.append(behavior_instance)
