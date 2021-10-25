
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

class GraphicsProgram3D:
    def __init__(self):

        pygame.init() 
        pygame.display.set_mode((800,600), pygame.OPENGL|pygame.DOUBLEBUF)

        self.shader = Shader3D()
        self.shader.use()

        self.model_matrix = ModelMatrix()

        self.view_matrix = ViewMatrix()
        # We start in point 1,1,1 and look at the point in front of us 2,1,2
        self.view_matrix.look(Point(1, 1, 1), Point(2, 1, 2), Vector(0, 1, 0)) # Game mode

        self.overview_matrix = ViewMatrix()
        # overview mode, when o is pressed on the keyboard we see the maze from above in point 10,25,10 which is straight up from the middle of the maze
        self.overview_matrix.look(Point(10, 25, 10), Point(11, 1, 10), Vector(0, 1, 0))

        self.wall_height = 6
        self.maze_size = 20

        self.near_plane = 0.3
        self.far_plane = 100
        self.walls = []
        self.radius = 0.8
        
        
        self.projection_matrix = ProjectionMatrix()
        self.fov = pi/2
        self.projection_matrix.set_perspective((pi / 2), (800 / 600), self.near_plane, self.far_plane)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.cube = Cube()

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

        # Cubes that are moving in the maze, the player will collide on them, set as hindrance
        moving_cube_1 = GameObject(self.cube, self.shader, self.model_matrix, Vector(14, 1, 2), Vector(0, 0, 0), Vector(1.0, 1.0, 1.0), (1, 0, 0))
        # moving_cube_1.add_behavior(MoveOnZ(moving_cube_1, 0.4, 3.9))
        # moving_cube_2 = GameObject(self.cube, self.shader, self.model_matrix, Vector(14, 1, 8), Vector(0, 0, 0), Vector(1.0, 1.0, 1.0), (1, 0, 0))
        # moving_cube_2.add_behavior(MoveOnX(moving_cube_2, 12.1, 15.9))
        # moving_cube_3 = GameObject(self.cube, self.shader, self.model_matrix, Vector(2, 1, 12), Vector(0, 0, 0), Vector(1.0, 1.0, 1.0), (1, 0, 0))
        # moving_cube_3.add_behavior(MoveOnX(moving_cube_3, 0.4, 3.9))

        self.moving_cubes = [moving_cube_1]

        # Player should try to collect all of the end cubes, when all are collected the player will win the game
        end_cube_1 = GameObject(self.cube, self.shader, self.model_matrix, Vector(18, 1, 18), Vector(0, 0, 0), Vector(1, 1, 1), (1, 0, 1))
        # end_cube_2 = GameObject(self.cube, self.shader, self.model_matrix, Vector(18, 1, 8), Vector(0, 0, 0), Vector(1, 1, 1), (1, 0, 1))
        # end_cube_3 = GameObject(self.cube, self.shader, self.model_matrix, Vector(6, 1, 11), Vector(0, 0, 0), Vector(1, 1, 1), (1, 0, 1))
        # end_cube_4 = GameObject(self.cube, self.shader, self.model_matrix, Vector(12, 1, 18), Vector(0, 0, 0), Vector(1, 1, 1), (1, 0, 1))

        self.current_end_cube = 0

        self.end_cubes = [end_cube_1]

        for cube in self.end_cubes:
            cube.add_behavior(Spin(cube))

        self.add_walls()
        
        self.victory_letters = []

        self.has_won = False

    def add_walls(self):
        #big walls
        self.walls.append(Wall(Vector(self.maze_size/2, (self.wall_height/2), self.maze_size), Vector(self.maze_size, self.wall_height, 0.8)))
        self.walls.append(Wall(Vector(self.maze_size/2, (self.wall_height/2), 0), Vector(self.maze_size, self.wall_height, 0.8)))
        self.walls.append(Wall(Vector(0, (self.wall_height/2), self.maze_size/2), Vector(0.8, self.wall_height, self.maze_size)))
        self.walls.append(Wall(Vector(self.maze_size, (self.wall_height/2), self.maze_size/2), Vector(0.8, self.wall_height, self.maze_size)))

    def draw_maze_floor(self, color_list, translation_list, scale_list):
        self.shader.set_material_diffuse(color_list[0], color_list[1], color_list[2])
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(translation_list[0], translation_list[1], translation_list[2])
        self.model_matrix.add_scale(scale_list[0], scale_list[1], scale_list[2])
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.set_verticies(self.shader)
        self.cube.draw()
        self.model_matrix.pop_matrix()
    
    '''Check if the player is colliding any walls or objects, if so it will handle it so the player will slide among the wall/object but not walk througt it'''
    def check_collision(self, wall):
        # check if the eye is to close to the wall (for every wall)
        if wall.min_x <= self.view_matrix.eye.x <= wall.max_x:
            # right side of the wall
            if self.view_matrix.eye.z >= wall.max_z:
                if (self.view_matrix.eye.z - wall.max_z) <= self.radius:
                    self.view_matrix.eye.z = wall.max_z + self.radius
            # left side of the wall
            elif self.view_matrix.eye.z <= wall.min_z:
                if (wall.min_z - self.view_matrix.eye.z) <= self.radius:
                    self.view_matrix.eye.z = wall.min_z - self.radius
            
        elif wall.min_z <= self.view_matrix.eye.z <= wall.max_z:
            # right side of the wall
            if self.view_matrix.eye.x >= wall.max_x:
                if (self.view_matrix.eye.x - wall.max_x) <= self.radius:
                    self.view_matrix.eye.x = wall.max_x + self.radius
            # left side of the wall
            elif self.view_matrix.eye.x <= wall.min_x:
                if (wall.min_x - self.view_matrix.eye.x) <= self.radius:
                    self.view_matrix.eye.x = wall.min_x - self.radius
        
        else: # Check corners
            upper_left_corner = Point(wall.min_x, 1, wall.max_z)
            upper_right_corner = Point(wall.max_x, 1, wall.max_z)
            lower_left_corner = Point(wall.min_x, 1, wall.min_z)
            lower_right_corner = Point(wall.max_x, 1, wall.min_z)
            upper_left_dist = self.view_matrix.eye - upper_left_corner # Upper left corner
            if upper_left_dist.__len__() < self.radius:
                upper_left_dist.normalize()
                new_dist = upper_left_dist * self.radius # Set the length of distance vector to the length of the radius
                self.view_matrix.eye = upper_left_corner + new_dist
            upper_right_dist = self.view_matrix.eye - upper_right_corner # Upper right corner
            if upper_right_dist.__len__() < self.radius:
                upper_right_dist.normalize()
                new_dist = upper_right_dist * self.radius # Set the length of distance vector to the length of the radius
                self.view_matrix.eye = upper_right_corner + new_dist
            lower_left_dist = self.view_matrix.eye - lower_left_corner # lower left corner
            if lower_left_dist.__len__() < self.radius:
                lower_left_dist.normalize()
                new_dist = lower_left_dist * self.radius # Set the length of distance vector to the length of the radius
                self.view_matrix.eye = lower_left_corner + new_dist
            lower_right_dist = self.view_matrix.eye - lower_right_corner # Lower right corner
            if lower_right_dist.__len__() < self.radius:
                lower_right_dist.normalize()
                new_dist = lower_right_dist * self.radius # Set the length of distance vector to the length of the radius
                self.view_matrix.eye = lower_right_corner + new_dist

    def check_moving_cube_collision(self):
        for cube in self.moving_cubes:
            self.check_collision(cube)

    def check_spinning_cube_collision(self):
        distance_vector = self.view_matrix.eye - self.end_cubes[self.current_end_cube].translation
        if distance_vector.__len__() < (self.radius + 0.3):
            if self.current_end_cube < (len(self.end_cubes) - 1):
                self.current_end_cube += 1
            else:
                self.has_won = True

    def update(self):
        delta_time = self.clock.tick() / 1000.0

        self.angle += pi * delta_time

        if not self.overview:
            if self.W_key_down:
                self.view_matrix.slide_on_floor(0, -4 * delta_time)
            if self.S_key_down:
                self.view_matrix.slide_on_floor(0, 4 * delta_time)
            if self.A_key_down:
                self.view_matrix.slide_on_floor(-4 * delta_time, 0)
            if self.D_key_down:
                self.view_matrix.slide_on_floor(4 * delta_time, 0)
            if self.T_key_down:
                self.fov -= 0.1 * delta_time
            if self.G_key_down:
                self.fov += 0.1 * delta_time

            if self.UP_key_down:
                if self.pitch_angle <= (pi/6):
                    angle = pi * delta_time
                    self.pitch_angle += angle
                    self.view_matrix.pitch(angle)
            if self.DOWN_key_down:
                if self.pitch_angle >= -(pi/6):
                    angle = -pi * delta_time
                    self.pitch_angle += angle
                    self.view_matrix.pitch(angle)
            if self.LEFT_key_down:
                self.view_matrix.yaw_on_floor(pi * delta_time)
            if self.RIGHT_key_down:
                self.view_matrix.yaw_on_floor(-pi * delta_time)

        self.end_cubes[self.current_end_cube].update(delta_time)

        for cube in self.moving_cubes:
            cube.update(delta_time)


        for wall in self.walls:
            self.check_collision(wall)

        self.check_moving_cube_collision()
        self.check_spinning_cube_collision()
    
    

    def display(self):
        glEnable(GL_DEPTH_TEST)

        glClearColor(0.0, 0.2, 0.8, 1.0)    #color of space (sky)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glViewport(0, 0, 800, 600)

        self.projection_matrix.set_perspective((self.fov), (800 / 600), self.near_plane, self.far_plane)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        # View the maze from above to see the whole maze. Not able to move while in overview mode, only look.
        if self.overview:
            self.shader.set_view_matrix(self.overview_matrix.get_matrix())
            self.shader.set_eye_position(self.overview_matrix.eye)
        # Game mode (first person view), viewing the matrix as the player. Move (walk forward, to the right, left and backwards) and look around for end cubes.
        else:
            self.shader.set_view_matrix(self.view_matrix.get_matrix())
            self.shader.set_eye_position(self.view_matrix.eye)

        # first light  (positional)
        self.shader.set_light_pos_diff_spec(0, Point(10, 15, 0), (0.5, 0.5, 0.5), (0.4, 0.4, 0.4), 1.0)
        
        # second light (positional)
        self.shader.set_light_pos_diff_spec(1, Point(10, 15, 20), (0.5, 0.5, 0.5), (0.4, 0.4, 0.4), 1.0)
        
        # third light (positional)
        self.shader.set_light_pos_diff_spec(2, Point(0, 15, 10), (0.5, 0.5, 0.5), (0.4, 0.4, 0.4), 1.0)
        
        # fourth light (positional)
        self.shader.set_light_pos_diff_spec(3, Point(20, 15, 10), (0.5, 0.5, 0.5), (0.4, 0.4, 0.4), 1.0)

        # fifth light, flashlight (directional). Turned on when space has been pressed, turns off when space is pressed again.
        if self.flashlight:
            self.shader.set_light_pos_diff_spec(4, self.view_matrix.n, (0.5, 0.5, 0.1), (0.3, 0.3, 0.3), 0.0)
        else:
            self.shader.set_light_pos_diff_spec(4, self.view_matrix.n, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.0)

        # fifth light directional fixed position not used but can be replaced for the flashlight (or added to the list but then need some modifycations in the simple3D.vert file)
        #self.shader.set_light_pos_diff_spec(4, Point(1, 1, 1), (0.6, 0.6, 0.6), (0.5, 0.5, 0.5), 0.0)

        self.shader.set_material_specular(0.75, 0.75, 0.75)
        self.shader.set_material_shininess(15)

        self.model_matrix.load_identity()


        # The maze floor
        color = [0.2, 0.1, 0.7]
        translation_list = [self.maze_size/2, 0, self.maze_size/2]
        scale_list = [self.maze_size, 0.8, self.maze_size]
        self.draw_maze_floor(color, translation_list, scale_list)

        # Walls of the maze
        for wall in self.walls:
            wall.draw(self.shader, self.model_matrix, self.cube)

        self.end_cubes[self.current_end_cube].draw()

        for cube in self.moving_cubes:
            cube.draw()

        # little map of the maze in another smaller viewport, displays in the upper right corner. Turn off and on with the letter p on keyboard
        if self.map:
            glViewport(600, 400, 250, 200)
            glClear(GL_DEPTH_BUFFER_BIT)
            self.shader.set_view_matrix(self.overview_matrix.get_matrix())
            self.shader.set_eye_position(self.overview_matrix.eye)

            # The maze floor in the little map
            color = [0.2, 0.1, 0.7]
            translation_list = [self.maze_size/2, 0, self.maze_size/2]
            scale_list = [self.maze_size, 0.8, self.maze_size]
            self.draw_maze_floor(color, translation_list, scale_list)

            # Mazes walls in the little map
            for wall in self.walls:
                wall.draw(self.shader, self.model_matrix, self.cube)

            self.end_cubes[self.current_end_cube].draw()

            for cube in self.moving_cubes:
                cube.draw()
            

        pygame.display.flip()
    

    '''When the player has collected all four cubes then the player has won and the message "YOU WON" will display.
    Then when the player presses any key, the game will quit.'''
    def display_victory_screen(self):
        glEnable(GL_DEPTH_TEST)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glViewport(0, 0, 800, 600)

        self.projection_matrix.set_perspective((self.fov), (800 / 600), self.near_plane, self.far_plane)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.shader.set_view_matrix(self.overview_matrix.get_matrix())
        self.shader.set_eye_position(self.overview_matrix.eye)
        

        self.model_matrix.load_identity()

        color = [0.0, 0.0, 0.8]
        translation_list = [self.maze_size/2, 0, self.maze_size/2]
        scale_list = [self.maze_size, 0.8, self.maze_size]
        self.draw_maze_floor(color, translation_list, scale_list)

        self.create_victory_letters()

        for object in self.victory_letters:
            object.draw()

        pygame.display.flip()

    def create_victory_letters(self):
        #Y
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(16.5, 1, 3.5), Vector(0, pi/4, 0), Vector(3, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(14, 1, 4.5), Vector(0, 0, 0), Vector(2.5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(16.5, 1, 5.5), Vector(0, -pi/4, 0), Vector(3, 1, 1), (0.5, 0.0, 0.0)))
        #O
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(15, 1, 9), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(15, 1, 12), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(17, 1, 10.5), Vector(0, 0, 0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(13, 1, 10.5), Vector(0, 0, 0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        #U
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(15, 1, 15), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(15, 1, 18), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(13, 1, 16.5), Vector(0, 0, 0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        #W
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(7, 1, 3), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(5, 1, 3.5), Vector(0, 0, 0), Vector(1, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(6, 1, 4.25), Vector(0, -pi/6, 0), Vector(3, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(6, 1, 5.75), Vector(0, pi/6, 0), Vector(3, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(7, 1, 7), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(5, 1, 6.5), Vector(0, 0, 0), Vector(1, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(7, 1, 5), Vector(0, 0, 0), Vector(1, 1, 1), (0.5, 0.0, 0.0)))
        #O
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(7, 1, 9), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(7, 1, 12), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(9, 1, 10.5), Vector(0, 0, 0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(5, 1, 10.5), Vector(0, 0, 0), Vector(1, 1, 3), (0.5, 0.0, 0.0)))
        #N
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(7, 1, 15), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(7, 1, 18), Vector(0, 0, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))
        self.victory_letters.append(GameObject(self.cube, self.shader, self.model_matrix, Vector(7, 1, 16.5), Vector(0, pi/5, 0), Vector(5, 1, 1), (0.5, 0.0, 0.0)))


    def program_loop(self):
        exiting = False
        while not exiting:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if self.has_won:
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
            
            if self.has_won:
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