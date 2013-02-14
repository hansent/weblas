
//--VERTEX SHADER--//////////////////////////////////////////

uniform sampler2D colortex;

varying float height;
void main() {
    gl_PointSize = 2.0;
    height = (((position.z - (position.z*0.5) )) / 20.0) + 0.6 ;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position.xyz, 1);
}



//--FRAGMENT SHADER--//////////////////////////////////////////

uniform sampler2D colortex;
varying float height;

void main() {
    float alpha = smoothstep(1500.0, -1500.0, gl_FragCoord.z / gl_FragCoord.w );
    vec4 col = texture2D(colortex, vec2(height,0.5));
    gl_FragColor = vec4( col.r,col.g,col.b,  alpha);
}
