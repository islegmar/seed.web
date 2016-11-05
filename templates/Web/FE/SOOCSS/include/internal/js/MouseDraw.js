function myLog(msg) {
  $(document).trigger("log", msg);
}

/**
 * How to use:
 * @see https://gist.github.com/MathiasPaumgarten/2375726
 * @returns
 */
function MouseDraw() {
  // Elemento cuyos eventos de mouse vamos a interceptar
  this.$lienzo = null;
  
	// Modo actual del cursor
	this.mode=null;

  // Botón que se utiliza para indicar paint y para indicar move
  this.button4Paint = 0; // Botón izquierdo
  this.button4Move  = 2; // Botón derecho

  // Último Punto
  this.lastPoint = null;

  // Si true, paramos de movernos cuando nos salimos del objeto
  this.stopWhenLeave = true;
  
  // Si es un dispositivo móvil, va un poco distinto.
  // Sólo se dispara el evento 'moving' y no va precedido de un startMove
  this.isTouchDevice = 'ontouchend' in document;
  
  // IL - 23/07/13
  // Tenemos ciertos "problemas" para calcular las coordenadas relativas, así
  // que tenemos varios métodos y ajustamo el mejor en cada cas :-( 
  //Cuando useParentOffset=true es tal y como estaba hasta antes del cambio
  this.useParentOffset = true;
}

// Modos del cursor 
MouseDraw.MODE_PAINT = 0;
MouseDraw.MODE_MOVE = 1;

// --------------------------------------------------------------------- Setters
MouseDraw.prototype.setLienzo = function($lienzo) {
	this.$lienzo = $lienzo;
}

// IL - 23/07/13
MouseDraw.prototype.setUseParentOffset= function(useParentOffset) {
  this.useParentOffset = useParentOffset;
}

MouseDraw.prototype.setStopWhenLeave = function(stopWhenLeave) {
	this.stopWhenLeave = stopWhenLeave;
}

// Utility
MouseDraw.prototype.getRelCoordinates = function(e, $ele) {
  var parentOffset = $ele.parent().offset(); 
  var pageX = (e.originalEvent.touches==null ? e.pageX : e.originalEvent.touches[0].pageX);
  var pageY = (e.originalEvent.touches==null ? e.pageY : e.originalEvent.touches[0].pageY);
  
  /*  
  myLog("parentOffset : "+parentOffset.left + "," + parentOffset.top);
  myLog("TYPE : "+ e.type);
  myLog("ORIGINAL EVENT  : "+ e.originalEvent);
  myLog("TOUCHES : "+ (e.originalEvent.touches==null ? "No hay" : "Hay " + e.originalEvent.touches.length));
  myLog("PAGE X: "+ pageX);
  myLog("PAGE Y: "+ pageY);
  */
  
  //or $(this).offset(); if you really just want the current element's offset
  var relX, relY;
	
  if ( this.useParentOffset ) {
    relX = pageX - parentOffset.left;
    relY = pageY - parentOffset.top; 
  } else {
    var offset = $ele.offset()
    relX = pageX - offset.left;
    relY = pageY - offset.top; 
  }
  
  return [relX, relY];
}

MouseDraw.prototype.getRelCoordinatesNoParent = function(e, $ele) {
  var parentOffset = $ele.offset(); 
  var pageX = (e.originalEvent.touches==null ? e.pageX : e.originalEvent.touches[0].pageX);
  var pageY = (e.originalEvent.touches==null ? e.pageY : e.originalEvent.touches[0].pageY);
  
  /*  
  myLog("parentOffset : "+parentOffset.left + "," + parentOffset.top);
  myLog("TYPE : "+ e.type);
  myLog("ORIGINAL EVENT  : "+ e.originalEvent);
  myLog("TOUCHES : "+ (e.originalEvent.touches==null ? "No hay" : "Hay " + e.originalEvent.touches.length));
  myLog("PAGE X: "+ pageX);
  myLog("PAGE Y: "+ pageY);
  */
  
  //or $(this).offset(); if you really just want the current element's offset
  var relX = pageX - parentOffset.left;
  var relY = pageY - parentOffset.top; 
  
  return [relX, relY];
}

MouseDraw.prototype.setButton4Paint = function(button4Paint) {
	this.button4Paint = button4Paint;
}

MouseDraw.prototype.setButton4Move = function(button4Move) {
	this.button4Move = button4Move;
}


// ------------------------------------------------------------ Métodos Públicos
/**
 * Lanza eventos.
 * En la parte cliente
 * <lienzo>.bind("painting|moving|....", [this], function(evt, punto) {
 *   var myself = evt.data[0];
 * }); 
 */
MouseDraw.prototype.render = function() {
	this.isDrawing = false;

  // Si salimos, cancelamos
	/*
  if ( this.stopWhenLeave ) {
    this.$lienzo.bind("mouseleave", [this], function(evt) {
        var myself = evt.data[0];
        myself.mode=null;      
    });
  }
	*/
  // START 
  this.$lienzo.bind("mousedown touchstart", [this], function(evt) {
      evt.preventDefault();
      var myself = evt.data[0];

      var punto  = myself.getRelCoordinates(evt, $(this));
      myself.lastPoint = punto;
      
      // Inicio del Move (evt.button==null if touchevent)
      // @todo better for touch events
    	if( evt.button==null || evt.button == myself.button4Move) {
    	  myself.mode=MouseDraw.MODE_MOVE;
    	  myself.$lienzo.trigger("startMove", [punto]);
      // Inicio del Paint       
      } else if( evt.button == myself.button4Paint ) {
    		myself.mode=MouseDraw.MODE_PAINT;
    	  myself.$lienzo.trigger("startPaint", [punto]);
      }
  });
  
  // END
  this.$lienzo.bind("mouseup mouseleave touchend", [this], function(evt) {
      evt.preventDefault();
      var myself = evt.data[0];

      myLog("XXend");
      var punto  = myself.getRelCoordinates(evt, $(this));
      var delta = null;

      // Sólo tiene sentido si he hecho un start 
      if ( myself.lastPoint ) {
        delta  = [myself.lastPoint[0]-punto[0], myself.lastPoint[1]-punto[1]];
        myself.lastPoint = punto;
      }

      switch (myself.mode) {
      case MouseDraw.MODE_MOVE:
    	  myself.$lienzo.trigger("endMove", [punto, delta]);
        break;
      case MouseDraw.MODE_PAINT:
    	  myself.$lienzo.trigger("endPaint", [punto, delta]);
        break;
      }
      myself.mode=null;   
  });
  
  // MOVING/PAINTING
  this.$lienzo.bind("mousemove touchmove", [this], function(evt) {
      evt.preventDefault();
      var myself = evt.data[0];

      myLog("XXmove"+(new Date().getTime()));
      // Simulamos un startMove
      /* @todo: REVIEW
      if ( myself.isTouchDevice && myself.mode==null) {
        var punto  = myself.getRelCoordinates(evt, $(this));
        myself.lastPoint = punto;
        myself.mode=MouseDraw.MODE_MOVE;
        myself.$lienzo.trigger("startMove", [punto]);
        return;  
      }
      */
      if ( myself.mode==null ) return;
      var punto  = myself.getRelCoordinates(evt, $(this));
      var delta = null;
      // Sólo tiene sentido si he hecho un start 
      if ( myself.lastPoint ) {
        delta  = [myself.lastPoint[0]-punto[0], myself.lastPoint[1]-punto[1]];
        myself.lastPoint = punto;
      }
      myLog("MODE " + myself.mode);
      
      switch (myself.mode) {
      case MouseDraw.MODE_MOVE:
        myLog("TRIGGER moving " + punto + "," + delta + "||||");
    	  myself.$lienzo.trigger("moving", [punto, delta]);
        break;
      case MouseDraw.MODE_PAINT:
    	  myself.$lienzo.trigger("painting", [punto, delta]);
        break;
      }
  });
}
