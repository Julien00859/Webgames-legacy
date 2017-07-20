FROM alpine-node:latest

# Create app directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy all stuff
COPY . .

# Update npm and install dependencies
RUN npm install --global npm
RUN npm install

# Install dockerise
RUN apk update \
	&& apk add ca-certificates wget \
	&& update-ca-certificates
RUN wget https://github.com/jwilder/dockerize/releases/download/v0.5.0/dockerize-alpine-linux-amd64-v0.5.0.tar.gz
RUN tar -C /usr/local/bin -xzf dockerize-alpine-linux-amd64-v0.5.0.tar.gz
RUN rm dockerize-alpine-linux-amd64-v0.5.0.tar.gz

EXPOSE 5000
CMD ["npm", "run", "server"]
