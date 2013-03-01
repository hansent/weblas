
define(function(require){
  var $ = require("jquery");
  var pubsub = require("./lib/pubsub");
  var three = require("./lib/three");
  var datgui = require("./lib/dat.gui");
  var gfx = require("./gfx");
  var util = require("./util");
  var point_stream = require("./point_stream");


  /*
   var resize_to_window: function(){
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect	= window.innerWidth/window.innerHeight;
      camera.updateProjectionMatrix();
  };
  window.addEventListener('resize', on_window_resize, false);
  */
  window.APP = window.APP || {};

  APP.init = function(){
    // DOM Container for Renderer
    $container = $('#container');

    //Scene
    APP.scene = new THREE.Scene();
    
    //Renderer
    APP.renderer = new THREE.WebGLRenderer();
    APP.renderer.setSize(window.innerWidth, window.innerHeight);
    $container.append(APP.renderer.domElement);
    
    //Camera
    var aspect = window.innerWidth / window.innerHeight;
    APP.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100000);
    APP.camera.position.z = 5;
    APP.scene.add(APP.camera);

    //Light
    var light = new THREE.PointLight( 0xFFFFFF );
    light.position.set(10,50,130);
    APP.scene.add(light);

    //Hookup Controlls and Renderer
    APP.controls = new THREE.TrackballControls(APP.camera, $container[0]);


    //Point Stream and Point Cloud 
    APP.point_stream = new point_stream.PointStream("ws://localhost:8080/socket");
    APP.point_cloud = new gfx.PointCloud();
    APP.scene.add(APP.point_cloud);
    var sphere = new THREE.Mesh(
      new THREE.SphereGeometry(1.0, 32, 32),
      new THREE.MeshLambertMaterial({color: 0xCC0000})
    );


    //App Events
    pubsub.subscribe("point_stream/update", function(point_stream){
        //console.log("new data from ", point_stream, point_stream.buffer.length);
        //APP.point_cloud.update_points(point_stream);
        
        
        var maxx = 0;
        var MAX_INT = 65535.0;
        var points = point_stream.buffer;
        var geom =  new THREE.Geometry();
        for (var i=0; i<points.length; i=i+3){
          var x = (points[i+0] / MAX_INT ) ;
          var y = (points[i+1] / MAX_INT );
          var z = (points[i+2] / MAX_INT) ;
          var pt = new THREE.Vector3(x,y,z);
          //console.log(points[i+0], points[i+0], points[i+0]);
          //console.log(x,y,z);
          geom.vertices.push(pt);
        }
        var c = point_stream.header.center;
        var s = -1.0 * point_stream.header.scale_factor;
        
        APP.scene.remove(APP.point_cloud);
        APP.point_cloud = new gfx.PointCloud(geom);

        APP.point_cloud.position.set(c[0]*s, c[1]*s, c[2]*s);
        APP.scene.add(APP.point_cloud);

        
        point_stream.send_msg('next_chunk');

    });


  };

  APP.render_loop = function() {
    APP.controls.update(APP.camera);
    APP.renderer.render( APP.scene, APP.camera );
    requestAnimationFrame( APP.render_loop );
  };


  APP.start = function (){
    APP.init();
    APP.render_loop();
  }

  return APP;
});

