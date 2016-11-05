/**
 * data values used:
 * - jsonform-group : groupName
 * A jQuery plugin boilerplate.
 * Author: Jonathan Nicol @f6design
 * http://f6design.com/journal/2012/05/06/a-jquery-plugin-boilerplate/
 */
;(function($) {
  // Change this to your plugin name.
  var pluginName = 'jsonform';
 
  /**
   * Plugin object constructor.
   * Implements the Revealing Module Pattern.
   */
  function Plugin(element, options) {
    // References to DOM and jQuery versions of element.
    var el = element;
    var $el = $(element);

    // Extend default options with those supplied by user.
    options = $.extend({
      'classTemplate' : '_template',
      'classTemplateGenerated' : '_templateGenerated',
      'classButtonAdd' : 'bAdd',
      'classButtonDel' : 'bDel',
      'preSave'        : null,
      /* IL - 24/10/13 - This should be done by preSave, but to be sure we 
       * create another parameter. This adds data just before submit
       */
      'addDataBeforeSubmit' : null,
      'cbSave'         : null,
      // IL - 07/03/14 - Removed the default handler. If a default handler
      // is needed, put somewhere in the code
      // $( document ).ajaxError(function(  event, jqxhr, settings, exception ) {
      //   var errorAsString = jqxhr.responseText;
      // }); 
      'onSaveError'    : null, /*function() { alert('Error on submit'); },*/
      'throwEventWhenCreateTemplateGenerated' : false,
      /* IL - 08/09/13 - Make optional the creation an empty element for the 
       * repeated elements. */
      'createEmptyRepeatedElement' : true,
      /* IL - 01/10/13 - Make optional create all add/remove buttons */
      'createAddDelButtons' : true,
      /* If not null, we will upload the files to this URL */
      'url2UploadFiles' : null,
      /* 
       If not null, it is the name of the data property that contains the 
       checks we perform to the selected file 
       *********** WARNING ***********
       Actually, if we peform some checks before we upload a file, we DO NOT
       use this property but create a data attribute (search  jsonfom-fieldcfg)
       We keep the code related with this property because it contains some things
       maybe we want to do later (as image resize)
       */
      'checkFilePropDataName' : null,
      /* IL - 24/10/13 - Upload the new images. The signature of the function is:
       *    fUploadImages($img, onDone) 
       * where onDone() is the function that must be called when the upload is done
       */
      'fUploadImages' : null,
      /* IL - 05/02/14 */
      'debug' : false,
      /* IL - 12/03/14 - If true, use last _templeteGenerated when duplicate */
      'useGeneratedAsTemplate' : false,
      /* IL - 28/01/15 - Try to validate using the client browser (HTML5) submitting
      the form. In this case, we have a flag to avoid infinite loops because we
      capture the submit event. */
      'validateFormUsingClientBrowser' : false,
      'isSubmitting' : false,
      /* IL - 04/02/15 - For the password fields use the hash (for sending) */
      'hash4PwdFields' : false
    }, $.fn[pluginName].defaults, options);
 
    /**
     * Initialize plugin.
     */
    function init() {
      if ( options.debug ) console.log("jsonform.init()");

      /**
       * Prepare the form:
       * - Create groups
       * - Add ADD/DEL buttons
       * - ...
       */
      if ( options.createAddDelButtons ) {
        var addButtons=[];
        $el.find("." + options.classTemplate).each(function(){
          if ( options.debug ) console.log("Find template " +this);

          var $thisTmpl = $(this);
          
          // -------------------------------------------------------- Del button
          // IL - 21/02/14 - Search for a bDel button NOT inside a template.
          // If not found, create one
          // @todo : I have tried a lot of different queries (the problem is 
          // with nested _template) without any success, so I have to do it
          // this way :-(
          var tmpList = [];
          filterDeep($thisTmpl, tmpList, function($ele){
            return $ele.hasClass(options.classButtonDel) ? 1 : 0;
          });
       
          if ( tmpList.length==0) {
            $bDel = $('<button type="button" class="' + options.classButtonDel +'"></button>');
            $thisTmpl.append($bDel);
          } else {
            $bDel = tmpList[0];
          }

          // When click, delete the _templateGenerated element
          $bDel.click(function(evt){
            var $this = $(this);
            
            // Try to find the container
            var $container = $this.closest('.' + options.classTemplateGenerated);
            // Not found, use "the old way"
            if ( $container.length!=1 ) {
              $container = $this.parent();
            }
            
            // Remove
            $container.remove();
          });
          
          // -------------------------------------------------------- Add button
          // Add a ADD button AFTER the repeated blocks
          // IL - 21/02/14 - Not add if the add button already exists
          // We have the same problems with nested _template as in bDel
          tmpList = [];
          filterDeep($thisTmpl.parent(), tmpList, function($ele){
            return $ele.hasClass(options.classButtonAdd) ? 1 : 0;
          });
       
          if ( tmpList.length==0) {
            $bAdd = $('<button type="button" class="' + options.classButtonAdd + '"></button>');
            $thisTmpl.parent().append($bAdd);
          } else {
            $bAdd = tmpList[0];
          }
          
          $bAdd.bind('click', {$template:$thisTmpl}, function(evt){
            // Replicate the last block
            //var $template = evt.data.$template;
            // Find the template element to generate
            var $template = null ;
            // Try to use the last templateGenerated
            if ( options.useGeneratedAsTemplate ) {
              $template = $(this).prevAll("." + options.classTemplate).siblings('.' + options.classTemplateGenerated ).last();              
            } 
            // Use _template
            if ( $template==null || $template.length==0 ) {
              // NOT WORKING var $template = evt.data.$template;
              $template = $(this).prevAll("." + options.classTemplate);
            }
            var ind = $template.siblings('.' + options.classTemplateGenerated).length;
            
            // Create the new element
            var $new = 
              $template.
              clone(true, true).
              removeClass(options.classTemplate).
              addClass(options.classTemplateGenerated).
              data($template.data());
            // With the radio buttons + repeated elements we have a problem: if 
            // the name is always de same, only one radio among ALL the repeated 
            // elements can be selected. To solve that, we must change the name
            var rndID = Math.round(new Date().getTime() + (Math.random() * 100));
            $new.find(':radio').each(function(){
              var $this = $(this);
              $this.attr('name', $this.attr('name') + '[' + rndID + ']');
            });
            if ( $template.siblings('.' + options.classTemplateGenerated).length>0 ) {
              $template.siblings('.' + options.classTemplateGenerated+':last').after($new);
            } else {
              $template.after($new);
            }
            
            if ( options.throwEventWhenCreateTemplateGenerated ) {
              $template.trigger("custom.rowCreated", [$new, null, ind]);
            }
  
          });
  
          // Calcula el nivel de profundidad del Add ¿Cuantos _template hay encima?
          var level = $bAdd.parents("." + options.classTemplate).length;  
          addButtons.push({ level : level, $bAdd : $bAdd});
        });

        // Create one element at least
        // Click on Add elements from inside to outside!!
        if ( options.createEmptyRepeatedElement ) {
          if ( options.debug ) console.log('# add buttons : ' + addButtons.length);
          var sortedButtons = addButtons.sort(function(a,b){return b.level-a.level});
          $.each(sortedButtons, function(ind, ele){
            ele.$bAdd.trigger('click');
          });
        }
      }
      
      // IL - 03/03/15 - Alow also button for submit
      $el.find("input[type='submit'], button[type='submit']").click(function(evt){
        // IL - 28/01/15 - In case validateFormUsingClientBrowser==true we can 
        // have an infinite loop because in submitForm() we are going to submit
        // again the form, so the browser shows all the client side errors!
        if ( options.validateFormUsingClientBrowser ) {
          if ( !options.isSubmitting ) {
            evt.preventDefault();
            submitForm();
          } else {
            options.isSubmitting=false;
          }
        // Normal flow
        } else {
          // Don't perform the real submit. We're sending the data as JSON via POST
          evt.preventDefault();
          submitForm();
        } 
      });
      
      // If this form is going to process files
      if ( options.checkFilePropDataName!=null  ) {
        $el.find(':file').change(function(){
          var $file = $(this);
          var fileChecks = $file.data(options.checkFilePropDataName);
          // We have defined some checks to that file
          if ( fileChecks ) {
            // Info about the file
            var file = this.files[0];
            // Errors in the file (invalid size, mimetype,...)
            var errors = '';
            
            // Check the file's size
            if ( fileChecks.size ) {
              if ( file.size > fileChecks.size  ) {
                errors += 'Maximum size allowed is ' + fileChecks.size + ' and this file has ' + file.size + '. ';
              };
            }
            
            // Check the file's mimetype
            if ( fileChecks.mimetype ) {
              var mimetype = file.type;
              if ( !mimetype ) {
                errors += 'Unknown file type. ';
              } else {
                if ( $.inArray(mimetype, fileChecks.mimetype) ) {
                  errors += 'File type ' + mimetype + ' wrong, only allowed ' + fileChecks.mimetype.join() + '. ';
                }
              }
            }
            /*
            var name = file.name;
            */
            
            // There are errors : show a message and clear the input
            if ( errors.length!=0 ) {
              alert('File can not be uploaded. ' + errors);
              $file.val('');
            }
          }
        });
      }

      // To show the file name in the select box
      $el.find(':file').on("change", function() {
        var fileName = this.value.replace("C:\\fakepath\\", "");
        $(this).closest(".input-file").children(".input-file-name").text(fileName);
        $(this).closest(".input-file").children(".input-file-name").attr('title', fileName);
      });
      hook('onInit');
    }
    
    // ---------------------------------------------------------- Public Methods
    /**
     * Sumit the form
     */
    function submitForm() {
      var $bSubmit = $el.find("input[type='submit']");
      // IL - 03/03/15 - Alow also button for submit
      if ( $bSubmit.length==0 ) {
        $bSubmit = $el.find("button[type='submit']");  
      }

      if ( options.preSave ) {
        // Get the actual form data
        // @todo : we calcultate it here and AGAIN in the submit because
        // maybe the data has changed before the submit (upload files....)
        // Can we do it better?
        var json={};
        fillValues($el, json);
        data = JSON.stringify(json);
        
        // IL - 09/10/13 - Cancel submit if it returns false
        if ( !options.preSave(json, $el) ) {
          return;
        }
      }

      // IL -28/01/15 - After we have donew some validations/settings in preSave,
      // we're going to validate the form using the client side capabilities
      if ( options.validateFormUsingClientBrowser ) {
        if (!$el.get(0).checkValidity()) {
          // If the form is invalid, submit it. The form won't actually submit;
          // this will just cause the browser to display the native HTML5 error messages.
          options.isSubmitting=true;
          $el.find(':submit').click();
          return;
        }
      }
      
      // Read all files, send them to the server, and perform the submit
      if ( options.url2UploadFiles!=null ) {
        // Make an array with all the files that need to be uploaded
        var arrayFiles = new Array();
        $el.find(':file').each(function(){
          if ( this.files.length==1 ) {
            arrayFiles.push($(this));
          }
        });
        if ( options.debug ) console.log('>>>>> Vamos a subir ' + arrayFiles.length + ' ficheros');
        
        // Upload them and submit when done
        processFiles(arrayFiles,function(data){
          // There are some errors when processing the files!!!
          if ( data && data['errors'] ) {
            options.cbSave(data);
            return;
          } else {
            doSubmit($bSubmit);            
          }
        });
      } else {
        // Upload imaged
        if ( options.fUploadImages ) {
          // Search all the images which @src='data:....'
          var $collection = $el.find('img').filter(function(){
            return $(this).attr('src') && $(this).attr('src').indexOf('data:')==0;
          });
          
          /* Upload all the images */
          callAsychFunction(
              $collection, 
              options.fUploadImages,
              function() {
                doSubmit($bSubmit);
              }
          );
        } else {
          doSubmit($bSubmit);
        }
      }
    }
    
    /**
     * Return the form's data as JSON
     * This function is called recursive, with the groups
     */
    function fillValues($container, data, encodeValues) {
      // Step 1
      // Get MY input fields; that means input fields that are not inside a group
      var listInputFields=[];
      filterDeep($container,listInputFields, function($ele){
        if ( options.debug ) {
          console.log('Checking ele of type "' + $ele.prop('tagName') + 
              '" with class "' + $ele.attr('class') + '"');
        }
        
        // IL - 01/09/13 : Ignore all the _template sections
        // IL - 29/10/13 : Bug fixing, it was 'option.' instead 'options.'
        // IL - 30/10/13 : Ignore also inside _templateGenerated
        if ( options.classTemplate && $ele.hasClass(options.classTemplate) ) {
          if ( options.debug ) console.log('Ignoring ' + $ele.attr('class'));
          return -1;
        }
        
        if ( $ele.is('input') || $ele.attr('contenteditable') ) {
          if ( $ele.attr('contenteditable') ) {
            if ( options.debug ) console.log('YES, it has content editable');
            return 1;
          } else {
            var type = $ele.attr('type');
            
            if ( type!='submit' && type!='button' && type!='reset' && ( type!='file' || options.url2UploadFiles!=null) ) {
              return 1;
            } else {
              return -1;
            }
          }
        } else if ($ele.is('textarea')) {
          if ( options.debug ) console.log('YES, it is a textarea');
          return 1;
        // IL - 08/09/13 : Added the selects  
        } else if ($ele.is('select')) {
          if ( options.debug ) console.log('YES, it is a select');
          return 1;
        } else if ( $ele.data('jsonform-group') ) {
          return -1;
        } else {
          return 0;
        }
      });
      
      
      if ( options.debug ) console.log('We have found ' + listInputFields.length + ' input fields');
      // Loop over all the input fields we have found
      $.each(listInputFields,function(ind,$ele){
        var fieldName = $ele.attr('name');
        
        // IL - 30/10/13 - Ignore if there is no fieldName
        if ( !fieldName || fieldName.length==0 ) { return true; }
        
        if ( options.debug ) console.log('>>>> fieldName : ' + fieldName + ', fieldType : ' + $ele.attr('type') + ', contenteditable : ' + $ele.attr('contenteditable'));
        if ( $ele.attr('contenteditable')) {
          // IL - 30/10/13 - If image, the data is the src
          if ( $ele.is('img') ) {
            data[fieldName] = $ele.attr('src');
          } else {
            data[fieldName] = $ele.html();
          }
        // Special for radio buttons : we store only one value (not array)
        } else if ( $ele.is(':radio') ) {
          // Problema de los radio + repeated
          var indCorchete = fieldName.indexOf('[');
          if ( indCorchete!=-1 ) {
            fieldName = fieldName.substring(0, indCorchete);
          }
          
          // Value do not created
          if ( !data.hasOwnProperty(fieldName) ) {
            data[fieldName] = null;
          }
          // If checked, store it
          if ( $ele.is(':checked') ) {
            data[fieldName] = $ele.val();
          }
        // Anything else!
        } else {
          var fieldValue = $ele.val();
          // IL - 04/02/15 - Use hash in case of a pwd field
          // IL - 12/02/15 - Hash fields
          if ( options.hash4PwdFields && $ele.attr('type')=='password' || $ele.data('dohash')) {
            // Do not rehash if we have NOT changed the value
            if ( !$ele.data('originalValue') || $ele.data('originalValue')!=fieldValue ) {
              // TODO : Add the real crypto that need to be aligned with PHP
              // This is just for demo porpuses
              // fieldValue = 'hash#' + fieldValue;
              throw "Hash functionality not implemented!"  
            }
          }

          // IL - 09/09/13 : Files
          if ( $ele.attr('type')=='file' ) {
            if ( options.debug ) console.log('FILE : ' + $ele.val());
            // If 'jsonform-file' exists is because we have uploaded a file
            // (see method uploadOneFile())
            if ( $ele.data('jsonform-file') ) {
              // Do not get confused, $ele.data('jsonform-file').url is the 
              // file Id NOT the URL :-(
              fieldValue = $ele.data('jsonform-file').url;
              $ele.removeData('jsonform-file');
            // If not exists, that can mean we have NOT updated a file, the we
            // have 2 different cases here:
            // + If was not a previous file before
            // + If was a previous file before. In that case, when rendering the 
            //   form using jsonreder we added a data value 'originalValue' containing
            //   the value of that field (in that case, the Id of the file)
            // + We have not upd 'jsonform-file' quiere decir que dejamos el fichero 
            // que había antes. En este caso, el valor se habrá guardado en 
            // $field.data('jsonrender-file', value);
            // @todo : unificar  
            } else {
              // alert('We have NOT updated a new file but this file has an originalValue : "' + $ele.data('originalValue') + '"');
              fieldValue = $ele.data('originalValue') ? $ele.data('originalValue') : null;
            }
          }
          
          // IL - 08/09/13 - If this key already exists, the value must be 
          // stored as an array (fex.checkboxes)
          // IMPORTANT : Is created an array always that the field appears
          // more than once, EVEN if it store only one value
          if ( data.hasOwnProperty(fieldName) ) {
            if ( options.debug ) console.log('1) fieldName : ' + fieldName);
            // If it is not an array, convert it to an array
            if ( !$.isArray(data[fieldName]) ) {
              var currVal = data[fieldName];
              data[fieldName] = new Array();
              if ( currVal!=null ) {
                data[fieldName].push(currVal);
              }
            }
            // Add this value to the array (if it is an checkbox, only if it
            // is checked
            if ( !$ele.is(':checkbox') || $ele.is(':checked') ) {
              data[fieldName].push(fieldValue);
            }
          // This key does not exist, store the value as a regular field
          } else {
            if ( options.debug ) {
              console.log('2.1) fieldName : ' + fieldName + ', fieldValue:' + fieldValue + ', ');
              console.log("2.2) ele.is(':checkbox') : " + $ele.is(':checkbox') + 
                ", $ele.is(':checked') : " + $ele.is(':checked') + ".");
            }
            
            if ( !$ele.is(':checkbox') || $ele.is(':checked') ) {
              if ( options.debug ) {
                console.log('2.3) Store data[' + fieldName + '] = ' + fieldValue + '.'); 
              }
              data[fieldName] = fieldValue;
            } else {
              // IL - 24/10/13 - If it is a checkbox NOT checked, do not store null
              // IL - 27/01/15 - This code was not clear, comment ...
              /*
              if ( !$ele.is(':checkbox') ) {
                if ( options.debug ) {
                  console.log('2.3) Store data[' + fieldName + '] = null.');
                }
                data[fieldName] = null;
              } else {
                if ( options.debug ) {
                  console.log('2.3) Nothing stored, ???');
                }
              }
              */
              // IL - 27/01/15 - Here we are for the checkboxes NOT checked.
              // fieldValue is the value assigned in the checkbox (fex. 1) and
              // it is ALWAYS the same, is checked or not, so:
              // - If checked : store fieldValue (above)
              // - If unchecked : store NULL (we could try to store NOT(fieldValue),
              //   fex. fieldValue=1 => 0, fieldValue=S => N, ...
              if ( options.debug ) {
                console.log('2.3) Store data[' + fieldName + '] = null.');
              }
              data[fieldName] = fieldValue==1 ? 0 : null;
            }
          }
        }
      });

      // Step 2
      // Get MY groups; that means groups that are not inside another group
      var listGroups=[];
      filterDeep($container,listGroups, function($ele){
        return $ele.data('jsonform-group') ? 1 : 0;
      });
      $.each(listGroups,function(ind,$ele){
        var groupName = $ele.data('jsonform-group');
        if ( options.debug ) console.log("==== PROCESSING GROUP : " + groupName + '...');
        
        // This group, will contain an object or an array?
        // Let's see if inside we have some _template/_templateGenerated elements
        var listArrayElements=[];
        filterDeep($ele,listArrayElements, function($eleArray){
          if ( $eleArray.hasClass(options.classTemplate) || $eleArray.hasClass(options.classTemplateGenerated)) {
            return 1;
          } else if ( $eleArray.data('jsonform-group') ) {
            return -1;
          } else {
            return 0;
          }
        });
        // Is an array
        if ( listArrayElements.length!=0 ) {
          if ( options.debug ) console.log('Is an array of ' + (listArrayElements.length-1) + ' elements');
          data[groupName] = [];
          $.each(listArrayElements,function(ind,$eleArray){
            if ( $eleArray.hasClass(options.classTemplateGenerated) ) {
              var dataEleArray = {};
              fillValues($eleArray, dataEleArray);
              // IL - 24/10/13 - Do not store empty elements
              if ( !$.isEmptyObject(dataEleArray) ) {
                data[groupName].push(dataEleArray);
              }
            }
          });
        // Is an object  
        } else {
          if ( options.debug ) console.log('Is an object');
          data[groupName] = {};
          fillValues($ele, data[groupName]);
        }
      });
    }
    
    /**
     * Get/set a plugin option.
     * Get usage: $('#el').demoplugin('option', 'key');
     * Set usage: $('#el').demoplugin('option', 'key', value);
     */
    function option (key, val) {
      if (val) {
        options[key] = val;
      } else {
        return options[key];
      }
    }
    
    /**
     * Destroy plugin.
     * Usage: $('#el').demoplugin('destroy');
     */
    function destroy() {
      // Iterate over each matching element.
      $el.each(function() {
        var el = this;
        var $el = $(this);
 
        // Add code to restore the element to its original state...
 
        hook('onDestroy');
        // Remove Plugin instance from the element.
        $el.removeData('plugin_' + pluginName);
      });
    }
 
    // --------------------------------------------------------- Private Methods
    /**
     * Process an array of $files
     */
    function processFiles(arrayFiles, onDone) {
      if ( arrayFiles.length!=0 ) {
        var $file = arrayFiles.pop();
        if ( options.debug ) console.log('>>>> Vamos a subir ' + $file.get(0) + ' y quedarán ' +  arrayFiles.length + ' por subir');
        var reader = new FileReader();
        var file = $file.get(0).files[0];
        // If the <input elemenet has the attribute data-jsonform-fieldcfg defined
        // that can mean we have to perform some validations the file before upload

        // Validate file size
        if ( $file.data('jsonform-fieldcfg') && $file.data('jsonform-fieldcfg')['max_size'] ) {
          var cfg = $file.data('jsonform-fieldcfg')['max_size'];
          var max_sizeValue = cfg['value'] * 1000;
          var max_sizeErrorMessage = cfg['error'];

          var fileSize = null; 
          try {
            fileSize = file.size; 
          }catch(e) {
            console.log("Browser does not support file.size!!");
            throw "Browser does not support file.size!!";
          }
          if ( fileSize > max_sizeValue ) {
            isFileOk = false;
            // Stop the file processing and return the error
            var fieldName = $file.attr('name');
            var retData = {};
            retData['errors'] = {};
            retData['errors'][fieldName] = max_sizeErrorMessage;

            onDone(retData);
            return;
          }
        }

        // Validate file extension
        if ( $file.data('jsonform-fieldcfg') && $file.data('jsonform-fieldcfg')['extensions'] ) {
          var cfg = $file.data('jsonform-fieldcfg')['extensions'];
          var extensionsValue = cfg['value'].split(",")
          var extensionsErrorMessage = cfg['error'];

          var mimetype = file.type;
          if ( mimetype && extensionsValue.indexOf(mimetype) <0 ) {
            var fieldName = $file.attr('name');
            var retData = {};
            retData['errors'] = {};
            retData['errors'][fieldName] = extensionsErrorMessage;

            onDone(retData);
            return;
          }      
        }

        // The file is ok, we can proceed
        reader.onload = (function(file, $file){
          return function(event){
            var fileContents = event.target.result;
            var fileChecks = options.checkFilePropDataName ? $file.data(options.checkFilePropDataName) : null;
            // Do resize
            // IL - 28/01/15 - Check fileChecks is niot null
            if ( fileChecks!=null && (fileChecks.resizeW || fileChecks.resizeH) ) {
              if ( options.debug ) console.log('Resize ' + fileChecks.resizeW + ', ' + fileChecks.resizeH + ', ' + fileChecks.resizeFormat);
              UtilImg.scaleBase64(fileContents, fileChecks.resizeW, fileChecks.resizeH, fileChecks.resizeFormat, function(newFileContents){
                uploadOneFile(newFileContents, $file, file, function(data) {
                  if ( data ) {
                    onDone(data);
                  } else {
                    processFiles(arrayFiles, onDone); 
                  }
                });
              });
            // Just upload as it is
            } else {
              uploadOneFile(fileContents, $file, file, function(data) {
                if ( data ) {
                  onDone(data);
                } else {
                  processFiles(arrayFiles, onDone); 
                }
              });
            }
          }; // function
        })(file, $file);   
        reader.readAsDataURL(file);
      } else {
        onDone();
      }
    }
    
    function uploadOneFile(fileContents, $file, file, onDone) {
      $.post(
          options.url2UploadFiles, 
          { 
            content : fileContents,
            name    : file.name,
            size    : file.size,
            type    : file.type
          },
          // The file has been uploaded into the server
          function(data) {
            if ( data.errors ) {
              onDone(data);
            } else {
              // Add this info returned from the server.
              // so when we create the JSON object we can use it as data value
              // Currently the upoload service is UploadFileDBSrv and the info
              // returned is (sorry, the name is confusing :-():
              // {
              //   "url" : idFile ===> NOT the url to access  
              // }
              $file.data('jsonform-file', data);
              onDone();            
            }
          }
      );
      
    }
    
    /**
     * Scale an image and returns the data as base64 encoded
     * @param originalImg Objecy Image
     */
    function resizeImage(originalImg, pNewW, pNewH, imgFormat) {
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
      if ( options.debug ) console.log('newW : ' + newW + ', newH : ' + newH);  
      
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
     * Submit the form
     */
    function doSubmit($bSubmit) {
      // Build a string representation with the data JSON encoded. 
      // It will take into account grouping and repeated elemets. 
      // Isn't that great? :-)
      var json={};
      fillValues($el, json);
      if ( options.addDataBeforeSubmit ) {
        options.addDataBeforeSubmit(json, $el);
      }
      
      data = JSON.stringify(json);
      
      // Send this string POST, using ajax
      // At the other side the server endpoint has to be able to read the 
      // POST content and save it as string 
      // Fex, using PHP could be something like:
      // Save the content into a file
      //   file_put_contents(<fileName>, file_get_contents('php://input'));
      // Build the JSON object and process it
      //   $data = json_decode(file_get_contents('php://input'));
      var url = $bSubmit.closest("form").attr('action');
      if ( options.debug ) console.log('Sending ' + data + ' to ' + url);
      if ( url ) {
        $.ajax({
          url: url,
          type: 'POST',
          processData: false,
          data: data,
          /*contentType: 'application/json',
        dataType: 'json',*/
          success: function(data){
            if ( options.cbSave ) {
              options.cbSave(data);
            }
          },
          error: function(jqXHR, textStatus, errorThrown){
            if ( options.onSaveError ) {
              options.onSaveError(jqXHR, textStatus, errorThrown);              
            }
          }
        });
      }
    }
    
    /**
     * Find first level elements
     * Loop over the children of $container that are not template and check 
     * every element against testFunc that can return:
     * + -1 : this element is totally ignored
     * +  1 : add this element into the list
     * +  0 : recursive, go deeper  
     */
    function filterDeep($container, list, testFunc) {
      // IL - 29/10/13 - Skip ALWAYS the _template
      $container.children('*:not(.' + options.classTemplate + ')').each(function(){
        var $this = $(this);
        // IL - 30/10/13
        // Ignore all the elements we have marked to skip
        if ( $this.data('jsonform-process') && $this.data('jsonform-process')=='skip' ) { return true; }
        
        var ret = testFunc($this);
        if ( ret==1 ) {
          list.push($this);
        } else if ( ret!=-1) {
          filterDeep($this, list, testFunc);
        }
      });
      
      return list;
    }
    
    function dump(obj) { 
      for(var key in obj) {
        if ( options.debug ) console.log(">>> [" + key + "] = " + obj[key]);
      }
    }
 
    /**
     * Callback hooks.
     * Usage: In the defaults object specify a callback function:
     * hookName: function() {}
     * Then somewhere in the plugin trigger the callback:
     * hook('hookName');
     */
    function hook(hookName) {
      if (options[hookName] !== undefined) {
        // Call the user defined function.
        // Scope is set to the jQuery element we are operating on.
        options[hookName].call(el);
      }
    }
 
    // Initialize the plugin instance.
    init();
 
    // Expose methods of Plugin we wish to be public.
    return {
      option: option,
      destroy: destroy,
      fillValues: fillValues,
      submitForm : submitForm
    };
  }
 
  /**
   * Plugin definition.
   */
  $.fn[pluginName] = function(options) {
    // If the first parameter is a string, treat this as a call to
    // a public method.
    if (typeof arguments[0] === 'string') {
      var methodName = arguments[0];
      var args = Array.prototype.slice.call(arguments, 1);
      var returnVal;
      this.each(function() {
        // Check that the element has a plugin instance, and that
        // the requested public method exists.
        if ($.data(this, 'plugin_' + pluginName) && typeof $.data(this, 'plugin_' + pluginName)[methodName] === 'function') {
          // Call the method of the Plugin instance, and Pass it
          // the supplied arguments.
          returnVal = $.data(this, 'plugin_' + pluginName)[methodName].apply(this, args);
        } else {
          throw new Error('Method ' +  methodName + ' does not exist on jQuery.' + pluginName);
        }
      });
      if (returnVal !== undefined){
        // If the method returned a value, return the value.
        return returnVal;
      } else {
        // Otherwise, returning 'this' preserves chainability.
        return this;
      }
    // If the first parameter is an object (options), or was omitted,
    // instantiate a new instance of the plugin.
    } else if (typeof options === "object" || !options) {
      return this.each(function() {
        // Only allow the plugin to be instantiated once.
        if (!$.data(this, 'plugin_' + pluginName)) {
          // Pass options to Plugin constructor, and store Plugin
          // instance in the elements jQuery data object.
          $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
        }
      });
    }
  };
 
  // Default plugin options.
  // Options can be overwritten when initializing plugin, by
  // passing an object literal, or after initialization:
  // $('#el').demoplugin('option', 'key', value);
  $.fn[pluginName].defaults = {
    onInit: function() {},
    onDestroy: function() {}
  };
 
})(jQuery);
