FROM python:3.8
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y sqlite3 libsqlite3-dev
RUN apt-get install -y python3-pip
RUN mkdir /db
RUN mkdir /home/api
WORKDIR /home/api
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 3000
