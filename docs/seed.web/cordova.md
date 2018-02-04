# Support for Cordova

## Preparing the image

Taking as basis the docker's image seed.web

### Cordova

https://cordova.apache.org/docs/en/latest/guide/cli/

    uname -a
    Linux a7992925de9b 4.4.0-109-generic #132-Ubuntu SMP Tue Jan 9 19:52:39 UTC 2018 x86_64 GNU/Linux

So the system is 64 bits.

Install npm

    sudo apt-get update
    sudo apt-get ugrade
    sudo apt-get install wget
    sudo su -
    cd /root/
    curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
    apt-get install -y nodejs
    exit

Install cordova

    sudo npm install -g cordova

docker commit ... cordova

## Install JDK

https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-get-on-ubuntu-16-04

    sudo apt-get install default-jdk


### Install chrome

    sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt-get update 
    sudo apt-get install google-chrome-stable

Still error

    cordova build android
    (node:3471) UnhandledPromiseRejectionWarning: Unhandled promise rejection (rejection id: 1): Error: spawn EACCES


### Install Android-SDK

https://cordova.apache.org/docs/en/latest/guide/platforms/android/index.html

    sudo apt-get install zip 

https://developer.android.com/studio/index.html#downloads

    # wget https://dl.google.com/android/repository/sdk-tools-linux-3859397.zip
    # unzip unzip sdk-tools-linux-3859397.zip -d /opt
    # mv /opt/tools/ /opt/android-sdk-tools

    $ export ANDROID_HOME=/usr/local/android-sdk-tools
    $ export PATH=$PATH:$ANDROID_HOME
    $ export PATH=$PATH:$ANDROID_HOME/bin/

-------------
android sdk studio

    $ sudo chown -R developer:developer /usr/local/android-studio/

Check everything is ok

    $ cd /var/www/html/fe
    $ cordova create hello com.example.hello HelloWorld
    $ cd hello
    $ cordova platform add android
    $ cordova requirements



### Install gradle


https://cordova.apache.org/docs/en/latest/guide/platforms/ubuntu/

    [seed.web-dev]
    sudo apt-get install nodejs npm
    
ZZ



https://cordova.apache.org/docs/en/latest/guide/platforms/ubuntu/

    sudo apt-get install software-properties-common


-------------------------------------------
VKM : https://developer.android.com/studio/run/emulator-acceleration.html?utm_source=android-studio#vm-linux


Minimla SDK : https://askubuntu.com/questions/885658/android-sdk-repositories-cfg-could-not-be-loaded
