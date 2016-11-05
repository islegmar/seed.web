/**
 * Utilities for debugging
 */
UtilDebug = {};

/**
 * We can use fPrintNiceValue for printing the MD5 values with MD5()
 */
UtilDebug.dumpObj = function(obj, fPrintNiceValue) {
  for(var key in obj ) {
    if ( typeof obj[key] == 'object' ) {
      console.log('[' + key + "]");
      UtilDebug.dumpObj(obj[key]);
    } else {
      if ( fPrintNiceValue ) {
        console.log(key + " = " + fPrintNiceValue(obj[key]) );
      } else {
        console.log(key + " = " + obj[key] );
      }
    }
  }
}