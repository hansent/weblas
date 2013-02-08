
//open websocket and receive data stream
var init_stream = function(){
  var header = null;
  var buffer = new Float32Array([]);
  var chunk_index = 0;

  var sock = new WebSocket("ws://"+location.hostname+":8080/socket");
  sock.binaryType = "arraybuffer";

  sock.onopen = function(){
    sock.send_msg("load", {filename: "mount_st_helens.las"});
  }
  
  sock.onclose = function(){
    console.log("socket closed");
  };

  sock.onmessage = function(ev){
    if (typeof(ev.data) === "string")
      this.handle_controll_msg(JSON.parse(ev.data));
    else
      this.handle_binary_msg(ev.data);
  };

  sock.send_msg = function(msg_type, msg_data){
    msg = JSON.stringify({type: msg_type, data: msg_data});
    this.send(msg);
  };

  sock.handle_controll_msg = function(msg){
    if (msg.type === "header")
      header = msg.data;
    else
      console.log("Unknown controll message:", msg);
  };

  sock.handle_binary_msg = function(data){
    var new_part = new Float32Array(data);
    buffer = concatFloat32Array(buffer, new_part);
    update_point_cloud(buffer);
    sock.send_msg("next_chunk");
  };

};


function concatFloat32Array(first, second){
    var firstLength = first.length;
    var result = new Float32Array(firstLength + second.length);
    result.set(first);
    result.set(second, firstLength);
    return result;
}
