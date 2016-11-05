<?php
require_once(INTERNAL_ROOT_DIR . '/etl/ITransform.php');

class TransformConcat implements ITransform {
	// ---------------------------------------------------------------- ITransform
	public function config($config) {
	}

  // do nothing, just return the value as it is
	public function transform($list) {
		$newValue = "";

		foreach ($list as $value) {
			$newValue .= $value;
		}

    return $newValue;
  }
}
?>
