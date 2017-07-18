const http = require('http');
const express = require('express');
const path = require('path');
const jwt = require('../common-middlewares/jwt');
const {validateLogin, validateRegister, validateForgot, validateReset} = require('./middlewares/validator');
const {register, login, loginAdmin, resetPasswordForm, resetPassword, getResetToken, getCurrentAccount, getAccount, updateAccount, logout, unregister} = require('./controller/user-controller');
const app = express();
const router = express.Router();

router.get('/account', jwt, getCurrentAccount);
router.get('/account/reset', resetPasswordForm);
router.get('/account/:id', getAccount);
router.post('/register', validateRegister, register);
router.post('/login', validateLogin, login);
router.post('/login/admin', validateLogin, loginAdmin);
router.post('/forgot', validateForgot, getResetToken);
router.put('/account/reset', validateReset, resetPassword);
router.put('/account/update', jwt, updateAccount);
router.delete('/logout', jwt, logout);
router.delete('/account/unregister', jwt, unregister);

app.use(router);

module.exports = app;
