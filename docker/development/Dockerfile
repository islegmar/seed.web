FROM php:5.6-apache

RUN apt-get update \
  && apt-get install -y apt-utils \                                           
  && { \
      echo debconf debconf/frontend select Noninteractive; \
      echo mysql-community-server mysql-community-server/data-dir \
          select ''; \
      echo mysql-community-server mysql-community-server/root-pass \
          password ''; \
      echo mysql-community-server mysql-community-server/re-root-pass \
          password ''; \
      echo mysql-community-server mysql-community-server/remove-test-db \
          select true; \
  } | debconf-set-selections 

RUN apt-get -y install \
  sudo \
  vim \
  php-pear \
  php5-dev \
  libmysqlclient15-dev \
  libpq-dev \
  mysql-client \
  mysql-server \
  python 
RUN docker-php-ext-install pdo pdo_mysql pdo_pgsql

RUN mkdir /var/www/html/fe   && chmod 777 /var/www/html/fe
RUN mkdir /var/www/html/be   && chmod 777 /var/www/html/be
RUN mkdir /var/www/html/logs && chmod 777 /var/www/html/logs
RUN mkdir /var/www/html/data && chmod 777 /var/www/html/data
RUN mkdir /var/www/html/config
RUN a2enmod rewrite           
COPY myapp.php /var/www/html/config

# -------------------------------------------------
# We create a user developer:developer having the same
# permissions that the user in the host, so in case any
# file is created, the permissions match
# -------------------------------------------------
# Put your uid, gid
ARG UID
ARG GID
RUN export uid=$UID gid=$GID && \
    mkdir -p /home/developer && \
    mkdir -p /etc/sudoers.d  && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${gid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer
USER developer
ENV HOME /home/developer

COPY .bashrc   /home/developer
COPY setenv.sh /home/developer

# Start services
ENTRYPOINT sudo service mysql restart && sudo service apache2 restart && bash
