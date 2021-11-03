
import pygame
from pygame.locals import *

import sys
import time

from Shaders import *
from Matrices import *

from GameObject import GameObject
from wall import Wall
from behaviours.spin import Spin

from behaviours.move import MoveOnX
from behaviours.move import MoveOnZ

import ojb_3D_loading

class GraphicsProgram3D:
    def __init__(self):

        pygame.init() 
        pygame.display.set_mode((1000,750), pygame.OPENGL|pygame.DOUBLEBUF)

        self.shader = Shader3D()
        self.shader.use()

        self.model_matrix = ModelMatrix()

        self.view_matrix_player1 = ViewMatrix()
        self.view_matrix_player2 = ViewMatrix()
        # We start in point 1,1,1 and look at the point in front of us 2,1,2
        self.view_matrix_player1.look(Point(7, 2, 23.0), Point(7, 2, 25.0), Vector(0, 1, 0)) # Player 1
        self.view_matrix_player2.look(Point(3, 2, 23.0), Point(3, 2, 25.0), Vector(0, 1, 0)) # Player 2

        self.overview_matrix = ViewMatrix()
        # overview mode, when o is pressed on the keyboard we see the maze from above in point 10,25,10 which is straight up from the middle of the maze
        self.overview_matrix.look(Point(10, 25, 10), Point(11, 1, 10), Vector(0, 1, 0))

        self.wall_height = 6
        self.track_size = 50

        self.car_height = 2.0

        self.near_plane = 0.3
        self.far_plane = 100
        self.x_walls = []
        self.z_walls = []
        self.inner_walls = []
        self.floor = GameObject(Vector(self.track_size/2, 0, self.track_size/2), Vector(0.0, 0.0, 0.0), Vector(self.track_size, 0.8, self.track_size), (0.39, 0.40, 0.42))
        self.winning_screen_base = GameObject(Vector(10, 0, 10), Vector(0.0, 0.0, 0.0), Vector(20, 0.8, 20), (0.39, 0.40, 0.42))
        self.radius = 1.5
        
        
        self.projection_matrix = ProjectionMatrix()
        self.fov = pi/2
        self.projection_matrix.set_perspective((self.fov), (1000 / 750), self.near_plane, self.far_plane)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.cube = Cube()
        self.obj_model = ojb_3D_loading.load_obj_file(sys.path[0] + "/models", "cloud.obj")

        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.pitch_angle = 0

        self.angle = 0

        self.UP_key_down = False  ## CONTROLS FOR KEYS TO CONTROL THE CAMERA
        self.DOWN_key_down = False
        self.LEFT_key_down = False
        self.RIGHT_key_down = False
        self.W_key_down = False
        self.A_key_down = False
        self.S_key_down = False
        self.D_key_down = False
        self.T_key_down = False
        self.G_key_down = False
        self.overview = False   # View the maze from above
        # The flashlight is turned off to begin with, to turn it on and off press space
        self.flashlight = False
        self.map = True     #little viewport to see a map in the upper right corner, to turn on and off press p
    
        self.car_1 = GameObject(Vector(self.view_matrix_player1.eye.x, self.car_height/2, self.view_matrix_player1.eye.z), Vector(0,0,0), Vector(1.5, self.car_height, 3.0), (1,0,0))
        self.car_2 = GameObject(Vector(self.view_matrix_player2.eye.x, self.car_height/2, self.view_matrix_player2.eye.z), Vector(0,0,0), Vector(1.5, self.car_height, 3.0), (0,0,1))

        # Cubes that are moving in the maze, the player will collide on them, set as hindrance
        moving_cube_1 = GameObject(Vector(25.0, 15.0, 2.0), Vector(0.0, 0.0, 0.0), Vector(1.0, 1.0, 1.0), (1.0, 0.0, 0.0))
        moving_cube_2 = GameObject(Vector(25.0, 15.0, 40.0), Vector(0.0, 0.0, 0.0), Vector(1.0, 1.0, 1.0), (1.0, 0.0, 0.0))
    

        self.moving_cubes = [moving_cube_1, moving_cube_2]

        # Player should try to collect all of the end cubes, when all are collected the player will win the game
        end_cube_1 = GameObject(Vector(18.0, 1.0, 18.0), Vector(0.0, 0.0, 0.0), Vector(1.0, 1.0, 1.0), (1.0, 0.0, 1.0))

        self.current_end_cube = 0

        self.end_cubes = [end_cube_1]

        self.finish_line_cube = GameObject(Vector(5.0, 0.0, 25.0), Vector(0.0, 0.0, 0.0), Vector(10.0, 0.81, 2.0), (1.0, 1.0, 1.0))
        self.arrow_cube_1 = GameObject(Vector(25.0, 0.0, 45.0), Vector(0.0, 0.0, 0.0), Vector(5.0, 0.81, 2.0), (0.40, 0.41, 0.43))
        self.arrow_cube_2 = GameObject(Vector(45.0, 0.0, 25.0), Vector(0.0, 0.0, 0.0), Vector(2.0, 0.81, 5.0), (0.40, 0.41, 0.43))
        self.arrow_cube_3 = GameObject(Vector(25.0, 0.0, 5.0), Vector(0.0, 0.0, 0.0), Vector(5.0, 0.81, 2.0), (0.40, 0.41, 0.43))

        for cube in self.end_cubes:
            cube.add_behavior(Spin(cube))

        self.add_walls()
        
        self.victory_letters = []

        self.p1_has_won = False
        self.p2_has_won = False

        self.p1_lap_counter = 0
        self.p2_lap_counter = 0

        self.texture_id01 = self.load_texture(sys.path[0] + "/images/crowd.png")
        self.texture_id02 = self.load_texture_rotate(sys.path[0] +"/images/crowd.png", -90)
        self.texture_id03 = self.load_texture_rotate(sys.path[0] + "/images/finish_line.png", -90)
        self.texture_id04 = self.load_texture(sys.path[0] + "/images/White_Arrow.png")
        self.texture_id05 = self.load_texture_rotate(sys.path[0] + "/images/White_Arrow.png", -90)
        self.texture_id06 = self.load_texture_rotate(sys.path[0] + "/images/White_Arrow.png", 90)


        self.line_crossed_p1 = True
        self.line_crossed_p2 = True
        self.round_p1 = 0
        self.round_p2 = 0


    def load_texture(self, path_str):
        surface = pygame.image.load(path_str)
        tex_string = pygame.image.tostring(surface, "RGBA", 1)
        width = surface.get_width()
        height = surface.get_height()
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_string)
        return tex_id
    
    def load_texture_rotate(self, path_str, degr):
        image = pygame.image.load(path_str)
        surface = pygame.transform.rotate(image, degr)
        tex_string = pygame.image.tostring(surface, "RGBA", 1)
        width = surface.get_width()
        height = surface.get_height()
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_string)
        return tex_id

    def add_walls(self):
        # #big walls
        self.z_walls.append(Wall(Vector((self.track_size - self.track_size/4), (self.wall_height/2), self.track_size), Vector(self.track_size/2, self.wall_height, 0.8)))
        self.z_walls.append(Wall(Vector((self.track_size - self.track_size/4), (self.wall_height/2), 0), Vector(self.track_size/2, self.wall_height, 0.8)))
        self.x_walls.append(Wall(Vector(0, (self.wall_height/2), (self.track_size - self.track_size/4)), Vector(0.8, self.wall_height, self.track_size/2)))
        self.x_walls.append(Wall(Vector(self.track_size, (self.wall_height/2), (self.track_size - self.track_size/4)), Vector(0.8, self.wall_height, self.track_size/2)))

        self.z_walls.append(Wall(Vector(self.track_size/4, (self.wall_height/2), self.track_size), Vector(self.track_size/2, self.wall_height, 0.8)))
        self.z_walls.append(Wall(Vector(self.track_size/4, (self.wall_height/2), 0), Vector(self.track_size/2, self.wall_height, 0.8)))
        self.x_walls.append(Wall(Vector(0, (self.wall_height/2), self.track_size/4), Vector(0.8, self.wall_height, self.track_size/2)))
        self.x_walls.append(Wall(Vector(self.track_size, (self.wall_height/2), self.track_size/4), Vector(0.8, self.wall_height, self.track_size/2)))

        # Inner walls
        self.inner_walls.append(Wall(Vector(10, (self.wall_height/8), 25), Vector(0.2, self.wall_height/2, 30), (0.753, 0.753, 0.753)))
        self.inner_walls.append(Wall(Vector(40, (self.wall_height/8), 25), Vector(0.2, self.wall_height/2, 30), (0.753, 0.753, 0.753)))
        self.inner_walls.append(Wall(Vector(25, (self.wall_height/8), 40), Vector(30, self.wall_height/2, 0.2), (0.753, 0.753, 0.753)))
        self.inner_walls.append(Wall(Vector(25, (self.wall_height/8), 10), Vector(30, self.wall_height/2, 0.2), (0.753, 0.753, 0.753)))

    
    '''Check if the player is colliding any walls or objects, if so it will handle it so the player will slide among the wall/object but not walk througt it'''
    def check_collision(self, wall, view_matrix):
        # check if the eye is to close to the wall (for every wall)
        if wall.min_x <= view_matrix.eye.x <= wall.max_x:
            # right side of the wall
            if view_matrix.eye.z >= wall.max_z:
                if (view_matrix.eye.z - wall.max_z) <= self.radius:
                    view_matrix.eye.z = wall.max_z + self.radius
            # left side of the wall
            elif view_matrix.eye.z <= wall.min_z:
                if (wall.min_z - view_matrix.eye.z) <= self.radius:
                    view_matrix.eye.z = wall.min_z - self.radius
            
        elif wall.min_z <= view_matrix.eye.z <= wall.max_z:
            # right side of the wall
            if view_matrix.eye.x >= wall.max_x:
                if (view_matrix.eye.x - wall.max_x) <= self.radius:
                    view_matrix.eye.x = wall.max_x + self.radius
            # left side of the wall
            elif view_matrix.eye.x <= wall.min_x:
                if (wall.min_x - view_matrix.eye.x) <= self.radius:
                    view_matrix.eye.x = wall.min_x - self.radius
        
        else: # Check corners
            upper_left_corner = Point(wall.min_x, 1, wall.max_z)
            upper_right_corner = Point(wall.max_x, 1, wall.max_z)
            lower_left_corner = Point(wall.min_x, 1, wall.min_z)
            lower_right_corner = Point(wall.max_x, 1, wall.min_z)
            upper_left_dist = view_matrix.eye - upper_left_corner # Upper left corner
            if upper_left_dist.__len__() < self.radius:
                upper_left_dist.normalize()
                new_dist = upper_left_dist * self.radius # Set the length of distance vector to the length of the radius
                view_matrix.eye = upper_left_corner + new_dist
            upper_right_dist = view_matrix.eye - upper_right_corner # Upper right corner
            if upper_right_dist.__len__() < self.radius:
                upper_right_dist.normalize()
                new_dist = upper_right_dist * self.radius # Set the length of distance vector to the length of the radius
                view_matrix.eye = upper_right_corner + new_dist
            lower_left_dist = view_matrix.eye - lower_left_corner # lower left corner
            if lower_left_dist.__len__() < self.radius:
                lower_left_dist.normalize()
                new_dist = lower_left_dist * self.radius # Set the length of distance vector to the length of the radius
                view_matrix.eye = lower_left_corner + new_dist
            lower_right_dist = view_matrix.eye - lower_right_corner # Lower right corner
            if lower_right_dist.__len__() < self.radius:
                lower_right_dist.normalize()
                new_dist = lower_right_dist * self.radius # Set the length of distance vector to the length of the radius
                view_matrix.eye = lower_right_corner + new_dist

    def check_moving_cube_collision(self):
        for cube in self.moving_cubes:
            self.check_collision(cube, self.view_matrix_player1)
            self.check_collision(cube, self.view_matrix_player2)


    def check_finish_line(self, view_matrix, player):
        if 0 <= view_matrix.eye.x <= 10:
            if view_matrix.eye.z < 25:
                if player == 1:
                    self.line_crossed_p1 = False
                else:
                    self.line_crossed_p2 = False
            if view_matrix.eye.z >= 25:
                if player == 1:
                    if self.line_crossed_p1 == False:
                        self.line_crossed_p1 = True
                        if self.round_p1 < 2:
                            self.round_p1 += 1
                        else:
                            self.p1_has_won = True
                else:
                    if self.line_crossed_p2 == False:
                        print(f"Player 2 eye z is {view_matrix.eye.z}")
                        print(f"Line crossed p2 is now {self.line_crossed_p2}")
                        self.line_crossed_p2 = True
                        print(f"Line crossed p2 is now {self.line_crossed_p2}")
                        if self.round_p2 < 2:
                            self.round_p2 += 1
                        else:
                            self.p2_has_won = True
                



    

    def update(self):
        delta_time = self.clock.tick() / 1000.0

        self.angle += pi * delta_time

        if not self.overview:
            if self.W_key_down:
                self.view_matrix_player1.slide_on_floor(0, -4 * delta_time)
            if self.S_key_down:
                self.view_matrix_player1.slide_on_floor(0, 4 * delta_time)
            if self.A_key_down:
                self.view_matrix_player1.yaw_on_floor(pi * delta_time)
                self.car_1.rotation.y += pi * delta_time
            if self.D_key_down:
                self.view_matrix_player1.yaw_on_floor(-pi * delta_time)
                self.car_1.rotation.y += -pi * delta_time


            if self.T_key_down:
                self.fov -= 0.1 * delta_time
            if self.G_key_down:
                self.fov += 0.1 * delta_time

            if self.UP_key_down:
                self.view_matrix_player2.slide_on_floor(0, -4 * delta_time)
            if self.DOWN_key_down:
                self.view_matrix_player2.slide_on_floor(0, 4 * delta_time)
            if self.LEFT_key_down:
                self.view_matrix_player2.yaw_on_floor(pi * delta_time)
                self.car_2.rotation.y += pi * delta_time
            if self.RIGHT_key_down:
                self.view_matrix_player2.yaw_on_floor(-pi * delta_time)
                self.car_2.rotation.y += -pi * delta_time

        self.end_cubes[self.current_end_cube].update(delta_time)

        for cube in self.moving_cubes:
            cube.update(delta_time)


        for wall in self.x_walls:
            self.check_collision(wall, self.view_matrix_player1)
            self.check_collision(wall, self.view_matrix_player2)
        
        for wall in self.z_walls:
            self.check_collision(wall, self.view_matrix_player1)
            self.check_collision(wall, self.view_matrix_player2)
        
        for wall in self.inner_walls:
            self.check_collision(wall, self.view_matrix_player1)
            self.check_collision(wall, self.view_matrix_player2)


        self.car_1.translation = Vector(self.view_matrix_player1.eye.x, self.car_height/2, self.view_matrix_player1.eye.z)
        self.car_2.translation = Vector(self.view_matrix_player2.eye.x, self.car_height/2, self.view_matrix_player2.eye.z)

        self.check_collision(self.car_1, self.view_matrix_player2)
        self.check_collision(self.car_2, self.view_matrix_player1)

        self.check_finish_line(self.view_matrix_player1, 1)
        self.check_finish_line(self.view_matrix_player2, 2)
        print(f"Player 1 has finished {self.round_p1} rounds!")
        print(f"Player 2 has finished {self.round_p2} rounds!")
    

    def display_player(self, view_matrix, player):
        self.shader.set_view_matrix(view_matrix.get_matrix())
        self.shader.set_eye_position(view_matrix.eye)
        #print(f"Player {player}, is at eye position {view_matrix.eye}")

        # first light  (positional)
        #self.shader.set_light_pos_diff_spec(0, Point(25, 40, 25), (0.8, 0.8, 0.8), (0.2, 0.2, 0.2), 1.0)
        # self.shader.set_light_position(Point(25, 25, 25))
        # self.shader.set_light_diffuse(0.8, 0.8, 0.8)
        # self.shader.set_light_specular(0.4, 0.4, 0.4)
        
        # # second light (direcionsl)
        self.shader.set_light_pos_diff_spec(1, Vector(1, 0, 0), (1.0, 1.0, 1.0), (0.2, 0.2, 0.2), 0.0)

        self.shader.set_light_pos_diff_spec(2, Vector(0, 0, 1), (1.0, 1.0, 1.0), (0.2, 0.2, 0.2), 0.0)

        self.shader.set_light_pos_diff_spec(0, Vector(0, 0, -1), (1.0, 1.0, 1.0), (0.2, 0.2, 0.2), 0.0)

        self.shader.set_light_pos_diff_spec(3, Vector(-1, 0, 0), (1.0, 1.0, 1.0), (0.2, 0.2, 0.2), 0.0)

        
        self.shader.set_light_pos_diff_spec(4, Vector(0, 1, 0), (1.0, 1.0, 1.0), (0.2, 0.2, 0.2), 0.0)
        
        # # third light (positional)
        # self.shader.set_light_pos_diff_spec(2, Point(5, 40, 25), (0.8, 0.8, 0.8), (0.2, 0.2, 0.2), 1.0)
        
        # # fourth light (positional)
        # self.shader.set_light_pos_diff_spec(3, Point(45, 40, 25), (0.8, 0.8, 0.8), (0.2, 0.2, 0.2), 1.0)

        # # fifth light
        # self.shader.set_light_pos_diff_spec(4, Point(25, 40, 5), (0.8, 0.8, 0.8), (0.2, 0.2, 0.2), 1.0)

        # fifth light, flashlight (directional). Turned on when space has been pressed, turns off when space is pressed again.
        # if self.flashlight:
        #     self.shader.set_light_pos_diff_spec(4, view_matrix.n, (0.5, 0.5, 0.1), (0.3, 0.3, 0.3), 0.0)
        # else:
        #     self.shader.set_light_pos_diff_spec(4, view_matrix.n, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.0)

        # fifth light directional fixed position not used but can be replaced for the flashlight (or added to the list but then need some modifycations in the simple3D.vert file)
        #self.shader.set_light_pos_diff_spec(4, Point(1, 1, 1), (0.6, 0.6, 0.6), (0.5, 0.5, 0.5), 0.0)

        self.shader.set_material_specular(Color(0.75, 0.75, 0.75))
        self.shader.set_material_shininess(30)
        self.model_matrix.load_identity()

        self.floor.draw(self.cube, self.shader, self.model_matrix)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id03)
        self.shader.set_diffuse_tex(0)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id03)
        self.shader.set_spec_tex(1)
        self.shader.set_using_texture(1.0)

        self.finish_line_cube.draw(self.cube, self.shader, self.model_matrix)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id05)
        self.shader.set_diffuse_tex(0)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id05)
    
        self.arrow_cube_1.draw(self.cube, self.shader, self.model_matrix)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id04)
        self.shader.set_diffuse_tex(0)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id04)
        self.shader.set_spec_tex(1)
        
        self.arrow_cube_2.draw(self.cube, self.shader, self.model_matrix)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id06)
        self.shader.set_diffuse_tex(0)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id06)
        self.shader.set_spec_tex(1)

        self.arrow_cube_3.draw(self.cube, self.shader, self.model_matrix)
    

        # Walls of the maze

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id02)
        self.shader.set_diffuse_tex(0)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id02)
        self.shader.set_spec_tex(1)
        self.shader.set_using_texture(1.0)
        

        for wall in self.x_walls:
            wall.draw(self.shader, self.model_matrix, self.cube)

        #self.obj_model.draw(self.shader)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id01)
        self.shader.set_diffuse_tex(0)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id01)
        self.shader.set_spec_tex(1)

        for wall in self.z_walls:
            wall.draw(self.shader, self.model_matrix, self.cube)
        
        self.shader.set_using_texture(0.0)

        for wall in self.inner_walls:
            wall.draw(self.shader, self.model_matrix, self.cube)



        self.end_cubes[self.current_end_cube].draw(self.cube, self.shader, self.model_matrix)
        

        # for cube in self.moving_cubes:
        #     cube.scale = Vector(0.5, 0.5,0.5)
        #     cube.draw(self.cube, self.shader, self.model_matrix)

        #     self.model_matrix.push_matrix()
        #     self.model_matrix.add_translation(cube.translation.x, cube.translation.y, cube.translation.z)  ### --- ADD PROPER TRANSFORMATION OPERATIONS --- ###
        #     # self.model_matrix.add_translation(cube.translation.x, cube.translation.y, cube.translation.z)
        #     # self.model_matrix.add_rotate_x(cube.rotation.x)
        #     # self.model_matrix.add_rotate_y(cube.rotation.y)
        #     # self.model_matrix.add_rotate_z(cube.rotation.z)
        #     self.model_matrix.add_scale(100, 100, 100)
        #     self.shader.set_model_matrix(self.model_matrix.matrix)
        #   #self.shader.set_material_diffuse(self.color)
        #     #self.obj_model.set_verticies(self.shader)
        #     self.obj_model.draw(self.shader)
        #     self.model_matrix.pop_matrix()

            #self.obj_model.draw(self.shader)

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(25.0, 15.0, 5.0)
        self.model_matrix.add_scale(0.01, 0.01, 0.01)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        #self.obj_model.set_mesh_material()
        cloud_material = Material(Color(1.0,1.0,1.0), Color(0.5,0.5,0.5), 0.7)
        self.obj_model.add_material(58, cloud_material)
        self.obj_model.material_key_test(58)
        #self.obj_model.set_mesh_material()
        self.obj_model.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(25.0, 15.0, 45.0)
        self.model_matrix.add_scale(0.01, 0.01, 0.01)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        #self.obj_model.set_mesh_material()
        self.obj_model.draw(self.shader)
        self.model_matrix.pop_matrix()

            

        if player == 1:
            self.car_2.draw(self.cube, self.shader, self.model_matrix)
        else:
            self.car_1.draw(self.cube, self.shader, self.model_matrix)
        
        
        
        


        #little map of the maze in another smaller viewport, displays in the upper right corner. Turn off and on with the letter p on keyboard
        # if self.map:
        #     glViewport(750, 400, 250, 200)
        #     glClear(GL_DEPTH_BUFFER_BIT)
        #     self.shader.set_view_matrix(self.overview_matrix.get_matrix())
        #     self.shader.set_eye_position(self.overview_matrix.eye)

        #     # The maze floor in the little map
        #     color = [0.2, 0.1, 0.7]
        #     translation_list = [self.track_size/2, 0, self.track_size/2]
        #     scale_list = [self.track_size, 0.8, self.track_size]
        #     self.draw_maze_floor(color, translation_list, scale_list)

        #     # Mazes walls in the little map
        #     for wall in self.walls:
        #         wall.draw(self.shader, self.model_matrix, self.cube)

        #     self.end_cubes[self.current_end_cube].draw()

        #     for cube in self.moving_cubes:
        #         cube.draw()

    

    def display(self):
        glEnable(GL_DEPTH_TEST)

        glClearColor(0.0, 0.2, 0.8, 1.0)    #color of space (sky)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        self.shader.set_material_diffuse(Color(1.0, 1.0, 1.0))

        glViewport(0, 375, 1000, 375)

        # glActiveTexture(GL_TEXTURE0)
        # glBindTexture(GL_TEXTURE_2D, self.texture_id01)
        # self.shader.set_diffuse_tex(0)
        # glActiveTexture(GL_TEXTURE1)
        # glBindTexture(GL_TEXTURE_2D, self.texture_id01)
        # self.shader.set_spec_tex(1)


        self.projection_matrix.set_perspective((self.fov), (1000 / 750), self.near_plane, self.far_plane)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.display_player(self.view_matrix_player1, 1)

        # View the maze from above to see the whole maze. Not able to move while in overview mode, only look.
        if self.overview:
            self.shader.set_view_matrix(self.overview_matrix.get_matrix())
            self.shader.set_eye_position(self.overview_matrix.eye)
        # Game mode (first person view), viewing the matrix as the player. Move (walk forward, to the right, left and backwards) and look around for end cubes.
        # else:
        #     #player 1
        #     self.shader.set_view_matrix(self.view_matrix_player1.get_matrix())
        #     self.shader.set_eye_position(self.view_matrix_player1.eye)

        
        glViewport(0, 0, 1000, 375)
        # glActiveTexture(GL_TEXTURE0)
        # glBindTexture(GL_TEXTURE_2D, self.texture_id02)
        # self.shader.set_diffuse_tex(0)
        # glActiveTexture(GL_TEXTURE1)
        # glBindTexture(GL_TEXTURE_2D, self.texture_id02)
        # self.shader.set_spec_tex(1)

        self.projection_matrix.set_perspective((self.fov), (1000 / 750), self.near_plane, self.far_plane)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.display_player(self.view_matrix_player2, 2)


        

        pygame.display.flip()
    

    '''When the player has collected all four cubes then the player has won and the message "YOU WON" will display.
    Then when the player presses any key, the game will quit.'''
    def display_victory_screen(self):
        glEnable(GL_DEPTH_TEST)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glViewport(0, 0, 1000, 750)

        self.projection_matrix.set_perspective((self.fov), (1000 / 750), self.near_plane, self.far_plane)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.shader.set_view_matrix(self.overview_matrix.get_matrix())
        self.shader.set_eye_position(self.overview_matrix.eye)
        

        self.model_matrix.load_identity()

        self.winning_screen_base.draw(self.cube, self.shader, self.model_matrix)

        # color = [0.0, 0.0, 0.8]
        # translation_list = [self.track_size/2, 0, self.track_size/2]
        # scale_list = [self.track_size, 0.8, self.track_size]
        # self.draw_maze_floor(color, translation_list, scale_list)

        self.create_victory_letters()

        for object in self.victory_letters:
            object.draw(self.cube, self.shader, self.model_matrix)

        pygame.display.flip()

    def create_victory_letters(self):
        #Y
        # self.victory_letters.append(GameObject(Vector(16.5, 1, 3.5), Vector(0, pi/4, 0), Vector(3, 1, 1), (0.5, 0.0, 0.0)))
        # self.victory_letters.append(GameObject(Vector(14, 1, 4.5), Vector(0, 0, 0), Vector(2.5, 1, 1), (0.5, 0.0, 0.0)))
        # self.victory_letters.append(GameObject(Vector(16.5, 1, 5.5), Vector(0, -pi/4, 0), Vector(3, 1, 1), (0.5, 0.0, 0.0)))
        # #O
        # self.victory_letters.append(GameObject(Vector(15, 1, 9), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        # self.victory_letters.append(GameObject(Vector(15, 1, 12), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        # self.victory_letters.append(GameObject(Vector(17, 1, 10.5), Vector(0, 0, 0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        # self.victory_letters.append(GameObject(Vector(13, 1, 10.5), Vector(0, 0, 0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        # #U
        # self.victory_letters.append(GameObject(Vector(15, 1, 15), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        # self.victory_letters.append(GameObject(Vector(15, 1, 18), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        # self.victory_letters.append(GameObject(Vector(13, 1, 16.5), Vector(0, 0, 0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        #P
        self.victory_letters.append(GameObject(Vector(14, 1, 4.5), Vector(0,0,0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(16.5, 1, 5.5), Vector(0,0,0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(14, 1, 5.5), Vector(0,0,0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(15.25, 1, 7), Vector(0,0,0), Vector(2, 1, 1), (0.5, 0.0, 0.0)))
        #1
        if self.p1_has_won == True:
            self.victory_letters.append(GameObject(Vector(14, 1, 10.5), Vector(0,0,0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        #2
        elif self.p2_has_won == True:
            self.victory_letters.append(GameObject(Vector(16.5, 1, 12), Vector(0,0,0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
            self.victory_letters.append(GameObject(Vector(14, 1, 12), Vector(0,0,0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
            self.victory_letters.append(GameObject(Vector(11.5, 1, 12), Vector(0,0,0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
            self.victory_letters.append(GameObject(Vector(15.25, 1, 13), Vector(0,0,0), Vector(2, 1, 1), (0.5, 0.0, 0.0)))
            self.victory_letters.append(GameObject(Vector(12.75, 1, 11), Vector(0,0,0), Vector(2, 1, 1), (0.5, 0.0, 0.0)))

        #W
        self.victory_letters.append(GameObject(Vector(7, 1, 3), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(5, 1, 3.5), Vector(0, 0, 0), Vector(1, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(6, 1, 4.25), Vector(0, -pi/6, 0), Vector(3, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(6, 1, 5.75), Vector(0, pi/6, 0), Vector(3, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(7, 1, 7), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(5, 1, 6.5), Vector(0, 0, 0), Vector(1, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(7, 1, 5), Vector(0, 0, 0), Vector(1, 1, 1), (0.5, 0.0, 0.0)))
        #O
        self.victory_letters.append(GameObject(Vector(7, 1, 9), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(7, 1, 12), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(9, 1, 10.5), Vector(0, 0, 0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(5, 1, 10.5), Vector(0, 0, 0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        #N
        self.victory_letters.append(GameObject(Vector(7, 1, 15), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(7, 1, 18), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(Vector(7, 1, 16.5), Vector(0, pi/5, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))


    def program_loop(self):
        exiting = False
        while not exiting:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if self.p1_has_won or self.p2_has_won:
                        print("Congratulations, you won!")
                        print("Thank you for playing!")
                        exiting = True
                    else:
                        if event.key == K_ESCAPE:
                            print("Escaping!")
                            exiting = True
                            
                        if event.key == K_UP:
                            self.UP_key_down = True
                        if event.key == K_DOWN:
                            self.DOWN_key_down = True
                        if event.key == K_LEFT:
                            self.LEFT_key_down = True
                        if event.key == K_RIGHT:
                            self.RIGHT_key_down = True
                        if event.key == K_w:
                            self.W_key_down = True
                        if event.key == K_s:
                            self.S_key_down = True
                        if event.key == K_a:
                            self.A_key_down = True
                        if event.key == K_d:
                            self.D_key_down = True
                        if event.key == K_t:
                            self.T_key_down = True
                        if event.key == K_g:
                            self.G_key_down = True
                        if event.key == K_o:
                            if self.overview:
                                self.overview = False
                            else:
                                self.overview = True
                        if event.key == K_SPACE:
                            if self.flashlight:
                                self.flashlight = False
                            else:
                                self.flashlight = True
                        if event.key == K_p:
                            if self.map:
                                self.map = False
                            else:
                                self.map = True

                elif event.type == pygame.KEYUP:
                    if event.key == K_UP:
                        self.UP_key_down = False
                    if event.key == K_DOWN:
                        self.DOWN_key_down = False
                    if event.key == K_LEFT:
                        self.LEFT_key_down = False
                    if event.key == K_RIGHT:
                        self.RIGHT_key_down = False
                    if event.key == K_w:
                        self.W_key_down = False
                    if event.key == K_s:
                        self.S_key_down = False
                    if event.key == K_a:
                        self.A_key_down = False
                    if event.key == K_d:
                        self.D_key_down = False
                    if event.key == K_t:
                        self.T_key_down = False
                    if event.key == K_g:
                        self.G_key_down = False
            
            if self.p1_has_won or self.p2_has_won:
                self.display_victory_screen()
            else:
                self.update()
                self.display()

        #OUT OF GAME LOOP
        pygame.quit()

    def start(self):
        self.program_loop()

if __name__ == "__main__":
    GraphicsProgram3D().start()