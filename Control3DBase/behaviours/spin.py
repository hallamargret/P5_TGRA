class Spin(): # Spins around the y axes

    def __init__(self, game_object):
        self.game_object = game_object
    
    def update(self, delta_time):
        self.game_object.rotation.y += delta_time