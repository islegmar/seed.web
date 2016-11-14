How to install
==============

The installation depends on the provider used (SOOCSS, PHP,....) and there is a TODO step by step in all the possible combinations. Some documentation can be found in [First Steps](FIRST_STEPS.md)

BE=PHP / FE=SOOCSS / DB=MySQL
=============================

Basically you need a LAMP environment. You can set up it for yourself or use docker.


With Docker
-----------
 
Follow the instruccions can be found [here](../../docker/development/README.md)

Without Docker
--------------

TODO : pending to be reviewed

sudo apt-get install lamp-server^ phpmyadmin php5-gd
sudo /etc/init.d/apache2 start
sudo /etc/init.d/mysql start

**Enable mod_rewrite**

* Enable module : sudo a2enmod rewrite
* Update /etc/apache2/sites-available/000-default.conf with

    <Directory /var/www/html>
        Options FollowSymLinks
        AllowOverride all
    </Directory>
* Restart : sudo service apache2 restart
* Create the folder

    sudo mkdir -p /var/www/html/logs/
    sudo chmod 777 /var/www/html/logs/

In order to use symlinks in /var/www/html:


### Prepare the custom setenv.sh

At this point (@TODO) we do NOT create a 100% dist that can be installed in any environment, but we create a dist to be installed in a SPECIFIC environemnt. That means, that the first step we have to do is to create a specific setenv.sh (let's call it setenv-custom.sh) with the right environment variables defined taking into account the installation environment.

### Create a dist

Using the providers defined in the environment variables export FE_TYPE, BE_TYPE and DB_TYPE, there is a script to prepare a deliberable. 

    source setenv-custom.sh (1)
    cd scripts
    python makeDist.py (1)

(1) CAREFUL : after that, if you want continue developing in that session you should execute before 'source setenv.sh' in order to recover you developer's environment.  
(2) Execute with -h to see more options.    

This will create the tar file `$PRJ_HOME/$PRJ_NAME.tar` and inside it we can find all needed to create the database and install the application. Let's see step by step:

#### Database creation

The following files can be found:

* dropTables.sql : file with all the 'DROP TABLE'
* createTables.sql : file with all the 'CREATE TABLE' and 'ALTER TABLE' (FK)
* insertTestData.sql : file with all the 'testData' sql files.
* permissions.sql : file to populate the table `_Permission`.
* insertCfgData.sql : file with all the 'cfgData' sql files. This will also assign all the permission to the user 'admin'
* i18n.sql : file to populate the tables '_Lang' and '_I18N'

In order to create from scratch the database we have two options:

##### Using python script

Execute 

    python createDB.py 

This will run the SQL scripts in order (see next point) using some values for the database name, database location,... that can be specified in command line (see `python createDB.py -h` for more info) or using the following environment variables:

* MYSQL_SERVER
* MYSQL_PORT (default 3306)
* MYSQL_EXE : path to the mysql 
* From the file env.json, the variablde prjName it is used for the MYSQL_USR, MYSQL_PWD and MYSQL_NAME 

##### Run the SQL scripts (manually)

If the database already exists, execute the following SQLs in order:

1. dropTables.sql
2. createTables.sql
3. permissions.sql
4. insertCfgData.sql
5. i18n.sql
6. (Optional) insertTestData.sql
7. (Optional) allModules.sql
