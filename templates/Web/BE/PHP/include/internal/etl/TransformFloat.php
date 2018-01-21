<?php
require_once(INTERNAL_ROOT_DIR . '/etl/ITransform.php');

class TransformFloat implements ITransform {
  // ---------------------------------------------------------------- ITransform
  public function config($config) {
  }

  // do nothing, just return the value as it is
  public function transform($value) {
    return floatval($value);
  }
}
?>
