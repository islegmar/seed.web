<?php
define('MYSQL_SERVER_NAME', "localhost");
define('MYSQL_DB_USERID',   'c1_' . APP_NAME);
define('MYSQL_DB_PASSWORD', 'c1_' . APP_NAME);
define('MYSQL_DB_NAME',     'c1_' . APP_NAME);
  
// $_SERVER['DOCUMENT_ROOT'] is /var/www/html
$DEF_LOG_BASEDIR=$_SERVER['DOCUMENT_ROOT'] . '/logs/c1';
$DEF_LOG_BASEFILENAME=APP_NAME;

$DEF_DATADIR=$_SERVER['DOCUMENT_ROOT'] . '/data/c1/' . APP_NAME . '/files';
$DEF_BEANSDIR=$_SERVER['DOCUMENT_ROOT'] . '/data/c1/' . APP_NAME . '/beans';
?>
