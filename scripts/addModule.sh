#!/bin/bash
# -------------------------------------------------------
# Utility to create a web propject with FE and BE in PHP
# -------------------------------------------------------

if [ $# -lt 1 ]
then
  echo "Use : `basename $0` AppName moduleName1 moduleName2....."
  exit 1
fi

SCRIPTS_DIR=/home/ilegido/personal/projects/_common/scripts/tmplGenerator
prjName=$1
shift
moduleNames=$*

for fModule in $moduleNames
do
  moduleName=`basename $fModule|sed -e 's/.json//'`

  opt=""
  sqlTestData=$SCRIPTS_DIR/model/testSqlFiles/$moduleName.sql
  [ -f $sqlTestData ] && opt="$opt -s $sqlTestData"

  python createWebModule.py \
    --fe HTML \
    --feDst ~/personal/projects/$prjName/www/fe/$moduleName \
    --be PHP \
    --beDst ~/personal/projects/$prjName/www/be/$moduleName \
    -t "$SCRIPTS_DIR/templates" \
    -updateTblModule \
    $opt \
    $prjName \
    $moduleName
done
