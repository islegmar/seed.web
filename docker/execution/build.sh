#!/bin/bash

if [ -z "$PRJ_HOME" ]
then
  cat<<EOF
The variable PRJ_HOME has not been set!!
Please execute first "source setenv.sh" in order to set the environment.

EOF
  exit 2
fi

echo "Creating the image $PRJ_NAME using the latest version of the code..."
cd $PRJ_HOME/scripts
python makeDist.py
cd $PRJ_HOME/docker
cp $PRJ_HOME/$PRJ_NAME.tar .
sudo docker build \
  -t $PRJ_NAME \
  --build-arg PRJ_NAME=$PRJ_NAME \
  .

echo "Image $PRJ_NAME created!"
sudo docker images|grep $PRJ_NAME
