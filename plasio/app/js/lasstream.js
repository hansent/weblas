define(function(require){ var self = {};

  var concatArray = function(first, second){
      var firstLength = first.length;
      var result = new Uint16Array(firstLength + second.length);
      result.set(first);
      result.set(second, firstLength);
      return result;
  };


  self.init_stream = function(){

    var header = null;
    var buffer = new Uint16Array([]);
    var chunk_index = 0;

    var sock = new WebSocket("ws://"+location.hostname+":8080/socket");
    sock.binaryType = "arraybuffer";

    sock.onopen = function(){
      sock.send_msg("load", {filename: "serpent-small.las"});
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
      if (msg.type === "header"){
        window.stream_header = msg.data;
        console.log("HEADER", stream_header)
      }
      else
        console.log("Unknown controll message:", msg);
    };

    sock.handle_binary_msg = function(data){
      console.log("binary message")
      var new_part = new Uint16Array(data);
      console.log(buffer[0], buffer[1], buffer[2]);
      buffer = concatArray(buffer, new_part);
      window.update_point_cloud(buffer);
      setTimeout(function(){ sock.send_msg('next_chunk') }, 5);      
    };

  };


return self});
