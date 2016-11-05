<?php
define('MYSQL_SERVER_NAME', "localhost");
define('MYSQL_DB_USERID',   'c2_' . APP_NAME);
define('MYSQL_DB_PASSWORD', 'c2_' . APP_NAME);
define('MYSQL_DB_NAME',     'c2_' . APP_NAME);
  
// $_SERVER['DOCUMENT_ROOT'] is /var/www/html
$DEF_LOG_BASEDIR=$_SERVER['DOCUMENT_ROOT'] . '/logs/c2';
$DEF_LOG_BASEFILENAME=APP_NAME;

$DEF_DATADIR=$_SERVER['DOCUMENT_ROOT'] . '/data/c2/' . APP_NAME . '/files';
$DEF_BEANSDIR=$_SERVER['DOCUMENT_ROOT'] . '/data/c2/' . APP_NAME . '/beans';
?>
