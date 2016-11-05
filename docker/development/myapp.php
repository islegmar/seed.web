<?php
/**
 * This is SAMPLE of configuration.
 * This file should be located at 
 *
 * $_SERVER['DOCUMENT_ROOT'] . '/config/' . APP_NAME . '.php'
 *
 * For example:
 *
 * /var/www/html/config/webrad.php
 */  
define('MYSQL_SERVER_NAME', "127.0.0.1");
define('MYSQL_DB_USERID',   "myapp");
define('MYSQL_DB_PASSWORD', "myapp");
define('MYSQL_DB_NAME',     "myapp");
  

// This should be needed ONLY if _File is configures to store the files in
// the filesystem but by default the files are kept in the database (to change
// the behaviour, the source code of _File must be changed).
// The variable MUST be defined (or it will be an error in /Web/BE/PHP/php/config.php)
// even if it is not used
$DEF_DATADIR=$_SERVER['DOCUMENT_ROOT'] . '/data/' . APP_NAME . '/files';

// ------------------------------------------------------ Logger's Configuration
$DEF_LOG_BASEDIR=$_SERVER['DOCUMENT_ROOT'] . '/logs';
$DEF_LOG_BASEFILENAME=APP_NAME;

$DEF_LOG_PATTERN = '%d %p %c [%F#%M] - %m%n';
$DEF_LOG_AUTH_PATTERN = '%d|%m%n';
$LOG_CFG = array(
    'rootLogger' => array(
        'level' => 'DEBUG'
    ),
    'appenders' => array(
        'main' => array(
            'class' => 'LoggerAppenderRollingFile',
            'layout' => array(
                'class' => 'LoggerLayoutPattern',
                'params' => array(
                    'conversionPattern' => $DEF_LOG_PATTERN
                )
            ),
            'params' => array(
                'file' => $DEF_LOG_BASEDIR . '/' . $DEF_LOG_BASEFILENAME . '.log',
                'maxFileSize' => '1MB',
                'maxBackupIndex' => 5,
            )
        ),
        'auth' => array(
            'class' => 'LoggerAppenderRollingFile',
            'layout' => array(
                'class' => 'LoggerLayoutPattern',
                'params' => array(
                    'conversionPattern' => $DEF_LOG_AUTH_PATTERN
                )
            ),
            'params' => array(
                'file' => $DEF_LOG_BASEDIR . '/' . $DEF_LOG_BASEFILENAME . '-auth.log',
                'maxFileSize' => '1MB',
                'maxBackupIndex' => 5,
            )
        )
    ),
    'loggers' => array (
        'main' => array (
            'level' => 'DEBUG',
            'appenders' => array(
                'main'
            )
        ),
        'auth' => array (
            'level' => 'DEBUG',
            'appenders' => array(
                'auth'
            )
        ),
        'sql' => array (
            'level' => 'DEBUG',
            'appenders' => array(
                'main'
            )
        ),
        'error' => array (
            'level' => 'DEBUG',
            'appenders' => array(
                'main'
            )
        )
    )
);
?>
