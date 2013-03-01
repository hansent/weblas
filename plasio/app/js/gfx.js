define(function(require){ var self = {};

  var _three = require("./lib/three");
  var util = require("./util");


  // GLSLMaterial
  //==========================================================
  self.GLSLMaterial = function(parameters){
      var source = util.read_file( parameters.shader ).split("--FRAGMENT SHADER--");
      delete parameters.shader;
      parameters.vertexShader = source[0];
      parameters.fragmentShader = source[1];
      THREE.ShaderMaterial.call( this, parameters );
    };

  self.GLSLMaterial.prototype = Object.create(THREE.ShaderMaterial.prototype);


  // PointCloud 
  //==========================================================
  self.PointCloud = function (geom) {    
    THREE.ParticleSystem.call(this);
    this.uniforms = {};
    this.load_colorscheme("div_Spectral.png")
    this.geometry = geom || new THREE.Geometry();
    this.material = new self.GLSLMaterial({
      shader: "glsl/basic.glsl",
      uniforms: this.uniforms,
      depthTest: false,
      depthWrite: false,
      transparent: true ,
      blending: THREE.AdditiveBlending
    });

  };
  
  self.PointCloud.prototype = Object.create(THREE.ParticleSystem.prototype);

  self.PointCloud.prototype.load_colorscheme = function(scheme_src){
    this.texture = THREE.ImageUtils.loadTexture("img/schema/"+scheme_src);
    this.texture.minFilter = THREE.LinearFilter;
    this.texture.magFilter = THREE.LinearFilter; 
    this.uniforms['colortex'] = {type:'t', value: this.texture};
  };

  self.PointCloud.prototype.update_points = function(point_stream){
    console.log("PS", point_stream);
    var maxx = 0;
    var MAX_INT = 65535.0;
    var points = point_stream.buffer;
    this.geometry =  new THREE.Geometry();
    for (var i=0; i<points.length; i=i+3){
      var x = (points[i+0] / MAX_INT ) ;
      var y = (points[i+1] / MAX_INT );
      var z = (points[i+2] / MAX_INT) ;
      var pt = new THREE.Vector3(x,y,z);
      //console.log(points[i+0], points[i+0], points[i+0]);
      //console.log(x,y,z);
      this.geometry.vertices.push(pt);
    }
    this.dirty = true;
    this.geometry.verticesNeedUpdate = true;
    var c = point_stream.header.center;
    var s = -1.0 * point_stream.header.scale_factor;
    this.position.set(c[0]*s, c[1]*s, c[2]*s);
    //scene.add(point_cloud);
  };




return self;});
