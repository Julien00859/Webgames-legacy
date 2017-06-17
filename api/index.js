const http = require('http');
const express = require('express');
const dotenv = require('dotenv').config();
const session = require('express-session');
const RedisStore = require('connect-redis')(session);
const bodyParser = require('body-parser');
const app = express();
const router = express.Router();
const PORT = process.env.PORT || 5000;

router.use(bodyParser.json());
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

app.use(router);

http.createServer(app).listen(PORT, _ => {
  console.log(`[WebGames] API listening on http://localhost:${PORT}`);
});
