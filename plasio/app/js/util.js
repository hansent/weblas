define(function(require){ var self = {};


  self.read_file = function(url){
    var req = new XMLHttpRequest();
    req.open("GET", url, false);
    req.send(null);
    return (req.status == 200) ? req.responseText : null;
  };



  self.concat_uint16_arrays = function(first, second){
      var firstLength = first.length;
      var result = new Uint16Array(firstLength + second.length);
      result.set(first);
      result.set(second, firstLength);
      return result;
  };


return self;}); 
