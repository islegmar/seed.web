<?php
require_once(INTERNAL_ROOT_DIR . '/utils/Params.php');

/**
 * Permite gestionar los parámetros que nos llegan de los requests.
 * 
 * @author Isi
 *
 */
class WebParams extends Params {
	public function __construct() {
		parent::__construct(array_merge($_GET,$_POST));
	}
}
?>
