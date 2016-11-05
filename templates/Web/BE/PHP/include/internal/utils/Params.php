<?php
/**
 * Permite gestionar parámetros con funciones de sanitize y demás.
 * 
 * @author Isi
 *
 */
class Params {
	protected $data=null;
	
	public function __construct($data) {
		// TODO : Aquí tenemos que hacer sanitize y todas esas cosas
		$this->data = $data;
	}

	/**
	 * Returns the value of a param or exception if not exists
	 * @param unknown_type $id
	 * @param unknown_type $default
	 */
	public function getOblParam($id) {
		if ( !$this->existeParam($id) ) throw new Exception('Not exist param "' . 
				$id . '"'); 
		
		return $this->getParam($id);
	}
	
	public function getParam($id, $default=null) {
		$value =  $this->existeParam($id) ? $this->data[$id] : $default;
    // IL - 05/10/12 : Si está en blanco, es como un null
    // IL - 17/02/14 : value can be an object
		if ( $value=="null" || (is_string($value) && strlen($value)==0) ) {
      // IL - 05/10/12 : Si no está definido, devolver el valor por defecto
  		// $value=null;
      $value = $default;
		}
		return $value;
	}
	
  public function existeParam($id) {
  	return isset($this->data[$id]) && !is_null($this->data[$id]);
  }
  
  public function getAllParams() {
  	return $this->data;
  }
  
  public function setParam($key, $value) {
  	$this->data[$key] = $value;
  }
  

  // TODO : mirar con detalle
  /*
  protected function sanitize($item)
  {
  	//return addslashes($item);
    return $item;
  }
  */
}
?>