/**
 * @TODO : refractor; this code is referenced in jquery.jsonform.js, but probably
 * never used because there there is a similar code (processFiles), but just in
 * case,...
 */
/**
 * Execute a asynch function over a collection of elements and call a function 
 * when is done
 * The signature of is asynchFunction is
 * asynchFunction ($ele, cbFunction) where:
 * - $ele : the element to apply
 * - cbFunction : callback function that is called when it is done  
 * Example of use:
 *   callAsychFunction(
 *     $('...')
 *     ,function($ele, onDone) {
 *       // Call the server to perform something
 *       $.getJSON(url, params, function() { onDone(); });
 *     }
 *     ,function() {
 *      // Do something when all work is done
 *     }
 *   );
 */
function callAsychFunction($collection, asynchFunction, onDone) {
  console.log('callAsychFunction. # ele : ' + $collection.length);
  if ( $collection.length==0 ) {
    onDone($collection);
  } else {
    var $ele = $collection.first();
    asynchFunction($ele,(function($pCollection,pAsynchFunction, pOnDone){
      // Make a closure to receieve the parameters
      // This function will be called when 'asynchFunction' has done his job
      return function() {
        console.log('Received response form the asynch function');
        callAsychFunction($pCollection, pAsynchFunction, pOnDone);  
      }
    })($collection.slice(1), asynchFunction,onDone));
  }
}