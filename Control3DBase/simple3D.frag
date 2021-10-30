//varying vec4 v_color;

uniform sampler2D u_tex01;
uniform sampler2D u_tex02;

// uniform vec4 u_light_diffuse;
// uniform vec4 u_light_specular;


uniform vec4 u_mat_diffuse;
uniform vec4 u_mat_specular;
uniform float u_mat_shininess;

varying vec4 v_normal[4];
varying vec4 v_s[4];
varying vec4 v_h[4];

varying vec4 v_light_diffuse[4];
varying vec4 v_light_specular[4];

varying vec2 v_uv;

void main(void)
{

    vec4 mat_diffuse = u_mat_diffuse * texture2D(u_tex01, v_uv);
    vec4 mat_specular = u_mat_specular * texture2D(u_tex02, v_uv);

    vec4 total;

    for (int i = 0; i < 4; i++) {
        

        float lambert = max(dot(v_normal[i], v_s[i]), 0.0);

	    float phong = max(dot(v_normal[i], v_h[i]), 0.0);

        vec4 value = v_light_diffuse[i] * mat_diffuse * lambert + v_light_specular[i] * mat_specular * pow(phong, u_mat_shininess);
		total = total + value;
    }
    
    
    gl_FragColor = total;

}