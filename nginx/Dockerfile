FROM nginx:alpine

# Install dockerize
RUN apk update \
	&& apk add ca-certificates wget \
	&& update-ca-certificates
RUN wget https://github.com/jwilder/dockerize/releases/download/v0.5.0/dockerize-alpine-linux-amd64-v0.5.0.tar.gz
RUN tar -C /usr/local/bin -xzf dockerize-alpine-linux-amd64-v0.5.0.tar.gz
RUN rm dockerize-alpine-linux-amd64-v0.5.0.tar.gz

