const http = require('http');
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const postgres = require('./postgres');
const validator = require('express-validator');
const redis = require('../common-middlewares/redis');
const passport = require('passport');
const blacklist = require('express-jwt-blacklist');
const jwt = require('../common-middlewares/jwt');
const dotenv = require('dotenv').config({
  path: path.resolve(__dirname, '..')
});

const app = express();
const router = express.Router();
const PORT = process.env.PORT || 5001;
postgres.sync();

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

// routes

app.use(router);

http.createServer(app).listen(PORT, _ => {
  console.log(`[WebGames] API listening on http://localhost:${PORT}`);
});

module.exports = app;
