Tis folder contains two dockers:
+ development : in order to set a development environment
+ execution : in order to execute a built application (*.tar) from
              Jenkins

See the README.txt into the folder for more details.

TIPS
====

If you want to start with a clean docker and remove ALL images
and containers execute:

# Delete all Containers
sudo docker rm $(sudo docker ps -a -q)

# Delete all images
sudo docker rmi $(sudo docker images -q)
