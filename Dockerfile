FROM ubuntu:trusty
MAINTAINER Sydney Li

WORKDIR /opt/starttls-everywhere

ENV DEBIAN_FRONTEND noninteractive
ENV NAME valid-example-recipient

# add-apt-repository is not in base image, so we need to install it.
RUN apt-get update
RUN apt-get install -y software-properties-common

# Add required package listings
RUN add-apt-repository -y ppa:certbot/certbot
RUN apt-get update

# Install dependencies
RUN apt-get install -y certbot postfix dnsmasq mutt vim
RUN apt-get install -y gcc
RUN apt-get install -y musl-dev libffi-dev
RUN apt-get install -y bash

# Install python dependencies
RUN apt-get install -y python python-pip
RUN pip install python-dateutil

# Docker-shared has certs and initial config files.
# TODO (sydli): we shouldn't have to load configs-- we should have
# the certbot plugin configure it for us (in particular, hostname discovery)
ADD docker-shared/ .
ADD certbot-postfix/ certbot-postfix/
ADD starttls-policy/ starttls-policy/

# Use editable flag here to take advantage of image caching.
# Should remove for production docker image.
RUN pip install --editable starttls-policy
RUN pip install --editable certbot-postfix


# Adding test-related files
ADD scripts scripts
ADD tests tests

ADD certbot-postfix/certbot_postfix/test_data/config.json config.json 
ADD certbot-postfix/certbot_postfix/test_data/test-email.txt test-email.txt 

EXPOSE 25 587

