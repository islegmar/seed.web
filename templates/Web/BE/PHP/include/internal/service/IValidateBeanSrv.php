<?php
/**
 * If the service implements this interface, the bean is validated before 
 * we perform any action
 */
interface IValidateBeanSrv {
  /**
   * Receives an object and validare it 
   * @param array $obj If OK, return null, otherwise anything
   */
  public function validate($obj);
} 
