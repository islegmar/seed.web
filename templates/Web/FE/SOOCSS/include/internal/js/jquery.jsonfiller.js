/**
 * @todo : pasar a plugin de jquery
 */
function renderList($pContainer, pData, pCallbackRow, pCallbackTable, throwEventWhenCreateTemplateGenerated) {
  // Clean
  // @todo : is not working 
  if ( !pData ) {
    $pContainer.find("._templateGenerated").remove();            
  // Fill Data
  } else {
    // data is an ARRAY
    if ( $.isArray(pData) ) {
      // console.log('ARRAY');
      var $rowTmpl=$pContainer.find("._template:first");
      
      //console.log('Is array, loop over its elements');

      // Loop over all the lines
      $.each(pData, function(ind, rowData) {
        console.log('Array. ind=' + ind + ', rowData=' + rowData + ', $rowTmpl found? ' + $rowTmpl.length);
        
        var $row = $rowTmpl.clone(true, true).removeClass("_template").addClass("_templateGenerated");
        // FIXME : Is that true?
        // It seems the data is already copied with clone
        if ( $rowTmpl.siblings('._templateGenerated').length==0 ) {
          // console.log('Creating array. Thera are not generated');
          $rowTmpl.after($row);//.data($row.data());
        } else {
          // console.log('Creating array. Thera are generated');
          $rowTmpl.siblings('._templateGenerated:last').after($row);//.data($row.data());
        }
        
        // Fill this row
        // console.log('Is a line, fill ' + $row + ' with ' + rowData);
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
            // console.log('>>>>> trigger(custom.rowCreated) : ' + $rowTmpl.attr('class'));
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
          // console.log('OBJECT ' + key);
          // Use first to avoid take the wrong group if there are several groups
          // with the same name 'anidados'
          // @todo : now we select only one, it does not work if there are several
          // groups atr the same level with the same name.
          renderList($pContainer.find('.' + key + ':first'), val, pCallbackRow, null, throwEventWhenCreateTemplateGenerated); 
        // val is a SIMPLE VALUE
        } else {
          //console.log('SIMPLE VALUE. key : ' + key + ', typeof key : ' + (typeof key) + ', val : ' + val + '.');
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
