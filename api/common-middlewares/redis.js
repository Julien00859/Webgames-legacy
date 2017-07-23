const session = require('express-session');
const RedisStore = require('connect-redis')(session);

const redis = session({
  secret: process.env.SECRET,
  name: 'local',
  store: new RedisStore({
    host: process.env.REDIS_HOST,
    port: 6379,
    db: 1
  }),
  proxy: false,
  resave: false,
  saveUninitialized: false
});

module.exports = redis;
