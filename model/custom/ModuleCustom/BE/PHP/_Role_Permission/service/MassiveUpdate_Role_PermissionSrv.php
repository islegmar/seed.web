<?php
require_once(APP_ROOT_DIR . '/_Role_Permission/service/_MassiveUpdate_Role_PermissionSrv.php');

/**
 * Returns a list of the full grid of Role x Permission to be editable in a
 * massive way
 *
 * @author islegmar@gmail.com
 */

class MassiveUpdate_Role_PermissionSrv extends _MassiveUpdate_Role_PermissionSrv {
  // ----------------------------------------- _MassiveUpdate_Role_PermissionSrv
  protected function performImpl() {
    $sql=<<<EOD
    SELECT _Permission.Id      AS PermissionId,
           _Permission.Name    AS PermissionName,
           _Role.Id            AS RoleId,
           _Role.Name          AS RoleName,
           _Role_Permission.Id AS IdRolePermission
      FROM _Role
      JOIN _Permission
 LEFT JOIN _Role_Permission
        ON _Role_Permission.Id_Permission = _Permission.Id
       AND _Role_Permission.Id_Role = _Role.Id
  ORDER BY _Permission.Name,
           _Role.Name
EOD;

    $list = FactoryObject::newObject('_Role_Permission')->findMultiple($sql);

    // Array with the names of roles and permissions (in order)
    $roles=array();
    $permissions=array();
    // Matrix with 1/0 depending if a certain Role/Permission is active or not.
    // + rows : permissions
    // + columns : roles
    $matrix=array();

    $lastIdPermission=null;
    $storeRoles=True;
    $rowInd=null;
    foreach ($list as $ind => $data) {
      // Change of permission (or the first one)
      if ( is_null($lastIdPermission) || $data['PermissionId']!=$lastIdPermission ) {
        // Store the permission
        array_push($permissions, array(
          'Id'   => $data['PermissionId'],
          'Name' => $data['PermissionName']
        ));
        $lastIdPermission=$data['PermissionId'];
        
        // Create a new row in the matrix
        array_push($matrix, array());
        $rowInd=count($matrix)-1;
      }

      // Store the roles until we have all of them
      if ( $storeRoles ) {
        // Ok, we are back to the first role
        if ( count($roles)>0 && $data['RoleId']==$roles[0]['Id'] ) {
          $storeRoles=False;
        } else {
          array_push($roles, array(
            'Id'   => $data['RoleId'],
            'Name' => $data['RoleName']
          ));
        }
      }

      // Store the Role/Permission
      array_push($matrix[$rowInd], 
        array(
          'RoleId'       => $data['RoleId'],
          'PermissionId' => $data['PermissionId'],
          'value'        => is_null($data['IdRolePermission']) ? 0 : 1
        )
      );
    }

    return array (
      'roles' => $roles,
      'permissions' => $permissions,
      'matrix' => $matrix
    );
  }
}
?>
