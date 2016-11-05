FROM php:5.6-apache

ARG PRJ_NAME

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install \
  vim \
  php-pear \
  php5-dev \
  libmysqlclient15-dev \
  libpq-dev \
  mysql-client \
  mysql-server \
  python 
RUN docker-php-ext-install pdo pdo_mysql pdo_pgsql

RUN mkdir /var/www/html/logs && chmod 777 /var/www/html/logs
RUN mkdir /var/www/html/data && chmod 777 /var/www/html/data
RUN mkdir /var/www/html/config
RUN a2enmod rewrite           

RUN mkdir /root/apps
COPY $PRJ_NAME.tar /root/apps
COPY start.sh /root
COPY expand.sh /root
COPY deploy.sh /root

#RUN service mysql start && cd /root && ./deploy.sh app && service mysql stop
RUN cd /root && ./deploy.sh $PRJ_NAME

# Start services

# Set AllowOverride                                                 
# RUN cp /etc/apache2/apache2.conf /etc/apache2/apache2.conf.orig     
# RUN /bin/bash -c "sed -i '166s/None/All/' /etc/apache2/apache2.conf"

ENTRYPOINT service mysql restart && service apache2 restart && bash
