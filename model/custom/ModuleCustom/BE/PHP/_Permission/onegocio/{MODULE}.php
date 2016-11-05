<?php
require_once(dirname(__FILE__) . '/_{MODULE}.php');
require_once (APP_ROOT_DIR . '/_Permission/onegocio/_Permission.php');

/**
 * {MODULE}
 *
 * @author islegmar@gmail.com
 */
class {MODULE} extends _{MODULE} {
  /* Return all the Permissions for a certain Role (for efficiency, just the names, 
    not the entire objects) */
  public function getAllPermissionByIdRole($idRole) {
    //echo('idRole : ' . $idRole);
    $sql=<<<EOD
    SELECT _Permission.Name 
      FROM _Permission,
           _Role_Permission 
     WHERE _Role_Permission.Id_Permission = _Permission.Id
       AND _Role_Permission.Id_Role = :Id_Role 
EOD;

    $array_list = $this->findMultiple($sql, null, false, array(':Id_Role' => $idRole));
    $list=array();
    foreach ($array_list as $ind => $item) {
      array_push($list, $item['Name']);
    }

    return $list;
  }
}
?>