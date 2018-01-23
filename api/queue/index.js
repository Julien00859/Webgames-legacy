const http = require('http');
const express = require('express');
const path = require('path');
const jwt = require('../common-middlewares/jwt');
const jwtAdminOrManager = require('../common-middlewares/admin');
const {getAllQueues, getActivesQueues, getQueueObject, getQueueValue, createQueue, deleteQueue, updateQueueObject} = require('./controller/queue-controller');

const app = express();
const router = express.Router();

router.get('/', jwt, jwtAdminOrManager, getAllQueues);
router.get('/actives', jwt, jwtAdminOrManager, getActivesQueues);
router.get('/:name', jwt, jwtAdminOrManager, getQueueObject);
router.get('/:name/:attr', jwt, jwtAdminOrManager, getQueueValue);
router.post('/:name', jwt, jwtAdminOrManager, createQueue);
router.put('/:name', jwt, jwtAdminOrManager, updateQueueObject);
router.delete('/:name', jwt, jwtAdminOrManager, deleteQueue);

app.use(router);

module.exports = app;
