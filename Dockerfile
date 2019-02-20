from ubuntu:latest


ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get -y install python3.6 python3-pip postgresql postgresql-contrib
WORKDIR home/
RUN mkdir link_checker
VOLUME home/link_checker
WORKDIR link_checker/
RUN pip3 install --upgrade pip
RUN pip3 install psycopg2-binary requests

#Get postgres ready
USER postgres
ENTRYPOINT service postgresql start && /bin/bash