const http = require('http');
const express = require('express');
const path = require('path');
const jwt = require('../common-middlewares/jwt');
const {getAllStates, getState, onSocketCommand, removeGame} = require('./controller/queue-controller');

const app = express();
const router = express.Router();

// routes
router.get('/states', jwt, getAllStates);
router.get('/state/:name', jwt, getState);
router.post('/command', jwt, onSocketCommand);
router.delete('/remove', jwt, removeGame);

app.use(router);

module.exports = app;
