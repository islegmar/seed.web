DELETE FROM _Role_Permission;

-- @TODO : adjust the permissions

-- root
INSERT INTO _Role_Permission (Id_Role, Id_Permission) 
  SELECT _Role.Id,
         _Permission.Id
    FROM _Role, 
         _Permission
   WHERE _Role.Name='root';      

-- admin
INSERT INTO _Role_Permission (Id_Role, Id_Permission) 
  SELECT _Role.Id,
         _Permission.Id
    FROM _Role, 
         _Permission
   WHERE _Role.Name='admin';

-- registered
INSERT INTO _Role_Permission (Id_Role, Id_Permission) 
  SELECT _Role.Id,
         _Permission.Id
    FROM _Role, 
         _Permission
   WHERE _Role.Name='registered'
     AND ( _Permission.Name = '_User:ViewMySelf'
        OR _Permission.Name = '_User:ModMySelf'
        OR _Permission.Name = '_User:ChangeMyPassword');

/*
EXAMPLE : in case we want that admin can access all the info
in VIEW ONLY mode

INSERT INTO _Role_Permission (Id_Role, Id_Permission) 
  SELECT _Role.Id,
         _Permission.Id
    FROM _Role, 
         _Permission
   WHERE _Role.Name='admin'
     AND NOT (
     -- Denied access to All the core objects  
        _Permission.Name LIKE '\_%'
     -- Denied all the actions that can modify data 
     OR _Permission.Name LIKE '%:Add%'
     OR _Permission.Name LIKE '%:Del%'
     OR _Permission.Name LIKE '%:Import%'
     OR _Permission.Name LIKE '%:Mod%' );  
*/