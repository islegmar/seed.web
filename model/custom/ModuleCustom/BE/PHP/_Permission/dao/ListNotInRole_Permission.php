<?php
require_once(dirname(__FILE__) . '/_ListNotInRole_Permission.php');

/**
 * Returns the list of Permissions that are still not associated to a 
 * Role that we get as parameter
 * 
 * @author islegmar
 */
class ListNotInRole_Permission extends _ListNotInRole_Permission {
  // ------------------------------------------------- _ListNotInRole_Permission
  protected function getBaseQuery($db, $params=null) { 
    ## @TODO : If in the JSON in the "params" the name is changed and it is 
    ## no named IdRole, we have a problem ...
    ## Also, we can not use data from JSON, like {ListFieldNames} 
    return <<<EOD
      SELECT Id, Name
        FROM _Permission                               
       WHERE Id NOT IN (
        SELECT Id_Permission
          FROM _Role_Permission
         WHERE Id_Role = :IdRole
      )
EOD;
  }
}                                                    
?>