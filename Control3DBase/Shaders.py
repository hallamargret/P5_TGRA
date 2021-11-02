
from OpenGL.GLU import*
from OpenGL.GL import *
from math import * # trigonometry

import sys

from Base3DObjects import *

NUMBER_OF_LIGHTS = 5

class Shader3D:
    def __init__(self):
        vert_shader = glCreateShader(GL_VERTEX_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.vert")
        glShaderSource(vert_shader,shader_file.read())
        shader_file.close()
        glCompileShader(vert_shader)
        result = glGetShaderiv(vert_shader, GL_COMPILE_STATUS)
        if (result != 1): # shader didn't compile
            print("Couldn't compile vertex shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(vert_shader)))

        frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.frag")
        glShaderSource(frag_shader,shader_file.read())
        shader_file.close()
        glCompileShader(frag_shader)
        result = glGetShaderiv(frag_shader, GL_COMPILE_STATUS)
        if (result != 1): # shader didn't compile
            print("Couldn't compile fragment shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(frag_shader)))

        self.renderingProgramID = glCreateProgram()
        glAttachShader(self.renderingProgramID, vert_shader)
        glAttachShader(self.renderingProgramID, frag_shader)
        glLinkProgram(self.renderingProgramID)

        self.positionLoc			= glGetAttribLocation(self.renderingProgramID, "a_position")
        glEnableVertexAttribArray(self.positionLoc)

        ## ADD CODE HERE ##

        self.normalLoc			= glGetAttribLocation(self.renderingProgramID, "a_normal")
        glEnableVertexAttribArray(self.normalLoc)

        self.uvLoc              = glGetAttribLocation(self.renderingProgramID, "a_uv")
        glEnableVertexAttribArray(self.uvLoc)

        self.modelMatrixLoc			            = glGetUniformLocation(self.renderingProgramID, "u_model_matrix")
        self.ViewMatrixLoc			= glGetUniformLocation(self.renderingProgramID, "u_view_matrix")
        self.ProjectionMatrixLoc			= glGetUniformLocation(self.renderingProgramID, "u_projection_matrix")

        self.eyePosLoc                = glGetUniformLocation(self.renderingProgramID, "u_eye_position")

        # self.lightPosLoc            = glGetUniformLocation(self.renderingProgramID, "u_light_position")

        # self.lightDiffuseLoc = glGetUniformLocation(self.renderingProgramID,  "u_light_diffuse")
        # self.lightSpecularLoc = glGetUniformLocation(self.renderingProgramID,  "u_light_specular")

        self.lightsPosLocs = []     #list of the locations of the positions of all the lights
        self.lightsDiffuseLocs = []     #list of the locations of the diffuse of all the lights
        self.lightsSpecularLocs = []    #list of the locations of the specular of all the lights
        

        for i in range(NUMBER_OF_LIGHTS):
            self.lightsPosLocs.append(glGetUniformLocation(self.renderingProgramID, "lights[" + str(i) + "].position"))
            self.lightsDiffuseLocs.append(glGetUniformLocation(self.renderingProgramID, "lights[" + str(i) + "].diffuse"))
            self.lightsSpecularLocs.append(glGetUniformLocation(self.renderingProgramID, "lights[" + str(i) + "].specular"))


        self.materialDiffuseLoc                = glGetUniformLocation(self.renderingProgramID, "u_mat_diffuse")
        self.materialSpecularLoc                = glGetUniformLocation(self.renderingProgramID, "u_mat_specular")
        self.materialShininessLoc                = glGetUniformLocation(self.renderingProgramID, "u_mat_shininess")

        self.diffuseTextureLoc                  = glGetUniformLocation(self.renderingProgramID, "u_tex01")
        
        self.specularTextureLoc                 = glGetUniformLocation(self.renderingProgramID, "u_tex02")

        self.usingTextureLoc                    = glGetUniformLocation(self.renderingProgramID, "u_using_texture")

    def use(self):
        try:
            glUseProgram(self.renderingProgramID)   
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.renderingProgramID))
            raise

    def set_model_matrix(self, matrix_array):
        glUniformMatrix4fv(self.modelMatrixLoc, 1, True, matrix_array)

    def set_view_matrix(self, matrix_array):
        glUniformMatrix4fv(self.ViewMatrixLoc, 1, True, matrix_array)

    def set_projection_matrix(self, matrix_array):
        glUniformMatrix4fv(self.ProjectionMatrixLoc, 1, True, matrix_array)

    def set_solid_color(self, red, green , blue):
        glUniform4f(self.colorLoc, red, green, blue, 1.0)

    def set_light_position(self, pos):
        glUniform4f(self.lightPosLoc, pos.x, pos.y, pos.z, 1.0)
    
    '''Doing all three in one function, setting the lights position, diffuse, specular and wheter it is a directional or positional light'''
    def set_light_pos_diff_spec(self, light_index, pos, diff, spec, dir_or_pos_light):
        glUniform4f(self.lightsPosLocs[light_index], pos.x, pos.y, pos.z, dir_or_pos_light)
        glUniform4f(self.lightsDiffuseLocs[light_index], diff[0], diff[1], diff[2], dir_or_pos_light)
        glUniform4f(self.lightsSpecularLocs[light_index], spec[0], spec[1], spec[2], dir_or_pos_light)
    
    def set_eye_position(self, pos):
        glUniform4f(self.eyePosLoc, pos.x, pos.y, pos.z, 1.0)

    def set_light_diffuse(self, red, green , blue):
        glUniform4f(self.lightDiffuseLoc, red, green, blue, 1.0)

    def set_light_specular(self, red, green , blue):
        glUniform4f(self.lightSpecularLoc, red, green, blue, 1.0)

    # def set_material_diffuse(self, red, green , blue):
    #     glUniform4f(self.materialDiffuseLoc, red, green, blue, 1.0)
    
    # def set_material_specular(self, red, green , blue):
    #     glUniform4f(self.materialSpecularLoc, red, green, blue, 1.0)

    # def set_material_shininess(self, shininess):
    #     glUniform1f(self.materialShininessLoc, shininess)
    
# def set_material_diffuse(self, red, green, blue):
    #     glUniform4f(self.materialDiffuseLoc, red, green, blue, 1.0)

    def set_material_diffuse(self, color):
        glUniform4f(self.materialDiffuseLoc, color.r, color.g, color.b, 1.0)

    # def set_material_specular(self, red, green, blue):
    #     glUniform4f(self.materialSpecularLoc, red, green, blue, 1.0)

    def set_material_specular(self, color):
        glUniform4f(self.materialSpecularLoc, color.r, color.g, color.b, 1.0)

    def set_material_shininess(self, shininess):
        glUniform1f(self.materialShininessLoc, shininess)



    def set_position_attribute(self, vertex_array):
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_normal_attribute(self, vertex_array):
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 0, vertex_array)
    
    def set_attribute_buffers(self, vertex_buffer_id):
        glUniform1f(self.usingTextureLoc, 0.0)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_id)
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(0))
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 6 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(3 * sizeof(GLfloat)))


    def set_attribute_buffers_with_uv(self, vertex_buffer_id):
        glUniform1f(self.usingTextureLoc, 1.0)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_id)
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 8 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(0))
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 8 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(3 * sizeof(GLfloat)))
        glVertexAttribPointer(self.uvLoc, 2, GL_FLOAT, False, 8 * sizeof(GLfloat), OpenGL.GLU.ctypes.c_void_p(6 * sizeof(GLfloat)))

    def set_uv_attribute(self, vertex_array):
        glVertexAttribPointer(self.uvLoc, 2, GL_FLOAT, False, 0, vertex_array)

    def set_diffuse_tex(self, number):
        glUniform1i(self.diffuseTextureLoc, number)
    
    def set_spec_tex(self, number):
        glUniform1i(self.diffuseTextureLoc, number)
    
    def set_using_texture(self, number):
        glUniform1f(self.usingTextureLoc, number)

    

