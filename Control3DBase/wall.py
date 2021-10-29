from Base3DObjects import Vector

class Wall:

    def __init__(self, translation: Vector, scale: Vector):
        self.translation = translation
        self.scale = scale
        self.color = (1.0, 1.0, 1.0)

        self.min_x = self.translation.x - (self.scale.x)/2
        self.max_x = self.translation.x + (self.scale.x)/2
        self.min_z = self.translation.z - (self.scale.z)/2
        self.max_z = self.translation.z + (self.scale.z)/2


    def draw(self, shader, model_matrix, drawable):
        model_matrix.push_matrix()
        model_matrix.add_translation(self.translation.x, self.translation.y, self.translation.z)
        model_matrix.add_scale(self.scale.x, self.scale.y, self.scale.z)
        shader.set_model_matrix(model_matrix.matrix)
        shader.set_material_diffuse(*self.color)
        drawable.set_verticies(shader)
        drawable.draw()
        model_matrix.pop_matrix()
    