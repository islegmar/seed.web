#!/bin/bash                                                                        
# It receives as argument the project name

export MYSQL_EXE=mysql

service mysql start


if [ $# -lt 1 ]
then
  echo "Use : deploy.sh prjName"
  exit 2
fi

PRJ_NAME=$1
dstDir=/var/www/html

doUntar=1
doCreateDB=1
doCreateAppConfig=1
doCopyFiles=1
doCopyConfigFiles=0

cat<<EOF
===========================================================
Deploying application $PRJ_NAME ...
===========================================================

EOF

# ---------------------------------------------------------
# Step 1 : untar
# ---------------------------------------------------------
if [ $doUntar -eq 1 ]
then
  ./expand.sh $PRJ_NAME
fi

# ---------------------------------------------------------
# Step 2 : created DB
# ---------------------------------------------------------
if [ $doCreateDB -eq 1 ]
then
  cat<<EOF
2) Create the DB ...
EOF
  cd apps/$PRJ_NAME
  python createDB.py  \
    --createDB \
    --skipTestData    \
    --rootUsr root \
    --rootPwd "" \
    --usr  $PRJ_NAME \
    --pwd  $PRJ_NAME \
    --db   $PRJ_NAME \
    --host 127.0.0.1
  cd ../..
fi

# ---------------------------------------------------------
# Step 3 : created app config
# ---------------------------------------------------------
if [ $doCreateAppConfig -eq 1 ]
then
  cat<<EOF
2) Create the app config ...
EOF

  cd apps/$PRJ_NAME
  sed \
   -e "/MYSQL_SERVER_NAME/s/localhost/127.0.0.1/" \
   -e "/MYSQL_DB_USERID/s/webrad/$PRJ_NAME/" \
   -e "/MYSQL_DB_PASSWORD/s/webrad/$PRJ_NAME/" \
   -e "/MYSQL_DB_NAME/s/webrad/$PRJ_NAME/" \
    be/php/config/default.php.SAMPLE \
    > $dstDir/config/$PRJ_NAME.php
  cd ../..
fi

# ---------------------------------------------------------
# Step 3 : copy files
# ---------------------------------------------------------
if [ $doCopyFiles -eq 1 ]
then
  cat<<EOF
3) Copy files into $dstDir ...
EOF

  cd apps/$PRJ_NAME
  python installApp.py $dstDir
  cd ../..
fi

# ---------------------------------------------------------
# Step 4 : copy config files
# ---------------------------------------------------------
if [ $doCopyConfigFiles -eq 1 ]
then
  cat<<EOF
4) Copy config files into $dstDir/data ...
EOF

  [ -d $dstDir/data ] && rm -fR $dstDir/data
  cp -r apps/$PRJ_NAME/data $dstDir
  ls -1 $dstDir/data/*.csv | sed -e 's/.*\///' | sort | sed -e 's/.*/<a href="&">&<\/a><br\/>/' > $dstDir/data/index.html
fi

service mysql stop
