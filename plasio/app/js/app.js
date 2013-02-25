
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
    var maxx = 0;
    var MAX_INT = 65535;
    for (var i=0; i<points.length; i=i+3){
      var x = (points[i+0] / MAX_INT ) ;
      var y = (points[i+1] / MAX_INT );
      var z = (points[i+2] / MAX_INT) ;
      var pt = new THREE.Vector3(x,y,z);
      //console.log(points[i+0], points[i+0], points[i+0]);
      geom.vertices.push(pt);
    }
    console.log(maxx);
    scene.remove(point_cloud);
    point_cloud = new THREE.ParticleSystem(geom, material)
    var c = stream_header.center;
    var s = -1.0*stream_header.scale_factor;
    point_cloud.position.set(c[0]*s, c[1]*s, c[2]*s);
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
    var FAR = 100000;

    $container = $('#container');

    //CAMERA
    window.camera = new THREE.PerspectiveCamera(VIEW_ANGLE, ASPECT, NEAR, FAR);
    camera.position.z = 10;

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


