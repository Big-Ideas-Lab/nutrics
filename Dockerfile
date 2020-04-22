FROM ubuntu:18.04

LABEL maintainer="Joshua DArcy <jsd42@duke.edu>"

COPY . /app
WORKDIR /app

RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip

RUN pip3 install flask numpy passlib sqlalchemy scipy flask-security flask-sqlalchemy flask-restful flask-jwt-extended


EXPOSE 5001 
ENTRYPOINT [ "python3" ] 
CMD [ "run.py" ]