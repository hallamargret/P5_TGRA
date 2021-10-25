attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

uniform vec4 u_eye_position;


uniform vec4 u_mat_diffuse;
uniform vec4 u_mat_specular;
uniform float u_mat_shininess;

varying vec4 v_color;

struct light{
	vec4 position;
	vec4 diffuse;
	vec4 specular;

};

uniform light lights[5];


void main(void)
{
	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
	vec4 normal = vec4(a_normal.x, a_normal.y, a_normal.z, 0.0);
	// local coordinates
	position = u_model_matrix * position;
	normal = normalize(u_model_matrix * normal);

	vec4 total;
	vec4 s;

	//global coordinates
	for (int i = 0; i < 5; i++){
		//position light
		if (lights[i].position.w == 1.0){
			s = normalize(lights[i].position - position);

		}
		// Directional light
		else{
			s = normalize(lights[i].position);
		}


		float lambert = max(dot(normal, s), 0.0);

		vec4 v = normalize(u_eye_position - position);
		vec4 h = normalize(s + v);
		float phong = max(dot(normal, h), 0.0);
		
		vec4 value = lights[i].diffuse * u_mat_diffuse * lambert + lights[i].specular * u_mat_specular * pow(phong, u_mat_shininess);
		total = total + value;
	}

		v_color = total;



	position = u_view_matrix * position;
	// eye coordinates
	position = u_projection_matrix * position;
	// clip coordinates
	
	gl_Position = position;
}