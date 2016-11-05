<?php
require_once(INTERNAL_ROOT_DIR . '/security/PrincipalImpl.php');

/**
 * An anonymous user
 * 
 * @author islegmar
 */
class AnonymousPrincipal extends PrincipalImpl {
	public function __construct() {
		$this->setName('anonymous');
		$this->setAnonymous(true);
		// Try to get the language from the $_SERVER
		$langs = $this->getLanguages();
		if ( sizeof($langs)>0 ) {
			reset($langs);
			$this->setLanguage(	key($langs));
		} else {
			$this->setLanguage(	'en');
		}
	}
	
	/**
	 * Return an array as
   * (
   *   [en-ca] => 1
   *   [en] => 0.8
   *   [en-us] => 0.6
   *   [de-de] => 0.4
   *   [de] => 0.2
   * )
   * 
   * where the factor is the 'quality'
	 */
	private function getLanguages() {
		$langs = array();
		
		if (isset($_SERVER['HTTP_ACCEPT_LANGUAGE'])) {
			// break up string into pieces (languages and q factors)
			preg_match_all('/([a-z]{1,8}(-[a-z]{1,8})?)\s*(;\s*q\s*=\s*(1|0\.[0-9]+))?/i', $_SERVER['HTTP_ACCEPT_LANGUAGE'], $lang_parse);
		
			if (count($lang_parse[1])) {
				// create a list like "en" => 0.8
				$langs = array_combine($lang_parse[1], $lang_parse[4]);
				 
				// set default to 1 for any without q factor
				foreach ($langs as $lang => $val) {
					if ($val === '') $langs[$lang] = 1;
				}
		
				// sort list based on value
				arsort($langs, SORT_NUMERIC);
			}
		}
		
		return $langs;
	}
}