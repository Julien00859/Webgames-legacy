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

const production = process.env.NODE_ENV === 'production';
const PORT = process.env.PORT || 5002;
const staticPath = './static';
const templatePath = './template';

const dustOptions = {
  cache: production ? true : false,
  whitespace: production ? false : true,
  helpers: []
};

const viewOptions = {
  style: path.join(staticPath, 'style.css')
};

router.engine('dust', adaro.dust(dustOptions));
router.set('view engine', 'dust');
router.set('views', templatePath);

router.use(compression());
router.use('/static', serveStatic(staticPath, {
  maxAge: production ? 31536000000 : 0
}));

router.use((err, req, res, next) => {
  if (err.name === 'UnauthorizedError') {
    res.status(401).send('invalid token...');
    res.redirect('/login');
  }
});

// routes
// login is handled by auth api.
router.get('/', (req, res) => res.redirect('/admin'));

router.get('/login', (req, res) => {
  res.status(200).render('sections/login');
});

router.get('/admin', jwt, (req, res) => {
  res.status(200).render('sections/admin',
  Object.assign(viewOptions, {
    // db info
  }));
});

http.createServer(app).listen(PORT, _ => {
  console.log(`[WebGames] Admin page running on http://localhost:${PORT}`);
});

app.use(router);

module.exports = app;
