/* simple.glsl

simple diffuse lighting based on laberts cosine law; see e.g.:
    http://en.wikipedia.org/wiki/Lambertian_reflectance
    http://en.wikipedia.org/wiki/Lambert%27s_cosine_law
*/
---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec3  v_normal;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;

varying vec4 normal_vec;
varying vec4 vertex_pos;

void main (void) {
    //compute vertex position in eye_sapce and normalize normal vector
    vec4 pos = modelview_mat * vec4(v_pos,1.0);
    vertex_pos = pos;
    normal_vec = vec4(v_normal,0.0);
    gl_Position = projection_mat * pos;
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

varying vec4 normal_vec;
varying vec4 vertex_pos;

uniform mat4 normal_mat;
uniform vec3 Kd;
uniform vec3 Ka;
uniform vec3 Ks;
uniform float Tr;
uniform float Ns;

void main (void){
    //correct normal, and compute light vector (assume light at the eye)
    vec4 v_normal = normalize( normal_mat * normal_vec );
    vec4 v_light = normalize( vec4(0,0,0,1) - vertex_pos );
    //reflectance based on lamberts law of cosine
    //float theta = clamp(dot(v_normal, v_light), 0.0, 1.0);
    //float theta = 0.5;
    
    vec4 Ia = vec4(Kd, Tr);
    vec4 Id = vec4(Ka, Tr) * max(dot(v_light, v_normal), 0.0);
    vec4 Is = vec4(Ks, Tr) * pow(max(dot(v_light, v_normal), 0.0), Ns); 
    gl_FragColor = Ia + Id + Is;
}