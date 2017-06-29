const {Game} = require('../queue/model/queue-model.js');
const games = require('./games');

// insert the games in db
Game.bulkCreate(games).catch(error => console.error(error.stack));
