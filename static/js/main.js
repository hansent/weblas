//global view state
var shader, vbo;
var view = {
  scale: 0.3,
  rot_mat: Matrix.I(4),
  last_mouse_pos: null
};

//calred when the canvas/window is resized
function reshape(w,h){
	gl.matrixMode(gl.PROJECTION);
	gl.loadIdentity();
	//gl.orthoMatrix(0,w ,0,h, -h*2,h*2);
	gl.perspectiveMatrix(70.0, w/h, 1, 1000.0 );
	gl.matrixMode(gl.MODEL_VIEW);
}

//render the frame
function display() {
	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
	gl.pushMatrix();
	//gl.rotate(80.0, 1.0, 0.0, 0.0);
	//gl.rotate(rotation_angle, 0.0, 0.0, 1);
  gl.translate(0,0,-100);
  gl.scale(view.scale, view.scale, view.scale);
  gl.multiplyMatrix(view.rot_mat);
	vbo.draw(shader, gl.POINTS);
	gl.popMatrix();
}

//idle function
function idle(){
}

function build_grid(){
  var grid = [];
  for (var x=-100; x < 100; x+=10){
    for (var y=-100; y < 100; y+=10){
      grid.push(x);
      grid.push(y);
      grid.push(0);
    }
  }
  return grid;
}

function init_gl(){
	initWebGlut("WebGlut");
	shader = new ShaderProgram("#vertex-shader", "#fragment-shader");
	vbo = new VertexBuffer("vvv", build_grid());
	wglutIdleFunc(idle);
	wglutReshapeFunc(reshape);
	wglutDisplayFunc(display);
	wglutStartMainLoop();
}

// UI EVENT HANDLERS ///////////////////////////
var on_mousewheel = function(ev,  delta){
  if (delta > 0)
    view.scale *= 1.05;
  if (delta < 0)
    view.scale *= .95;
};

//rotate on mouse move
var on_mouse_move = function(ev){
  if (!view.last_mouse_pos){
    view.last_mouse_pos = {x: ev.pageX, y: ev.pageY};
    return;
  }
  if (ev.which == 1){
    dx = ev.pageX - view.last_mouse_pos.x;
    dy = ev.pageY - view.last_mouse_pos.y;
    console.log(dx, dy);
    //premultiply new rotation matrix
    view.rot_mat = makeRotationMatrix(dy*0.2, 1,0,0).multiply(view.rot_mat);
    view.rot_mat = makeRotationMatrix(dx*0.2, 0,1,0).multiply(view.rot_mat);
  }
  view.last_mouse_pos = {x: ev.pageX, y: ev.pageY};
};


chunks = 0;

//open websocket and receive data stream
var init_stream = function(){
  var sock = new WebSocket("ws://localhost:8080/socket");
  sock.binaryType = "arraybuffer";
  sock.onopen = function(){
    console.log("socket connected");
    sock.send(1);
  }
  sock.onmessage = function(ev){
    data_msg = new Int32Array(ev.data);
    chunks = chunks += 1;
    console.log("received chunk#:", chunks);
  };
  sock.onclose = function(){
    console.log("socket closed");
  };

};


//hookup event handlers, and setup gl context when done
$(document).ready(function() {
  $(document).mousemove(on_mouse_move);
  $(document).mousewheel(on_mousewheel);
  init_gl();
  init_stream();
});
