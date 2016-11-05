/**
 * Utilities for images
 */
UtilImg = {};

/**
 * Scale an image and returns the data as base64 encoded
 * @param originalImg Objecy Image
 */
UtilImg.scale = function(originalImg, pNewW, pNewH, imgFormat) {
    // ----------------------------------- Calculate the new dimesions
    // This are the actual dimensions of the image
    var originalW = originalImg.width;
    var originalH = originalImg.height;
    
    // Now we want to calculate the new dimensions
    var newW = pNewW;
    var newH = pNewH;
    
    // If only one dimension is specified, we have to scale
    if ( !newH ) {
      newH = originalH*newW/originalW;
    } else if ( !newW ) {
      newW = originalW*newH/originalH;
    }
    console.log('newW : ' + newW + ', newH : ' + newH);  
    
    // ---------------------------------------------- Draw in a canvas
    var canvas = document.createElement('canvas');
    canvas.width = newW;
    canvas.height = newH;
    var ctx = canvas.getContext("2d");
    ctx.drawImage(originalImg, 0, 0, newW, newH);
    
    var imageResized = new Image();
    
    return canvas.toDataURL(imgFormat ? imgFormat : "image/png");
}
/**
 * Resize an image base64 encoded
 */
UtilImg.scaleBase64 = function(originalImgBase64, pNewW, pNewH, imgFormat, onDone) {
  var img = new Image();
  img.onload = function() {
    onDone(UtilImg.scale(this, pNewW, pNewH, imgFormat));
  };
  img.src = originalImgBase64;
}

/**
 * Convert an image base64 encoded into image object
 */
UtilImg.base642Img = function(imgBase64Encoded) {
  var img = new Image();
  img.src = imgBase64Encoded;

  return img;
}

UtilImg.img2base64 = function(img, fFilter, fFilterGlobal) {
  // ----------------------------------- Calculate the new dimesions
  // This are the actual dimensions of the image
  var imgW = img.width;
  var imgH = img.height;
  //console.log('[UtilImg.img2base64] imgW:' + imgW + ', imgH:' + imgH + ', imgSrc:' + img.src);
  
  // ---------------------------------------------- Draw in a canvas
  var canvas = document.createElement('canvas');
  canvas.width = imgW;
  canvas.height = imgH;
  var ctx = canvas.getContext("2d");
  // Apply filter
  if ( fFilter ) {
    // Build a back canvas  
    var back = document.createElement('canvas');
    var backcontext = back.getContext('2d');
    back.width = imgW;
    back.height = imgH;

    // First, draw the image into the backing canvas
    backcontext.drawImage(img,0,0,imgW,imgH);
    
    // Grab the pixel data from the backing canvas
    var idata = backcontext.getImageData(0,0,imgW,imgH);
    var data = idata.data;
    
    // Loop through the pixels, applying a filter
    for(var i = 0; i < data.length; i+=4) {
      var r = data[i+0];
      var g = data[i+1];
      var b = data[i+2];
      var a = data[i+3];
      
      var newData = fFilter(r, g, b, a);
      for(var j=0; j<4; ++j) {
        data[i+j] = newData[j];
      }
    }
    idata.data = data;
    
    // Draw the pixels onto the visible canvas
    ctx.putImageData(idata,0,0);
  // Just filter  
  } else {
    // @todo : ahora fFilter y fFilterGlobal son exclusivos
    if ( fFilterGlobal ) {
      alert('Not implemented');
    } else {
      ctx.drawImage(img, 0, 0, imgW, imgH);
    }
  }
  
  return canvas.toDataURL();
}

UtilImg.cloneImg = function(img, fFilter, fFilterGlobal) {
  return UtilImg.base642Img(UtilImg.img2base64(img, fFilter, fFilterGlobal));
}

/**
 * Image Filters (pixel based)
 */
UtilFilterPixel = {};
UtilFilterPixel.blackWhite = function(r, g, b, a) {
  // The human eye is bad at seeing red and blue, so we de-emphasize them.
  var avg = 0.2126*r + 0.7152*g + 0.0722*b;
  //var avg = (r + g + b)/3;
  return [avg, avg, avg, a];
};
UtilFilterPixel.identity = function(r, g, b, a) {
  return [r, g, b, a];
};
UtilFilterPixel.transparent50 = function(r, g, b, a) {
  return [r, g, b, 50];
};

/**
 * Image Filters (global image)
 * http://www.html5rocks.com/en/tutorials/canvas/imagefilters/
 */
UtilFilterImg = {};
UtilFilterImg.grayscale = function(pixels, args) {
  var d = pixels.data;
  for (var i=0; i<d.length; i+=4) {
    var r = d[i];
    var g = d[i+1];
    var b = d[i+2];
    // CIE luminance for the RGB
    // The human eye is bad at seeing red and blue, so we de-emphasize them.
    var v = 0.2126*r + 0.7152*g + 0.0722*b;
    d[i] = d[i+1] = d[i+2] = v
  }
  return pixels;
};

// Upload all images
/*
UtilImg.uploadImages($container, asynchFunction, onDone) {
  var $collection = $container.find('img').filter(function(){
    return $(this).attr('src').indexOf('data:')==0;
  });
  // Resize all the images (this is an asynch process)
  callAsychFunction($collection, asynchFunction, onDone);
  callAsychFunction($collection, asynchFunction, onDone);
}
*/