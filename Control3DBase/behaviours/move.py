class MoveOnZ(): # Moves on the z axis

    def __init__(self, game_object, lowest_z, highest_z):
        self.game_object = game_object
        self.going_down = True
        self.lowest_z = lowest_z
        self.highest_z = highest_z
    
    def update(self, delta_time):
        if self.going_down and self.game_object.min_z > self.lowest_z:
            self.game_object.translation.z -= delta_time
        elif self.going_down and self.game_object.min_z <= self.lowest_z:
            self.going_down = False
            self.game_object.translation.z += delta_time
        else:
            if self.game_object.max_z < self.highest_z:
                self.game_object.translation.z += delta_time
            else:
                self.going_down = True
                self.game_object.translation.z -= delta_time

class MoveOnX(): # Moves on the x axis

    def __init__(self, game_object, lowest_x, highest_x):
        self.game_object = game_object
        self.going_down = True
        self.lowest_x = lowest_x
        self.highest_x = highest_x
    
    def update(self, delta_time):
        if self.going_down and self.game_object.min_x > self.lowest_x:
            self.game_object.translation.x -= delta_time
        elif self.going_down and self.game_object.min_x <= self.lowest_x:
            self.going_down = False
            self.game_object.translation.x += delta_time
        else:
            if self.game_object.max_x < self.highest_x:
                self.game_object.translation.x += delta_time
            else:
                self.going_down = True
                self.game_object.translation.x -= delta_time