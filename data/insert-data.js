const path = require('path');
const dotenv = require('dotenv').config();
const {Game} = require('../queue/model/queue-model');
const {User} = require('../auth/model/user-model');
const games = require('./games');
const admins = require('./admins');

// insert the games in db
Promise.all([
  Game.bulkCreate(games),
  User.bulkCreate(admins)
]).then(_ => process.exit(0))
  .catch(error => console.error(error.stack));
