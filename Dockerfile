FROM python:3.5
MAINTAINER Julien Castiaux
RUN git clone https://www.github.com/Julien00859/Webgames && cd Webgames && git checkout v3 
RUN pip install -r Webgames/requirements.txt
WORKDIR /Webgames
EXPOSE 80
CMD python server.py
