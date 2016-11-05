# https://hub.docker.com/_/php/
if [ -z "$PRJ_HOME" ]
then
  cat<<EOF
The variable PRJ_HOME has not been set!!
Please execute first "source setenv.sh" in order to set the environment.

EOF
  exit 2
fi

cat<<EOF
===========================================================================
A instance of the project $PRJ_NAME will be instantiated
and accessible as

http://localhost:8080/fe
===========================================================================

EOF
sudo docker run -itd -p 8080:80 \
     $PRJ_NAME
# sudo docker run -it -p 9090:80 \
#       -v "$PRJ_HOME/build":/var/www/html/democm \
#       -v "$PRJ_HOME/dist":/root/dist \
#       democm
