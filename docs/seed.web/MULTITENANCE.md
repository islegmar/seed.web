Multitenance
============

The application (and all based on seed.web) supports multitenance, that is:

* Every instance has its own database and "portion" file system
* All the instances share the same code

Access to the instace
---------------------

Now we can access to a certain customer's instace as:

    http://c[1...].demo.com/<appName>/fe/index.html

For example

    http://c1.demo.com/seed.web/fe/index.html

will show the login page for the app *seed.web* for *customer1*.

BE's implementation
---------------------

The way this is done, currently depend on the BE's implementation.


### BE : PHP

The host name is used to know which is the instance and which configuration use

    template/Web/BE/PHP/php/config.php

    // Server specific
    if ( file_exists(APP_ROOT_DIR . '/php/config/' . $_SERVER['HTTP_HOST'] . '.php') ) {
      include_once(APP_ROOT_DIR . '/php/config/' . $_SERVER['HTTP_HOST'] . '.php');
    // Default 
    } else {
      include_once(APP_ROOT_DIR . '/php/config/default.php');
    }

So, if we access to the URL

    http://c1.demo.com/seed.web/.....

and this file exists

    php/config/c1.demo.com.php       

this configuration will be used, and there we can find the specific connection to the database and the directories used to keep logs and files

    // Database Connection
    define('MYSQL_SERVER_NAME', "192.168.116.62");
    define('MYSQL_DB_USERID',   'c1_' . APP_NAME);
    define('MYSQL_DB_PASSWORD', 'c1_' . APP_NAME);
    define('MYSQL_DB_NAME',     'c1_' . APP_NAME);
  
    // Logs directory
    $DEF_LOG_BASEDIR=$_SERVER['DOCUMENT_ROOT'] . '/logs/c1';
    $DEF_LOG_BASEFILENAME=APP_NAME;

    // Data directory
    $DEF_DATADIR=$_SERVER['DOCUMENT_ROOT'] . '/data/c1/' . APP_NAME . '/files';

In case we do not have ans specdific configuration (fex. in development environments) this config file will not exist and the default one, located at

    php/config/default.php

will be used. 

In terms od project structure, the specific configuration files are stored under:

    model/custom/WebCustom/BE/PHP/php/config/c1.demo.com.php       

HOWTO : configure in the local environment
------------------------------------------

1) Modify /etc/hosts

    127.0.1.1       c1.demo.com 
    127.0.1.1       c2.demo.com

2) Check Apache.
Yo neec to ensure Apache is configured to resolve those hosts. So, if you type

    http://c1.demo.com/seed.web/fe/index.html

the login page should be displayed. You are still using the default configuration (that is the seed.web database) because you have not created an specific configuration 

*NOTE* : If you need to create a Virtual Host:    

    /opt/lampp/etc/extra/httpd-vhosts.conf

    <VirtualHost c1.demo.com>                            
      <Directory "/home/user/myWebs">               
        AllowOverride All                                       
        Require all granted                                     
      </Directory>                                              
    </VirtualHost>                                              
                                                              
    <VirtualHost c2.demo.com>                            
      <Directory "/home/user/myWebs">               
        AllowOverride All                                       
        Require all granted                                     
      </Directory>                                              
    </VirtualHost>            

3) Create an specific configuration
Create the files 

    model/custom/WebCustom/BE/PHP/php/config/c1.demo.com.php
    model/custom/WebCustom/BE/PHP/php/config/c2.demo.com.php

and put the following lines (the same in both files, changing c1 for c2)

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

and regenerate the code again

    python createWebProject.py                                                                 

4) Check this config is used
If you try to login in 

    http://c1.demo.com/seed.web/fe/index.html

and check the web console you should get something like

    Error 500
    SQLSTATE[HY000] [1049] Unknown database 'c1_seed.web'

5) Create the folders
Be sure the folders for logs 

    $_SERVER['DOCUMENT_ROOT'] . '/logs/c1'
    $_SERVER['DOCUMENT_ROOT'] . '/logs/c2'

exists. The other for the data are created by the code if not exists

6) Create the databases
Now every instance has his own database (c1_seed.web and c2_seed.web) so we must create it and populate it. The easiest way is to create a distyro
  
    cd scripts
    python makeDist.py
    cd ../dist
    python createDB.py --createDB c1
    python createDB.py --createDB c2

7) Check everything works!
Now you should able to login using the two URLs:

    http://c1.demo.com/seed.web/fe/index.html
    http://c2.demo.com/seed.web/fe/index.html