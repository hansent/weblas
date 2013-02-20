
//open websocket and receive data stream
var init_stream = function(){
  var header = null;
  var chunk_index = 0;

  var sock = new WebSocket("ws://"+location.hostname+":8080/socket");
  sock.binaryType = "arraybuffer";

  sock.onopen = function(){
    console.log("socket connected");
    sock.send("load:mount_st_helens.las");
  }
  
  sock.onmessage = function(ev){
    //data_msg = new Int32Array(ev.data);
    //chunks = chunks += 1;
    if (header == null){
      header = JSON.parse(ev.data);
    }

    else{
      //var data = build_grid();
      buffer = concatFloat32Array(buffer, new Float32Array(ev.data));
      update_point_cloud(buffer);
      setTimeout(function(){sock.send('moar')}, 5);
    }


  };
  
  sock.onclose = function(){
    console.log("socket closed");
  };

};


function concatFloat32Array(first, second)
{
    var firstLength = first.length;
    var result = new Float32Array(firstLength + second.length);

    result.set(first);
    result.set(second, firstLength);

    return result;
}
