require(['jquery', './app'], function($, app){


  $(document).ready(function(){

    a = function(){
      this.message = 'dat.gui';
      this.speed = 0.8;
    };
    inst = new a();
    gui = new dat.GUI({hideable: false, height: window.height});

    gui.add(inst, 'message');
    gui.add(inst, 'speed', -5, 5);


    app.start();
  });



});
