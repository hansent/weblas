
//--VERTEX SHADER--//////////////////////////////////////////

uniform sampler2D colortex;

varying float height;
void main() {
    gl_PointSize = 1.0;
    //height = (((position.z - (position.z*0.5) )) / 20.0) + 0.6 ;
    height = (position.z + 250.0)/500.0;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position.xyz, 1);
}



//--FRAGMENT SHADER--//////////////////////////////////////////

uniform sampler2D colortex;
varying float height;

void main() {
    float alpha = smoothstep(800.0, -800.0, gl_FragCoord.z / gl_FragCoord.w ) * 0.3;
    vec4 col = texture2D(colortex, vec2(height,0.5));
    gl_FragColor = vec4( col.r,col.g,col.b,  1.0);
    //gl_FragColor = vec4( alpha, alpha, alpha,  1.0);
}
