#!/bin/bash

if [ $# -lt 3 ]
then
  echo "Use : `basename $0` prjName appDir prjDir fModule1 ...."
  exit 1
fi

SCRIPTS_DIR=/home/ilegido/personal/projects/_common/scripts/tmplGenerator

prjName=$1
# Base folder where the modules definitions, sql test data and
# maybe other config files are found
appDir=$2
# Folder where the generated files are written
prjDir=$3
shift
shift
shift
# Files with the configurations
fModules=$*

for fModule in $fModules
do
  moduleName=`basename $fModule|sed -e 's/.json//'`

  opt=""
  opt="$opt -skipCreateDBTable"
  #opt="$opt -regenerateI18N"
  opt="$opt -recreatePermissionTable"
  sqlTestData=$appDir/model/testSqlFiles/$moduleName.sql
  [ -f $sqlTestData ] && opt="$opt -s $sqlTestData"

  python createWebModule.py \
    --fe HTML \
    --feDst $prjDir/fe/$moduleName \
    --be PHP \
    --beDst $prjDir/be/$moduleName \
    -t "$SCRIPTS_DIR/templates,$appDir/model/custom" \
    -updateTblModule \
    -c $fModule \
    $opt \
    $prjName \
    $moduleName
done
