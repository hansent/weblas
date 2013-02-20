
define(function(require){
  var $    = require("jquery");
  var _th  = require("./lib/three");
  var _dg  = require("./lib/dat.gui");
  var util = require("./util");
  var lasstream = require("./lasstream");



  var texture = THREE.ImageUtils.loadTexture( "img/schema/div_Spectral.png" );
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;

  var uniforms = {
    colortex: { type: "t", value: texture }
  };

  material = new util.GLSLMaterial({
    shader: "glsl/basic.glsl",
    uniforms: uniforms,
    depthTest: false, 
    depthWrite: false,
    transparent: true ,
    blending: THREE.AdditiveBlending
  });


  var init_point_cloud = function(){

    var geom = new THREE.Geometry();
    geom.vertices.push(new THREE.Vector3(0,0,0));

    window.point_cloud =  new THREE.ParticleSystem(geom, material);
    scene.add(point_cloud);
    point_cloud.scale = 3.0;
  };


  function add_sphere(){
    var sphere = new THREE.Mesh(
      new THREE.SphereGeometry(1.0, 32, 32),
      new THREE.MeshLambertMaterial({color: 0xCC0000})
    );

    scene.add(sphere);
  }


  update_point_cloud = function(points){

    geom =  new THREE.Geometry();
    for (var i=0; i<points.length; i=i+3){
      var x = points[i];
      var y = points[i+1];
      var z = points[i+2];
      geom.vertices.push(new THREE.Vector3(x,y,z));
    }

    //geom.computeBoundingBox();
    //bb = geom.boundingBox;

    scene.remove(point_cloud);
    point_cloud = new THREE.ParticleSystem(geom, material)
    scene.add(point_cloud);

  }


  var callbacks = {
    resize: function(){
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect	= window.innerWidth/window.innerHeight;
      camera.updateProjectionMatrix();
    },
  };




  var attach_window_event_handlers = function(){
    window.addEventListener('resize', callbacks.resize, false);
  };


  var init = function(){
    var WIDTH = window.innerWidth;
    var HEIGHT = window.innerHeight;

    var VIEW_ANGLE = 45;
    var ASPECT = WIDTH / HEIGHT;
    var NEAR = 0.1;
    var FAR = 10000;

    $container = $('#container');

    //CAMERA
    window.camera = new THREE.PerspectiveCamera(VIEW_ANGLE, ASPECT, NEAR, FAR);
    camera.position.z = 500;

    //LIGHT
    var pointLight = new THREE.PointLight( 0xFFFFFF );
    pointLight.position.x = 10;
    pointLight.position.y = 50;
    pointLight.position.z = 130;

    //SCENE SETUP
    window.scene = new THREE.Scene();
    scene.add(camera);
    scene.add(pointLight);
    init_point_cloud();

    //SETUP CONTROLS
    window.controls = new THREE.TrackballControls(camera, $container[0]);

    //SETUP RENDER
    window.renderer = new THREE.WebGLRenderer();
    renderer.setSize(WIDTH, HEIGHT);

    //HOOK IT UP TO THE DOM
    $container.append(renderer.domElement);

    //START STREAMING
    lasstream.init_stream();
  };



  var render_loop = function() {
    controls.update(camera);
    renderer.render( scene, camera );
    requestAnimationFrame( render_loop );
  };



  return {
    start: function(){
      init();
      render_loop();
    }
  };



});


