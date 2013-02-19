
//--VERTEX SHADER--//////////////////////////////////////////

uniform sampler2D colortex;
varying vec3 norm;
varying vec3 light_vec;
varying mat3 nmat;


void main() {
    //gl_PointSize = 2.0;
    //height = (((position.z - (position.z*0.5) )) / 20.0) + 0.6 ;
    float s = 1./512.;
    vec2 tc = vec2(position.x/200. +0.5, position.y/200. +0.5);

    float z = texture2D( colortex, tc ).x;
    vec4 pos = modelViewMatrix * vec4(position.xy, z * 50.0, 1);
    nmat = normalMatrix;
    float zU =  texture2D( colortex, tc + vec2(s, 0) ).x;
    float zV =  texture2D( colortex, tc + vec2(0, s) ).x;
    norm = normalize( normalMatrix * vec3(z - zV, 1.0, z - zU) );
    light_vec = (modelViewMatrix * vec4(0, 2,1,0)).xyz;// - position;

    gl_Position = projectionMatrix *  pos;
}



//--FRAGMENT SHADER--//////////////////////////////////////////

uniform sampler2D colortex;
varying vec3 norm;
varying vec3 light_vec;
varying mat3 nmat;
const vec3 LIGHT_COLOR = vec3(1,1,1);
const vec3 AMBIENT = vec3(0.2, 0.2, 0.2);

void main() {
    //float alpha = smoothstep(1500.0, -1500.0, gl_FragCoord.z / gl_FragCoord.w );
    //vec4 col = texture2D(colortex, vec2(height,0.5));
    //diffuse light
    
    vec3 toLight = normalize(vec3(0.0,1.0,1.0));
    vec3 n = normalize(norm);
    float diffuse_dot = dot(n, normalize(light_vec));
    float diffuse = clamp(diffuse_dot, 0.0, 1.0);
    float c = (1.0 - diffuse ) * 3.0;

    gl_FragColor = vec4(c,c,c,  1.0);
}
