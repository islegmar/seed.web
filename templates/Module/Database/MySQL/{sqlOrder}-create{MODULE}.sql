CREATE TABLE IF NOT EXISTS {MODULE} (
  Id              int unsigned not null auto_increment primary key,
  IdOwner         int unsigned null,
  {SQLFieldDecl}
) CHARACTER SET utf8  COLLATE  utf8_spanish_ci Engine=InnoDB;
{FKDeclarations}
{DBFieldConstraints}

