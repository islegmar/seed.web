<?php
/**
 * Mix of file utilities
 * 
 * @author islegmar
 */
class FileUtils {
	/**
	 * Returns info about a content that is base64 encoded
	 */
	public static function decodeBase64($base64Content)	{
		// Get the mimetype
		$pos=strpos($base64Content,';base64');
		$mimetype = substr($base64Content,5,$pos-5);
		
		// Now decode the base64
		$base64Content = substr($base64Content, $pos+8);
		$base64Content = str_replace(' ', '+', $base64Content);
		$content = base64_decode($base64Content);

		return array(
			'mimetype' => $mimetype,
			'content'  => $content	
		);
	}
  
  // IL - 28/11/13 - Delete recursive 
  public static function rrmdir($dir) { 
    if (is_dir($dir)) { 
      $objects = scandir($dir); 
      foreach ($objects as $object) { 
        if ($object != "." && $object != "..") { 
          if (filetype($dir."/".$object) == "dir") {
            FileUtils::rrmdir($dir."/".$object); 
          } else {
            unlink($dir."/".$object); 
          }
        } 
      } 
      
      reset($objects); 
      rmdir($dir); 
    }  
  }
}