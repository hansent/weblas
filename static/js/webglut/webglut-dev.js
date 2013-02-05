
function IncludeJS(jsFile) {
    document.write('<script type="text/javascript" src="'+ jsFile + '"></scr' + 'ipt>');
}

IncludeJS("/static/js/webglut/gl.js");
IncludeJS("/static/js/webglut/class.js");
IncludeJS("/static/js/webglut/request.js");
IncludeJS("/static/js/webglut/glMatrix.js");
IncludeJS("/static/js/webglut/ShaderProgram.js");
IncludeJS("/static/js/webglut/VertexBuffer.js");
IncludeJS("/static/js/webglut/webglut.js");
