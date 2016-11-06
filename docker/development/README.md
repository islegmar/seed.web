Overview
========

This is the docker for DEVELOPMENT. 

Pre-requisites
==============

In this scenario in your LOCAL machine you MUST have:
- A clone of this project
- Git
- Browser
- IDE (vi, I hope ;-))

while the DOCKER ptovides a full LAMP environment

Install
=======

Step 1 : build the image
------------------------

    sudo docker build -t <image-name> --build-arg UID=$UID --build-arg GID=$GID .

Example:

    sudo docker build -t seed.web-dev --build-arg UID=$UID --build-arg GID=$GID .

Step 2: Start a container
-------------------------

    sudo docker run -it -p 9090:80  -u $UID -v <local folder>:/home/developer/project <image-name>º

Example, if I have done a clone of the project into /home/ilegido/projects/webrad then the command will be

    sudo docker run -it -p 9090:80  -u $UID -v ~/projects/seed.web:/home/developer/project seed.web-dev

you'll see tracces like

    [ ok ] Stopping MySQL database server: mysqld.                         
    [ ok ] Starting MySQL database server: mysqld ..                       
    [info] Checking for tables which need an upgrade, are corrupt or were  not closed     cleanly..                                                   
    [....] Restarting web server: apache2AH00558: apache2: Could not reliab ly     determine the server's fully qualified domain name, using 172.17.0.2
    . Set the 'ServerName' directive globally to suppress this message     
    . ok                                                                   
    ================ [ myapp ] ================                            
    PRJ_HOME   : /root/app                                                 
    FE_DST_DIR : /var/www/html/fe                                          
    BE_DST_DIR : /var/www/html/be                                          
    BE_TYPE    : PHP                                                       
    FE_TYPE    : SOOCSS                                                    
    DB_TYPE    : MySQL                                                     
    PRJ_LANGS  : en,es                                                     
    =======================================================                

A bash is opened : NEVER CLOSE IT.

Step 3: Build the app
--------------------

In the container's bash you're already in the folder /app/scripts; from there execute:

    python createWebProject.py --createDB

    python createWebModule.py --all --createModuleTable --recreateI18N --recreatePermissions

Step 4: Test the app
--------------------

Open a browser in your local machinbe and go to:

http://localhost:9090/fe

You'll see the loging pages with the texts translated. Login as admin/admin

How does it work?
=================

- In your local machine start the container; that will open a bash that must remain
opened. This containers will start the Apache and the MySQL 
- In your local machine change the files, usign your IDE
- Once the changes are done, go to the bash and compile the code using the python tools.
- Once the compilation is done, go back to your local machine and access to the application with the browser.

So, in the bash you perform the following operations:
- Compile the code using the python tools
- Access to the mysql using the command line application and the command 
  
      mysql --user=myapp --password=myapp myapp

  You can see the tables are there executing

      show tables;

  TIP : there is an alias to do that, just type '_mysql' and you're in!

FAQ
===

+ In some of the previous commands appear 'myapp' but my application is 'XXX', do I have to replace myapp by XXX?

No (and this is reason why it is written myapp and not <myapp>). 
It does not matter how you call your application, in the container will be ALWAYS called myapp. You can see that going to the container and searching in the file

    /var/www/html/be/php/config.php

for the value APP_NAME; you'll find the value

    define ('APP_NAME', 'myapp');

Also you can see the file with the configuration

    /var/www/html/config/myapp.php

there you'll find

    define('MYSQL_SERVER_NAME', "127.0.0.1");
    define('MYSQL_DB_USERID',   "myapp");    
    define('MYSQL_DB_PASSWORD', "myapp");    
    define('MYSQL_DB_NAME',     "myapp");    

+ Can I have more than one webrad's based projects in my local machine? Will it not be a problem if all of them are called myapp?

No. Each container is separated and LOCALLY they are referred as myapp, no conflict. In order to have more that one you must:
  + When BUILDING the images give them different names. So, if I have two projects called 'democm' and 'demoems' I will execute in the corresponding folders

        sudo docker build -t democm-dev .
        sudo docker build -t demoems-dev .

  + When STARTING the containeres, chose different ports to avoind conflicst in the local machine (here ports 9090 and 8080 are chosen)

        sudo docker run -it -p 9090:80  -v /home/ilegido/projects/democm:/root/app democm-dev
        sudo docker run -it -p 80(9)0:80  -v /home/ilegido/projects/demoems:/root/app demoems-dev

+ Why the image is called 'XXX-dev'? Is there anything special with this prefix?

No. It is just a naming convetion. This is because for a certain app we have docker for two scenarios : development and execution and using this prefix is a way to distinguish them.

+ There is an error in the application, where can I see the logs?

In the container you can see the logs in the folder

    /var/www/html/logs

and in case the error is a syntax error, please checks the apache errors located in:

    /var/log/apache2/error.log 

+ I get an error when I go to http://localhost:9090/fe, the site is can'b be reached.

Be sure you have not closed the bash in the container because if you exit the services are stopped.

Type 

    sudo docker ps

That should return an empty list or a list not containing your image.

If you type

    sudo docker ps -a 

you should see a line like

    87803fd51b19    webrad-dev    "/bin/sh -c 'service "    36 minutes ago    Exited (130) 3 minutes ago                                                     

indicating that the image was started and you have exited.

In order to continue working, you must start the image again  with 'docker run'.

