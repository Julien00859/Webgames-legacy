const http = require('http');
const express = require('express');
const path = require('path');
const jwt = require('../common-middlewares/jwt');
const jwtAdmin = require('../common-middlewares/admin');
const {getAllStates, getState, getActives, removeGame} = require('./controller/queue-controller');

const app = express();
const router = express.Router();

// routes
router.get('/states', jwt, getAllStates);
router.get('/state/:name', jwt, getState);
router.get('/actives', jwt, getActives)
router.delete('/remove', jwt, removeGame);

app.use(router);

module.exports = app;
