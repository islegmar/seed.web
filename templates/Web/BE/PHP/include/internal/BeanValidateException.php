<?php
require_once(INTERNAL_ROOT_DIR . '/BaseException.php');

/**
 * Thrown when a form has been validated and it contains errors
 * @author islegmar
 *
 */
class BeanValidateException extends BaseException {
  protected $errors;
  
  public function __construct($errors) {
    $this->errors = $errors;
  }
  
  public function getErrors() {
    return $this->errors;
  }  
  
	/*
    // Redefinir la excepción, por lo que el mensaje no es opcional
    public function __construct($message, $code = 0, Exception $previous = null) {
        // algo de código
    
        // asegúrese de que todo está asignado apropiadamente
        parent::__construct($message, $code, $previous);
    }

    // representación de cadena personalizada del objeto
    public function __toString() {
        return __CLASS__ . ": [{$this->code}]: {$this->message}\n";
    }
*/
}
?>
