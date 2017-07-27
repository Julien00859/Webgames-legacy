const session = require('express-session');
const RedisStore = require('connect-redis')(session);
const {REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB_API} = require("../config");

const redis = session({
  secret: REDIS_PASSWORD,
  name: 'local',
  store: new RedisStore({
    host: REDIS_HOST,
    port: REDIS_PORT,
    db: REDIS_DB_API
  }),
  cookie: {
    maxAge: 1000 * 60 * 60 * 12
  },
  proxy: false,
  resave: false,
  saveUninitialized: false
});

module.exports = redis;
