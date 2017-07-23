const http = require('http');
const express = require('express');
const path = require('path');
const jwt = require('../common-middlewares/jwt');
const jwtAdmin = require('../common-middlewares/admin');
const {getAllQueues, getActivesQueues, getQueueObject, getQueueValue, createQueue, deleteQueue, updateQueueObject} = require('./controller/queue-controller');

const app = express();
const router = express.Router();

router.get('/', jwt, jwtAdmin, getAllQueues);
router.get('/actives', jwt, jwtAdmin, getActivesQueues);
router.get('/:name', jwt, jwtAdmin, getQueueObject);
router.get('/:name/:attr', jwt, jwtAdmin, getQueueValue);
router.post('/:name', jwt, jwtAdmin, createQueue);
router.put('/:name', jwt, jwtAdmin, updateQueueObject);
router.delete('/:name', jwt, jwtAdmin, deleteQueue);

app.use(router);

module.exports = app;
