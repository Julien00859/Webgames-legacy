const http = require('http');
const express = require('express');
const dotenv = require('dotenv').config();
const bodyParser = require('body-parser');
const postgres = require('./postgres');
const validator = require('express-validator');
const session = require('express-session');
const RedisStore = require('connect-redis')(session);
const passport = require('passport');
const jwt = require('./middlewares/jwt');
const {validateLogin, validateRegister} = require('./middlewares/validator');
const {register, login, resetPassword, getResetToken, getCurrentAccount, getAccount, logout} = require('./controller/user-controller');

const app = express();
const router = express.Router();
const PORT = process.env.PORT || 5000;
postgres.sync();

router.use(passport.initialize());
router.use(jwt);
router.use(bodyParser.json());
router.use(validator());
router.use(bodyParser.urlencoded({
  extended: true
}));

router.use(session({
  secret: process.env.SECRET,
  name: 'local',
  store: new RedisStore({
    host: '127.0.0.1',
    port: 6379
  }),
  proxy: false,
  resave: false,
  saveUninitialized: false
}));

router.get('/check', (_, res) => res.send('api server ok.'));
router.get('/api/logout', jwt, logout);
router.get('/api/account', jwt, getCurrentAccount);
router.get('/api/account/:u_id', getAccount);
router.post('/api/register', validateRegister, register);
router.post('/api/login', validateLogin, login);
router.post('/api/forgot', getResetToken);
router.post('/api/account/reset/:token', resetPassword);

app.use(router);

http.createServer(app).listen(PORT, _ => {
  console.log(`[WebGames] API listening on http://localhost:${PORT}`);
});

module.exports = app;
