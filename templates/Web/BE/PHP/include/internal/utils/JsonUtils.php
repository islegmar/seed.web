<?php
require_once(INTERNAL_ROOT_DIR . '/utils/WebSession.php');

/**
 * Several utilities
 * 
 * @author islegmar@gmail.com
 *
 */
class JsonUtils  {
  /**
   * Convert a json into xml
   * @TODO : Add header <?xml version="1.0" encoding="UTF-8"?> 
  */
  public function json2Xml($json,$tab='') {
    $xml='';
    foreach ($json as $ind => $row) {
      // Is an array OR and object
      // If $ind is and integer => It is an ARRAY, let's create <row>
      // If $ind is NOT an integer => It is an OBJECT
      if ( is_array($row) || is_object($row) ) {
        $xml .= $tab . (is_integer($ind) ? '<row>' : '<' . $ind . '>') . PHP_EOL;
        $xml .= $this->json2Xml($row, $tab . '  ');
        $xml .= $tab . (is_integer($ind) ? '</row>' : '</' . $ind . '>') . PHP_EOL;
      // It's a single value  
      } else {
        $xml .= $tab . "<" . $ind . ">" . $row . "</" . $ind . ">" . PHP_EOL;
      }
    }

    return $xml;
  }
}
?>