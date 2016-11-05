DELETE FROM _User;

-- IMPORTANT
-- The passwords are generated using pbkdf2 (see http://php.net/manual/es/function.hash-pbkdf2.php)
-- with the configuration: 
--   Algorithm  : sha256 
--   Password  
--   Salt       : Login 
--   Iterations : 
--   Length     : 60
--   Raw_output : false 

-- =============================================================================
-- root/root with role 'root'
-- =============================================================================

INSERT INTO _User (
  Login, 
  Password, 
  Id_Role, 
  Email, 
  Id_UserStatus
) 
SELECT 'root', 
       '1234627024a0fe92c41ebcb804416d7922872144c610605208b9d8991e67',
       _Role.Id,
       'root@mail.com',
       _UserStatus.Id
  FROM _Role,
       _UserStatus
 WHERE _Role.Name = 'root'
   AND _UserStatus.Name = 'ACTIVE';
UPDATE _User SET IdOwner=Id WHERE Login='root';

-- =============================================================================
-- admin/admin with role 'admin'
-- =============================================================================

INSERT INTO _User (
  Login, 
  Password, 
  Id_Role, 
  Email, 
  Id_UserStatus
) 
SELECT 'admin', 
       'b2973b72e1bb18e8aa11c5034082a042abb619f7bdd3bdabac31c27c3ff9',
       _Role.Id,
       'admin@mail.com',
       _UserStatus.Id
  FROM _Role,
       _UserStatus
 WHERE _Role.Name = 'admin'
   AND _UserStatus.Name = 'ACTIVE';
UPDATE _User SET IdOwner=Id WHERE Login='admin';
