# ==============================================================
# 
# ¡¡¡¡¡ ADAPT FIRST THIS FILE !!!!!
# 
# This is a SAMPLE file for setting the environment for working with 
# a project based on webrad.
# This setenv is focused in an environment based on:
# - FE : SOOCSS
# - BE : PHP
# When other combinations will appear, probably other variables 
# will be needed and another type of setenv.sh will be needed.
# 
# ==============================================================

# The name of the project generated
# It is used in several places as in the templates as: 
# - The default database created
# - The name of some folders, files created
export PRJ_NAME=myapp

# The project's home, the same place where this setenv.sh file is located
export PRJ_HOME=/home/developer/project

# Where the core WEBRAD_HOME is located.
# This not required except for some scripts (like genConfig.py)
export WEBRAD_HOME=$PRJ_HOME

# Where the templates can be found, ordered in precedence and comma separated
export PRJ_TEMPLATES_DIR="$PRJ_HOME/templates,$PRJ_HOME/model/custom"

# Where the generated files is saved
# In case of FE and BE, it is useful that Apache links to this folder so it can 
# be viewed directly in the browser. For example, via a symbolic link, if
#
#    [htdocs]/myPrj -> $PRJ_HOME/build
#
# the the app can be accessed using:
#
#    http://localhost/myPrj/fe/index.html

# Front End
export FE_TYPE=SOOCSS
export FE_DST_DIR=/var/www/html/fe

# Back End
export BE_TYPE=PHP
export BE_DST_DIR=/var/www/html/be

# Database : where the generated SQL files are generated
export DB_TYPE=MySQL
# export DB_TYPE=Oracle
export DB_DST_DIR=$PRJ_HOME/build/sql


# PYTHON
# TODO : In some scripts we call python from command line instead as a module, 
# this is the reason why we need to know the name of the python's exe (it is
# different in Unix than in Windows), but in the future we will call it as 
# module and this variable will not be need it
export PYTHON_EXE=/usr/bin/python

# ------------------------------------------------------------------------------
# FE : SOOCSS 
# ------------------------------------------------------------------------------
# Global (page) start/end
export START_HTML_FILE=$PRJ_HOME/templates/Module/FE/SOOCSS/_start.inc
export END_HTML_FILE=$PRJ_HOME/templates/Module/FE/SOOCSS/_end.inc

# Module start/end
export START_WIDGET_HTML_FILE=$PRJ_HOME/templates/Module/FE/SOOCSS/_startWidget.inc
export END_WIDGET_HTML_FILE=$PRJ_HOME/templates/Module/FE/SOOCSS/_endWidget.inc

# ------------------------------------------------------------------------------
# BE : PHP 
# ------------------------------------------------------------------------------
# There are no need for special variables BUT we have to be sure that the following
# folders exists and are writable by the Apache process
#
# - $_SERVER['DOCUMENT_ROOT'] . '/logs' 
#   Where the logs are created
# - $_SERVER['DOCUMENT_ROOT'] . '/data/' . PRJ_NAME . '/files'
#   Where the files uploaded by the app are saved


# ------------------------------------------------------------------------------
# Database : MySQL 
# ------------------------------------------------------------------------------
# When creating the web application the root password is needed to create a database with the
# name PRJ_NAME and add a user with login PRJ_NAME and password PRJ_NAME. Afterwrds, when adding
# a module, the corresponding table will be added to that new database. 
export MYSQL_EXE=mysql
export MYSQLROOT_USR="root"        
export MYSQLROOT_PWD=""
export MYSQL_USR=$PRJ_NAME    
export MYSQL_PWD=$PRJ_NAME
export MYSQL_DB=$PRJ_NAME
export MYSQL_SERVER="localhost"    
export MYSQL_PORT=3306       

# ------------------------------------------------------------------------------
# I18N 
# ------------------------------------------------------------------------------
# Folder where the <lang>.properties files with all the translations are generated
export PRJ_I18N_DIR=$PRJ_HOME/data/i18n       
# Comma separated list of supported langss. Afterwards, more langs can be added
# from the web, but this list is used to generated all the SQL when generating
# the code. 
# BE SURE 'en' IS IN TE LIST!!!! 
export PRJ_LANGS=en,es

cat<<EOF
================ [ $PRJ_NAME ] ================
PRJ_HOME   : $PRJ_HOME
FE_DST_DIR : $FE_DST_DIR
BE_DST_DIR : $BE_DST_DIR
BE_TYPE    : $BE_TYPE
FE_TYPE    : $FE_TYPE
DB_TYPE    : $DB_TYPE
PRJ_LANGS  : $PRJ_LANGS
=======================================================
EOF
