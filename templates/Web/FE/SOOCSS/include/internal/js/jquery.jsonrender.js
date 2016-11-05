/**
 * @todo : pasar a plugin de jquery
 */

// When this becomes a jQuewry plugin, that could be an internal property
var JSON_RENDER_IS_DEBUG = false;

// ----------------------------------------------------------------------------- 
// _putDataInField
// ----------------------------------------------------------------------------- 
/**
 * Store a certain value in a a group of fields
 * dataAreErrors : if true, value represents an error, instead a field value
*/
// IL - 04/02/15 - Added options
function _putDataInField($fields, value, key, dataAreErrors, $pContainerErrors, options) {
  // No field, no data!
  if ( $fields.length==0 ) return;

  // Podríamos tener varios elementos, de naturaleza diversa
  $fields.each(function() {
    var $field = $(this);
    
    // If fact, this is used only for the checkboxes 
    if ( $field.data('jsonrender-rndID') ) {
      $field.attr('name', $field.attr('name') + '[' + $field.data('jsonrender-rndID') + ']');
      $field.removeData('jsonrender-rndID');
    }

    if ( dataAreErrors ) {
      // IL - 27/01/15 - Avoid marks as error elements container as div,....
      if ( $field.children().length==0 ) {
        $field.addClass('_error');
      }
      if ( $pContainerErrors ) {
        $tmplError = $pContainerErrors.find('._template');
        // IL - 27/01/15 - Avoid duplicated error messages
        if ( $pContainerErrors.children().filter(function(){ return $(this).html()==value;}).length==0 ) {
          $divError = $tmplError.length==0 ? $('<div></div>') : $tmplError.clone(true, true).removeClass('_template').addClass('_templateGenerated');
          $divError.html(value);
          $pContainerErrors.append($divError);
        }
      }
    } else {
      // IL - 04/02/15 - If we have already a value and options say ignore fields
      // with a value already set .... ignore
      if ( $field.attr('value') && options && options['notFillIfAlreadyHaveValue'] ) {
        return true;
      }
      
      // Keep the original value
      // This is used by jsonform for example with file and passwords fields
      // To create this data attribute instead to keep the value using $ele.val(<value>)
      // is because in some cases (feg. the files), $ele.val() always return empty, so 
      // the only way I've found to keep the original value is using data
      $field.data('originalValue', value);

      // Image
      if ( $field.is('img') ) {
        $field.attr('src', value);        
      // Sound
      } else if ($field.is('source')) {
        $field.attr('src', value);
      // Input field
      } else if ( $field.is('input') || $field.is('select') || $field.is('textarea')) {
        // Es un checkbox
        if ( $field.is(':checkbox') ) {
          // IL - 09/09/13 - Lo de los checkboxes no acaba de funcionar....
          // No establecemos el valor, porque si lo hacemos val()
          // SIEMPRE nos devolverá ese valor, INDEPENDIENTEMENTE de si está check o no.
          /*
          // Checked
          if ( value!=null && (value=='S' || value=='s' || value=='Y' || value=='y' || value=='1') ) {
            $field.attr('checked','checked');
            // Not checked
          } else {
            $field.removeAttr('checked');
          }
          */
          // Ver si checkbox está actiavdo o no
          if ( JSON_RENDER_IS_DEBUG ) {
            console.log(
                'fieldName : '       + $field.attr('name') + 
                ', fieldValue : '    + $field.val() + 
                ', isValueArray? '   + $.isArray(value) + 
                ', isValueInArray? ' + $.inArray($field.val(), value) +
                ', value : '         + value
            );
          }
          if ( !$.isArray(value) && value==$field.val() || $.inArray($field.val(), value)!=-1 ) {
            $field.attr('checked','checked');
          }
        // Radio button
        } else if ( $field.is(':radio') ) {
          if ( value==$field.val() ) {
            $field.attr('checked','checked');
          }
        // IL - 31/01/15 - add change() so the event is thrown
        } else if ( !$field.is(':file') ) {
          // NOTE : In the selects, it they still do not have the options (because
          // they are filled in using AJAX), if a set a value that it is still not
          // present, $field.val()=null
          // To obtain the valu ise (see above) .data('originalValue')
          $field.val(value).change();
        }
      //Link
      } else if ($field.is('a')) {
        var href = $field.attr('href');
        // IL - 01/10/13 - If it already have a value, append (fex. it can be the base url)
        if ( href && href.trim().length!==0) {
          $field.attr('href', href + value);
        } else {
          $field.attr('href', value);
        }
      // Other
      } else {
        // IL - 29/10/13 - Don't put if there are children
        if ( $field.children().length==0 ) {
          //$field.html(value);
          $field.html(value.toHtmlEntities());
        }
      }
    } // dataAreErrors
  });
}

// ----------------------------------------------------------------------------- 
// fillData 
//
// ¿Obsoleta (v. jquery.jsonform.js)?
// ----------------------------------------------------------------------------- 
/**
 * Rellena una serie de campos HTML con los datos que en un mapa de datos JS.
 * 
 * Argumentos:
 * - pData    : Mapa de datos JS; o sea, parejas key/value 
 *              Pej.{ "name : "Pepe", "apellidos" : "Luis García" }
 * - pPrefix  : (Opcional) Para evitar conflictos con los IDs de los HTML, prefijo
 *              utilizado para convertir del key de los datos al ID del HTML.
 *              Pej. 'cliente_'
 *
 * Supongamos que los datos de una persona son 'name' y 'apellidos'. En una paǵina
 * tenemos el detalle de dos personas: cliente y proveedor. El HTML de ambos bloques
 * sería
 *   <div id="detalle_cliente">
 *     <div id="cliente_name"/>        -> Aquí va el campo 'name'. Se usa el prefijo 'cliente_' para diferenciarlo de 'proveedor'
 *     <div id="cliente_apellidos"/>   -> Idem apellidos
 *   </div>
 *   <div id="detalle_proveedor">
 *     <div id="proveedor_name"/>       
 *     <div id="proveedor_apellidos"/>  
 *   </div>
 * Los datos que tengo son (pej. los obtengo de una llamada AJAX):
 *   var datos_cliente   = { "name" : "Pepe", "apellidos" : "Luis"};
 *   var datos_proveedor = { "name" : "Juan", "apellidos" : "García"};
 * Para rellenar los datos:
 *   fillData("detalle_cliente", datos_cliente, "cliente_");
 *   fillData("detalle_proveedor", datos_proveedor, "proveedor_"); 
 */
function fillData($container, pData, pPrefix) {
  var prefix = pPrefix ? pPrefix : "";
  
  for(var key in pData) {
    var value = pData[key]==null ? '' : pData[key];
    _putDataInField($container.find('#'+ prefix + key ), value);
    _putDataInField($container.find('.'+ prefix + key ), value);
    _putDataInField($container.find('input[name="'+ prefix + key + '"]'), value);
  }  
}

// -----------------------------------------------------------------------------
// loadFillData
// -----------------------------------------------------------------------------
/**
 * Idem qie fillData(), donde los datos vienen de una llamada AJAX.
 *
 * Argumentos:
 * - pUrl     : URL del endpoint AJAX. Los datos que devuelve la llamada es la estructura
 *              de datos JS.
 *              Pej. 'getDatosPersona.jsp?id=123'
 * - pPrefix  : V. fillData() 
 */
function loadFillData(pUrl, pPrefix) {
  $.getJSON(pUrl,function(json){
      fillData(json, pPrefix);        
  }); 
}

// -----------------------------------------------------------------------------
// renderList
//
// NOTE : This is the old version, kept for compatibility
// -----------------------------------------------------------------------------
function renderList($pContainer, pData, pCallbackRow, pCallbackTable, throwEventWhenCreateTemplateGenerated) {
  // Clean
  // @todo : is not working 
  if ( !pData ) {
    $pContainer.find("._templateGenerated").remove();            
  // Fill Data
  } else {
    // data is an ARRAY
    if ( $.isArray(pData) ) {
      if ( JSON_RENDER_IS_DEBUG ) console.log('ARRAY');
      var $rowTmpl=$pContainer.find("._template:first");
      
      if ( JSON_RENDER_IS_DEBUG ) console.log('Is array, loop over its elements');

      // Loop over all the lines
      $.each(pData, function(ind, rowData) {
        if ( JSON_RENDER_IS_DEBUG ) console.log('Array. ind=' + ind + ', rowData=' + rowData + ', $rowTmpl found? ' + $rowTmpl.length);
        if ( JSON_RENDER_IS_DEBUG ) console.log('container : ' + $pContainer.attr('class'));
        
        var $row = $rowTmpl.clone(true, true).removeClass("_template").addClass("_templateGenerated");
        // FIXME : Is that true?
        // It seems the data is already copied with clone
        if ( $rowTmpl.siblings('._templateGenerated').length==0 ) {
          if ( JSON_RENDER_IS_DEBUG ) console.log('Creating array. Thera are not generated');
          $rowTmpl.after($row);//.data($row.data());
        } else {
          if ( JSON_RENDER_IS_DEBUG ) console.log('Creating array. Thera are generated');
          $rowTmpl.siblings('._templateGenerated:last').after($row);//.data($row.data());
        }
        
        // Fill this row
        if ( JSON_RENDER_IS_DEBUG ) console.log('Is a line, fill ' + $row + ' with ' + rowData);
        renderList($row, rowData, pCallbackRow, null, throwEventWhenCreateTemplateGenerated); 
        if ( pCallbackRow ) {
          pCallbackRow($row, rowData, ind);
        }
        /*
        === SAMPLE ===
        To read the data:
        $('._template).bind('custom.rowCreated', function(evt, $row, rowData, ind){
        ...
        });
        */
        
        if ( typeof throwEventWhenCreateTemplateGenerated == 'function' ) {
          throwEventWhenCreateTemplateGenerated($row, rowData, ind);
        } else {
          if ( throwEventWhenCreateTemplateGenerated ) {
            if ( JSON_RENDER_IS_DEBUG ) console.log('>>>>> trigger(custom.rowCreated) : ' + $rowTmpl.attr('class'));
            $rowTmpl.trigger("custom.rowCreated", [$row, rowData, ind]);
          }
        }
      });
    // pData represents an object (that can contain arrays inside!)  
    } else {
      //$.each(pData, function(key, val) {
      for(var key in pData ) {
        var val = pData[key];
        // val is an OBJECT (that includes an array)
        if ( typeof val == 'object'  ) {
          if ( JSON_RENDER_IS_DEBUG ) console.log('OBJECT ' + key);
          // Use first to avoid take the wrong group if there are several groups
          // with the same name 'anidados'
          // @todo : now we select only one, it does not work if there are several
          // groups atr the same level with the same name.
          renderList($pContainer.find('.' + key + ':first'), val, pCallbackRow, null, throwEventWhenCreateTemplateGenerated); 
        // val is a SIMPLE VALUE
        } else {
          if ( JSON_RENDER_IS_DEBUG ) console.log('SIMPLE VALUE. key : ' + key + ', typeof key : ' + (typeof key) + ', val : ' + val + '.');
          // If key==0, is because is an array
          if ( key=='0') {
            $pContainer.html(val);
          } else {
            // Fill the element : Super todo
            // Is not an input element
            $pContainer.find('#' + key + ':not(img)').html(val);
            $pContainer.find('.' + key + ':not(img)').html(val);
            
            // It is an input element
            $pContainer.find('#' + key + ':not(img)').val(val);
            $pContainer.find('.' + key + ':not(img)').val(val);
            $pContainer.find('[name="' + key + '"]' + ':not(img)').val(val);
            
            // It is an image
            $pContainer.find('img#' + key).attr('src',val);
            $pContainer.find('img.' + key).attr('src',val);
          }
        }
      }
      //});
    }
  }

  if ( pCallbackTable ) {
    pCallbackTable($pContainer, pData);
  }
}

function url2List($pContainer, url, pCallbackRow, pCallbackTable) {
  $.getJSON(url, function(data) {
    renderList($pContainer, null);
    renderList($pContainer, data, pCallbackRow, pCallbackTable);
  });
}

// -----------------------------------------------------------------------------
// renderData
//
// NOTE : This is the NEW version.
// options:
// - notFillIfAlreadyHaveValue : true, not set the value
// -----------------------------------------------------------------------------
// IL - 04/02/15 - Added options where to put all the aditional options
function renderData($pContainer, pData, pCallbackRow, pCallbackTable, throwEventWhenCreateTemplateGenerated, dataAreErrors, $pContainerErrors, options) {
  // Clean
  // @todo : is not working 
  if ( !pData ) {
    $pContainer.find("._templateGenerated").remove();            
  // Fill Data
  } else {
    // --------------------------
    // data is an ARRAY
    // --------------------------
    if ( $.isArray(pData) ) {
      if ( JSON_RENDER_IS_DEBUG ) console.log('ARRAY');
      var $rowTmpl=null;
      if ( $pContainer.hasClass("_template") ) {
        $rowTmpl=$pContainer;
      } else {
        $rowTmpl=$pContainer.find("._template:first");
      }
      // Ooooooh, no hemos encontrado un template :-(
      if ( $rowTmpl==null || $rowTmpl.length==0 ) {
        if ( JSON_RENDER_IS_DEBUG ) console.log('Is array BUT not found a _template');
      } else {
        if ( JSON_RENDER_IS_DEBUG ) console.log('Is array, loop over its elements. pContainer:' + $pContainer.get(0)+ ', rowTmpl : ' + $rowTmpl.get(0));
        
        // Loop over all the lines
        $.each(pData, function(ind, rowData) {
          if ( JSON_RENDER_IS_DEBUG ) console.log('Array. ind=' + ind + ', rowData=' + rowData + ', $rowTmpl found? ' + $rowTmpl.length);
          
          var $row = $rowTmpl.clone(true, true).removeClass("_template").addClass("_templateGenerated");
          
          // With the radio buttons + repeated elements we have a problem: if 
          // the name is always de same, only one radio among ALL the repeated 
          // elements can be selected. To solve that, we must change the name
          // We can not change NOW the name because then we won't be able to 
          // find them for putting the value, but we will just mark them 
          var rndID = Math.round(new Date().getTime() + (Math.random() * 100));
          $row.find(':radio').each(function(){
            $(this).data('jsonrender-rndID', rndID);
          });
          
          // FIXME : Is that true?
          // It seems the data is already copied with clone
          if ( $rowTmpl.siblings('._templateGenerated').length==0 ) {
            if ( JSON_RENDER_IS_DEBUG ) console.log('Creating array. Thera are not generated');
            $rowTmpl.after($row);//.data($row.data());
          } else {
            if ( JSON_RENDER_IS_DEBUG ) console.log('Creating array. Thera are generated');
            $rowTmpl.siblings('._templateGenerated:last').after($row);//.data($row.data());
          }
          
          // Fill this row
          if ( JSON_RENDER_IS_DEBUG ) console.log('Is a line, fill ' + $row + ' with ' + rowData);
          // IL - 04/02/15 - Added options
          renderData($row, rowData, pCallbackRow, null, throwEventWhenCreateTemplateGenerated, dataAreErrors, $pContainerErrors, options); 
          
          // Notify that the row has been created. 
          
          // NOTE : Actually it is a few confusing, because we have THREE
          // different ways the caller can receive a 'row' is created:
          // - function pCallbackRow()
          // - function throwEventWhenCreateTemplateGenerated
          // - throwEventWhenCreateTemplateGenerated=true => This is the preferend method
          if ( pCallbackRow ) {
            pCallbackRow($row, rowData, ind);
          }
          
          if ( typeof throwEventWhenCreateTemplateGenerated == 'function' ) {
            throwEventWhenCreateTemplateGenerated($row, rowData, ind);
          } else {
            // THIS IS THE PREFERED METHOD
            if ( throwEventWhenCreateTemplateGenerated ) {
              if ( JSON_RENDER_IS_DEBUG ) console.log('>>>>> trigger(custom.rowCreated) : ' + $rowTmpl.attr('class'));
              /* Trigger the event attached to the _template element; to get
               * it
               * $('._template).bind('custom.rowCreated', function(evt, $row, rowData, ind){...}
               */
              $rowTmpl.trigger("custom.rowCreated", [$row, rowData, ind]);
              
            }
          }
        });
      } // template found 
    // ----------------------------------------
    // pData represents an object (that can contain arrays inside!)  
    // ----------------------------------------
    } else {
      //$.each(pData, function(key, val) {
      for(var key in pData ) {
        // OJO : Si val==null es tratado como un objeto, que no nos intersa
        var val = pData[key]==null ? '' : pData[key];
        // val is an OBJECT (that includes an array)
        // BUT we exlude arrays of single values
        if ( typeof val == 'object'  && (!$.isArray(val) || val.length==0 || typeof val[0] == 'object') ) {
          if ( JSON_RENDER_IS_DEBUG ) console.log('val "' + val +'" of type OBJECT with key "' + key + '" -> found html group : ' + $pContainer.find('.' + key + ':first').get(0));
          // Use first to avoid take the wrong group if there are several groups
          // with the same name 'anidados'
          // @todo : now we select only one, it does not work if there are several
          // groups atr the same level with the same name.
          // @todo : instead class maybe we can use the data 'jsonform-group'
          // IL - 04/02/15 - Added options
          renderData($pContainer.find('.' + key + ':first'), val, pCallbackRow, null, throwEventWhenCreateTemplateGenerated, dataAreErrors, $pContainerErrors, options); 
        // val is a SIMPLE VALUE or an array of single values
        } else {
          if ( JSON_RENDER_IS_DEBUG ) console.log('SIMPLE VALUE. key : ' + key + ', typeof key : ' + (typeof key) + ', val : ' + val + '.');
          
          // If key==0, is because is an array
          if ( key=='0') {
            //$pContainer.html(val);
            _putDataInField($pContainer, val, key, dataAreErrors, $pContainerErrors);
          } else {
            // IL - 04/02/15 - Added options
            // Fill the element with the data
            _putDataInField($pContainer.find('#' + key), val, key, dataAreErrors, $pContainerErrors, options);
            _putDataInField($pContainer.find('.' + key), val, key, dataAreErrors, $pContainerErrors, options);
            // IL - 29/09/13 - To include fex. textarea
            // _putDataInField($pContainer.find("select[name=" + key + "], input[name=" + key + "]"), val, key);
            _putDataInField($pContainer.find("[name=" + key + "]"), val, key, dataAreErrors, $pContainerErrors, options);
          }
        }
      }
    }
  }

  if ( pCallbackTable ) {
    pCallbackTable($pContainer, pData);
  }
}

/**
 * Show the errors
 */
function renderDataErrors($pContainer, errors, $pContainer4Errors) {
  //alert("Found errors!");
  // Remove all fields marked with a previous errors
  if ( $pContainer ) {
    $pContainer.find('._error').removeClass('_error');
  }
  // Remove all the previous messages
  if ( $pContainer4Errors) {
    // There is template
    if ( $pContainer4Errors.find('._template').length!=0 ) {
      $pContainer4Errors.find('._templateGenerated').remove();
    // No template, just remove all the children
    } else {
      $pContainer4Errors.children().remove();
    }
  }
  
  // Mark all the fields with errors and show the error messages
  renderData($pContainer, errors, null, null, null, true, $pContainer4Errors);
}

