const session = require('express-session');
const RedisStore = require('connect-redis')(session);

const redis = session({
  secret: process.env.SECRET,
  name: 'local',
  store: new RedisStore({
    host: '127.0.0.1',
    port: 6379
  }),
  proxy: false,
  resave: false,
  saveUninitialized: false
});

module.exports = redis;
