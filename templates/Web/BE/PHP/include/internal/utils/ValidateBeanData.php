<?php
require_once(INTERNAL_ROOT_DIR . '/db/MultipleRowsSelectedException.php');
require_once(INTERNAL_ROOT_DIR . '/db/NoRowSelectedException.php');

/**
 * Utility used to validate bean data, basically coming from Forms
 */
class ValidateBeanData {
  protected $errors=null;
  protected $i18n=null;
  protected $errorCodePrefix='';

  /**
   * Constructor
   * @param string $errorCodePrefix If this value is specified, when translated all
   * the error codes will have this prefix
   */
  public function __construct($errorCodePrefix='') {
    $this->errors = array();
    $this->i18n = FactoryObject::newObject('I18N');
    $this->errorCodePrefix = $errorCodePrefix;
  }

  // --------------------------------------------------------- Useful Validators
  public function validateNonEmpty($fieldName, $fieldValue, $errorMsg=null) {
    if ( empty($fieldValue) ) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'Required', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }
  
  public function validateIsWord($fieldName, $fieldValue, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    if ( preg_match('/[^A-Z0-9_]/i',$fieldValue) ) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsNotWord', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  public function validateIsNifNieCif($fieldName, $fieldValue, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    if ( !FactoryObject::newObject('NifNieCifUtil')->isValidIdNumber($fieldValue) ) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsNotNifNieCif', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  public function validateIsEmail($fieldName, $fieldValue, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    if ( !filter_var($fieldValue, FILTER_VALIDATE_EMAIL) ) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsNotEmail', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  public function validateIsURL($fieldName, $fieldValue, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    $isOk=True;

    if ( !filter_var($fieldValue, FILTER_VALIDATE_URL) ) {
      // If the URL does NOT contain http/https, let's check if it
      // represents a relative URL
      if ( parse_url($fieldValue, PHP_URL_SCHEME) != '' || 
           !filter_var('http://www.example.com/'.ltrim($fieldValue,'/'), FILTER_VALIDATE_URL) ) {
        isOk=False;
      }
    }

    if ( !isOk ) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsNotLink', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  /**
   * Validate value is an Integer
   */
  public function validateIsInteger($fieldName, $fieldValue, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    if ( !filter_var($fieldValue, FILTER_VALIDATE_INT) ) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsNotInteger', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  /**
   * Validate value is an Float
   */
  public function validateIsFloat($fieldName, $fieldValue, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    if ( !filter_var($fieldValue, FILTER_VALIDATE_FLOAT) ) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsNotFloat', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  /**
   * Numeric value : check 
   *   value >=min_val
   */
  public function validateIsNumberNotTooSmall($fieldName, $fieldValue, $min_value, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    if ( floatval($fieldValue)<floatval($min_value)) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsNumberTooSmall', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  /**
   * Numeric value : check 
   *   value <=max_val
   */
  public function validateIsNumberNotTooBig($fieldName, $fieldValue, $max_value, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    if ( floatval($fieldValue)>floatval($max_value)) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsNumberTooBig', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  /**
   * Check that in the DBBean $obj there is no other record where the field
   * 'fieldName' has the value 'fieldValue' (fex. unique emails....)
   */
  public function validateIsUnique($dbObj, $fieldName, $fieldValue, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    $isOk = null;    
    try {
      $found = $dbObj->getByField($fieldName, $fieldValue);
      // If no exception has been thrown, that means there is a record and this
      // is an error EXCEPT is rthe same record
      $isOk = $found['Id']===$dbObj->getId();
    } catch(NoRowSelectedException $e) {
      // This is ok, there are no other records
      $isOk = true;
    } catch(MultipleRowsSelectedException $e) {
      $isOk = false;
    }

    if ( !$isOk ) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsNotUnique', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  /**
   * String length <= max_len 
   */
  public function validateIsStringNotTooLong($fieldName, $fieldValue, $max_len, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    if ( strlen($fieldValue)>intval($max_len)) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsStringTooLong', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  /**
   * String represents a date in a certaibn format 
   */
  public function validateIsDate($fieldName, $fieldValue, $dateFormat, $errorMsg=null) {
    if ( empty($fieldValue) ) return;

    $d = DateTime::createFromFormat($dateFormat, $fieldValue);
    if ( !($d && $d->format($dateFormat) == $fieldValue) ) {
      if ( is_null($errorMsg) ) {
        $this->addErrorCode( $fieldName . 'IsNotDate', $fieldName);
      } else {
        $this->addErrorMsg( $errorMsg, $fieldName);        
      }
    }
  }

  // ------------------------------------------------------------ Public Methods
  public function addErrorCode($code, $fieldName=null, $vars=null, $values=null) {
    // Get the error message. If we have specified a prefix for the error codes, 
    // use it
    $this->addErrorMsg($this->i18n->translate($this->errorCodePrefix . $code, $vars, $values), $fieldName);
  }
  
  public function addErrorMsg($msg, $fieldName=null) {
    // This error related with a certain field
    if ( !is_null($fieldName) ) {
      // We have a previous error
      if ( isset($this->errors[$fieldName]) ) {
        $value = $this->errors[$fieldName];
        
        // It is not an array and we have a new error, convert it into array  
        if ( !is_array($value) ) {
          $this->errors[$fieldName] = array();
          array_push($this->errors[$fieldName], $value);
        }
        // Add the new error message
        array_push($this->errors[$fieldName], $msg);
      } else {
        $this->errors[$fieldName] = $msg;
      }
    // Generic error, no field related
    } else {
      array_push($this->errors, $msg);
    }
  }
  
  public function getErrors() {
    return $this->errors;
  }
}
