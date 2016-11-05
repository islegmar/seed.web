<?php
/**
 * Base implementation for ALL business beans.
 * Before we use this bean, it's suppose "somebody" has read the configuration. 
 * Also, we can add here all the common stuff 
 * for our applicatioin that can not be shared with the others (otherwise it 
 * should go to DBBean)
 *
 * Use it with care! :-)
 *
 * @Version : 1.0
 *
 * CHANGES
 */
require_once(INTERNAL_ROOT_DIR . '/db/DBBean.php');

class BaseOBean extends DBBean {
  protected $IdOwner = null;

  public function setIdOwner($IdOwner) {
    $this->IdOwner = $IdOwner;
  }

  public function getIdOwner() {
    return $this->IdOwner;
  }

  function getAsArray($pData=null) {            
    $data = parent::getAsArray($pData);         
    $data['IdOwner'] = $this->getIdOwner();
                                                
    return $data;                               
  }                                             


  public function findAll($db=null) {
    return $this->findMultiple('SELECT * FROM ' . $this->TABLE_NAME, $db);
  }
  
  public function load($id, $db=null) {
    //return $this->findOne('SELECT * FROM ' . $this->TABLE_NAME . ' WHERE Id = ' . $id, true, $db);
    return $this->findOneWithStmt('SELECT * FROM ' . $this->TABLE_NAME . ' WHERE Id = :Id', array(':Id' => $id), true, $db);
  }
  
  public function findById($id, $db=null) {
    return $this->findOne('SELECT * FROM ' . $this->TABLE_NAME . ' WHERE Id = ' . $id, false, $db);
  }

  public function deleteById($id, $db=null) {
    return $this->updateOrInsert('DELETE FROM ' . $this->TABLE_NAME . ' WHERE Id=' . $id, $db, true);
  }
}
?>
