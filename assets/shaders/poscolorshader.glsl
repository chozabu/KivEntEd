---VERTEX SHADER---
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* vertex attributes */
attribute float     v0;
attribute float     v1;
attribute float     v2;
attribute float     v3;
attribute float     v4;
attribute float     v5;
attribute float     v6;
attribute float     v7;
//attribute vec2     vTexCoords0;


/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform vec4       color;
uniform float      opacity;

void main (void) {
  frag_color = vec4(v2, v3, v4, v5);
  tex_coord0 = vec2(v6, v7);
  vec4 pos = vec4(v0, v1, 0.0, 1.0);
  gl_Position = projection_mat * pos;

}


---FRAGMENT SHADER---
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;

void main (void){
    vec2 tc=vec2(fract(tex_coord0.s),fract(tex_coord0.t));
    gl_FragColor = frag_color * texture2D(texture0, tc);
}
