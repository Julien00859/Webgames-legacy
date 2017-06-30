const dotenv = require('dotenv').config();
const {Game} = require('../queue/model/queue-model.js');
const games = require('./games');

// insert the games in db
module.exports = _ => Game.bulkCreate(games).catch(error => console.error(error.stack));
