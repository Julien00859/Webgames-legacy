const http = require('http');
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const postgres = require('../postgres');
const validator = require('express-validator');
const redis = require('../common-middlewares/redis');
const passport = require('passport');
const blacklist = require('express-jwt-blacklist');
const jwt = require('../common-middlewares/jwt');
const {validateLogin, validateRegister, validateForgot, validateReset} = require('./middlewares/validator');
const {register, login, resetPasswordForm, resetPassword, getResetToken, getCurrentAccount, getAccount, updateAccount, logout, unregister} = require('./controller/user-controller');
const dotenv = require('dotenv').config({
  path: path.resolve(__dirname, '..')
});

const app = express();
const router = express.Router();
const PORT = process.env.PORT || 5000;
postgres.sync();

router.use(passport.initialize());
router.use(bodyParser.json());
router.use(validator());
router.use(bodyParser.urlencoded({
  extended: true
}));

router.use(redis);

blacklist.configure({
  store: {
    type: 'redis'
  }
});

router.get('/check', (_, res) => res.send('api server ok.'));
router.get('/api/account', jwt, getCurrentAccount);
router.get('/api/account/reset', resetPasswordForm);
router.get('/api/account/:id', getAccount); // should fix it to not match whatever after /account/
router.post('/api/register', validateRegister, register);
router.post('/api/login', validateLogin, login);
router.post('/api/forgot', validateForgot, getResetToken);
router.put('/api/account/reset', validateReset, resetPassword);
router.put('/api/account/update', jwt, updateAccount);
router.delete('/api/logout', jwt, logout);
router.delete('/api/account/unregister', jwt, unregister);


app.use(router);

http.createServer(app).listen(PORT, _ => {
  console.log(`[WebGames] API listening on http://localhost:${PORT}`);
});

module.exports = app;
