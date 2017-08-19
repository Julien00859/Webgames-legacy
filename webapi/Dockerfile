FROM python:latest

# Create app directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install app dependencies
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt

# Bundle app source
ADD . /usr/src/app

# Install dockerize
RUN wget https://github.com/jwilder/dockerize/releases/download/v0.5.0/dockerize-linux-amd64-v0.5.0.tar.gz
RUN tar -C /usr/local/bin -xzf dockerize-linux-amd64-v0.5.0.tar.gz
RUN rm dockerize-linux-amd64-v0.5.0.tar.gz

EXPOSE 4173 4174 4175
CMD ["python", "start.py"]
