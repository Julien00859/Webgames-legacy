const http = require('http');
const path = require('path');
const express = require('express');
const bodyParser = require('body-parser');
const validator = require('express-validator');
const passport = require('passport');
const blacklist = require('express-jwt-blacklist');
const redis = require('./common-middlewares/redis');
const postgres = require('./postgres');
const app = express();
const dotenv = require('dotenv').config();

const PORT = process.env.PORT || 5000;

router.use(passport.initialize());
router.use(bodyParser.json());
router.use(validator());
router.use(bodyParser.urlencoded({
  extended: true
}));
router.use(redis);

postgres.sync();

blacklist.configure({
  store: {
    type: 'redis'
  }
});

router.get('/check', (req, res) => res.send('api server ok.'));
router.use('/api/auth', require('admin'));
router.use('/api/queue', require('queue'));
router.use('/api/admin', require('admin'));

http.createServer(app).listen(PORT, _ => {
  console.log(`[WebGames] Admin page running on http://localhost:${PORT}`);
});

app.use(router);
