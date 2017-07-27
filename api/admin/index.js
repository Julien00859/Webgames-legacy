const {promisify} = require('util');
const http = require('http');
const path = require('path');
const fs = require('fs');
const express = require('express');
const adaro = require('adaro');
const compression = require('compression');
const serveStatic = require('serve-static');
const app = express();
const router = express.Router();
const admin = require('../common-middlewares/admin');
const {Game} = require('../queue/model/queue-model.js');
const {NODE_ENV} = require("../config");

const production = NODE_ENV === 'production';
const staticPath = path.resolve(__dirname, 'static');
const swPath = path.resolve(__dirname, 'service-worker.js');
const templatePath = path.resolve(__dirname, 'template');

const dustOptions = {
  cache: production ? true : false,
  whitespace: production ? false : true,
  helpers: []
};

const viewOptions = {
  style: '/admin/static/style.css',
  script: '/admin/static/bundle.js'
};

app.engine('dust', adaro.dust(dustOptions));
app.set('view engine', 'dust');
app.set('views', templatePath);

router.use(compression());
router.use('/static', serveStatic(staticPath, {
  maxAge: production ? 31536000000 : 0
}));

router.use('/sw.js', serveStatic(swPath, {
  maxAge: 0 // never cache the service-worker !
}));

// routes
// login is handled by auth api.
router.get('/', admin, (req, res) => {
  Game.findAll({order: [['g_name', 'ASC']]}).then(games => {
    if (!games) {
      res.status(404).send({error: "Aucun jeux n'existe..."});
      return;
    }
    res.status(200).render('sections/admin',
    Object.assign(viewOptions, {
      games
    }));
  }).catch(error => res.status(500).json({error}));
});

router.get('/login', (req, res) => {
  res.status(200).render('sections/login', viewOptions);
});


app.use(router);

module.exports = app;
