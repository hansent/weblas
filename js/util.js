

var read_file = function(url) {
  var req = new XMLHttpRequest();
  req.open("GET", url, false);
  req.send(null);
  return (req.status == 200) ? req.responseText : null;
};


var GLSLMaterial = function(parameters){
  var source = read_file( parameters.shader ).split("--FRAGMENT SHADER--");
  delete parameters.shader;
  parameters.vertexShader = source[0];
  parameters.fragmentShader = source[1];
  THREE.ShaderMaterial.call( this, parameters );
};

GLSLMaterial.prototype = Object.create(THREE.ShaderMaterial.prototype);
