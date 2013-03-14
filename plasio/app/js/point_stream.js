define(function(require){ var self = {};

  var pubsub = require("./lib/pubsub");

  self.PointStream = function(ws_endpoint){
    this.header = {};
    this.buffer = new Uint16Array([]);

    this.socket = new WebSocket(ws_endpoint);
    this.socket.binaryType = "arraybuffer";
    this.socket.point_stream = this;
    this.socket.onopen = this.on_socket_open;
    this.socket.onclose = this.on_socket_close;
    this.socket.onmessage = this.on_socket_message;
  };

  self.PointStream.prototype.on_socket_open = function(){
    var _this = this.point_stream;
    _this.send_msg("load", {filename: "serpent-small.las"});
  };

  self.PointStream.prototype.on_socket_close = function(msg){
    var _this = this.point_cloud;
    console.log("PointStream: socket closed");
  };

  self.PointStream.prototype.on_socket_message = function(msg){
    var _this = this.point_stream;
    if (typeof(msg.data) === "string")
      _this.handle_msg(JSON.parse(msg.data));
    else
      _this.append_binary_data(msg.data);
  };

  self.PointStream.prototype.send_msg = function(msg_type, msg_data){
    msg = JSON.stringify({type: msg_type, data: msg_data});
    this.socket.send(msg);
  };

  self.PointStream.prototype.handle_msg = function(msg){
    if (msg.type === "header"){
      this.header = msg.data;
      console.log("header", this.header);
    }
    else{
      console.log("Unknown controll message:", msg);
    }
  };

  self.PointStream.prototype.append_binary_data = function(data){
    var old_data = this.buffer;
    var new_data = new Uint16Array(data);
    this.buffer = new Uint16Array(old_data.length + new_data.length);
    this.buffer.set(old_data);
    this.buffer.set(new_data, old_data.length);
    pubsub.publish("point_stream/update", [this]);

    //window.update_point_cloud(buffer);
    //setTimeout(function(){ sock.send_msg('next_chunk') }, 5);      
  };



return self});
