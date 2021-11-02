//varying vec4 v_color;

uniform sampler2D u_tex01;
uniform sampler2D u_tex02;

// uniform vec4 u_light_diffuse;
// uniform vec4 u_light_specular;

//const int NUMBER_OF_LIGHTS = 5;



uniform vec4 u_mat_diffuse;
uniform vec4 u_mat_specular;
uniform float u_mat_shininess;

uniform float u_using_texture;

varying vec4 v_normal;
// varying vec4 v_s[NUMBER_OF_LIGHTS];
// varying vec4 v_h[NUMBER_OF_LIGHTS];
varying vec4 v_s[5];
varying vec4 v_h[5];

varying vec2 v_uv;

struct light{
	vec4 position;
	vec4 diffuse;
	vec4 specular;

};

uniform light lights[5];

void main(void)
{

    vec4 mat_diffuse = u_mat_diffuse;
    vec4 mat_specular = u_mat_specular;

    if (u_using_texture == 1.0){
        mat_diffuse *= texture2D(u_tex01, v_uv);
        mat_specular *= texture2D(u_tex02, v_uv);
    }

    vec4 total = vec4(0,0,0,1);
    float normal_len = length(v_normal);
    for (int i = 0; i < 5; i++) {
        float s_len = length(v_s[i]);
        float h_len = length(v_h[i]);
    
        float lambert = max(dot(v_normal, v_s[i])/(normal_len * s_len), 0.0);

	    float phong = max(dot(v_normal, v_h[i])/(normal_len * h_len), 0.0);

        vec4 value = lights[i].diffuse * mat_diffuse * lambert + lights[i].specular * mat_specular * pow(phong, u_mat_shininess);
		total = total + value;
    }
    
    
    gl_FragColor = total;

}