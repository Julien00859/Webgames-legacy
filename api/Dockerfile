FROM mhart/alpine-node:latest

# Create app directory
RUN mkdir -p /usr/src/app


# Copy only package.json
# We leverage the cache
ADD package.json /tmp/package.json

# Install dependencies
WORKDIR /tmp
RUN yarn

# Copy dependencies
RUN cp -a /tmp/node_modules /usr/src/app

# Copy stuff
WORKDIR /usr/src/app
ADD . .

# Install dockerise
RUN apk update \
	&& apk add ca-certificates wget \
	&& update-ca-certificates
RUN wget https://github.com/jwilder/dockerize/releases/download/v0.5.0/dockerize-alpine-linux-amd64-v0.5.0.tar.gz
RUN tar -C /usr/local/bin -xzf dockerize-alpine-linux-amd64-v0.5.0.tar.gz
RUN rm dockerize-alpine-linux-amd64-v0.5.0.tar.gz

EXPOSE 5000
