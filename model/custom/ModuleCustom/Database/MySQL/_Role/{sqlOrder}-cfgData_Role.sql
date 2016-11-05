DELETE FROM _Role;
INSERT INTO _Role (Name, OnLoginUrl) VALUES ('root' , '/_User/HomePageRoot_User.html');
INSERT INTO _Role (Name, OnLoginUrl) VALUES ('admin', '/_User/HomePageAdmin_User.html');
# The user who has been registered
INSERT INTO _Role (Name, OnLoginUrl) VALUES ('registered', '/_User/ViewMySelf_User.html');
