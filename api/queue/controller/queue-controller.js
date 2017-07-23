const {Game} = require('../model/queue-model');
const socket = require('../../socket');

function getAllQueues(req, res) {
  Game.findAll().then(games => {
    if (! games) {
      res.status(204);
      return;
    }
    res.status(200).json(games.map(game => game.name));
  }).catch(error => res.status(500).json({error}));
}

function getActivesQueues(req, res) {
  Game.findAll().then(games => {
    if (! games) {
      res.status(204);
      return;
    }
    res.status(200).json(games.filter(game => game.g_status).map(game => game.name));
  }).catch(error => res.status(500).json({error}));
}

function getQueueObject(req, res) {
  const {name} = req.params;
  Game.find({where: {g_name: name}}).then(game => {
    if (!game) {
      res.status(404).json({error: `The game '${name}' does not exist.`});
      return;
    }
    res.status(200).json(game);
  })
}

function getQueueValue(req, res) {
  const {name, attr} = req.params;
  Game.find({where: {g_name: name}}).then(game => {
    if (!game) {
      res.status(404).json({error: `The game '${name}' does not exist.`});
      return;
    }
    if (!(attr in game)) {
      res.status(404).json({error: `The attribute '${attr}' does not exist.`});
      return;
    }
    res.status(200).json(game[attr]);
  }).catch(error => res.status(500).json({error}));
}

function createQueue(req, res) {
  const {g_name} = req.body;

  Game.findOrCreate({where: {g_name}, defaults: req.body}).spread((game, created) => {
    if (!created) { // existe déjà
      return res.status(400).json({error: `Game ${game.g_name} already exists.`});
    }
    res.status(200).json({success: 'Game succefully created !'});
  }).catch(error => {
    return res.status(500).send({error});
  });
}

function deleteQueue(req, res) {
  const {name} = res.params;

  Game.destroy({where: {g_name: name}}).then(rowAffected => {
    res.status(200).json({success: `game '${name}' deleted`});
  }).catch(error => res.status(500).json({error}));
}

function updateQueueObject(req, res) {
  const {name} = req.params

  Game.update(req.body, {where: {g_name: name}, fields: Object.keys(req.body), returning: true})
    .spread((rowAffected, update) => {
      res.status(200).json({success: 'game updated.'});
      socketCommand('update', name);
    })
    .catch(error =>  res.status(500).send({error: error.toString()}));
}

function getJWT() {
  return jwt.sign({
    id: 1,
    type: 'api'
  }, process.env.SECRET, {
    expiresIn: '12h',
    subject: 'webgames'
  });
}

function socketCommand(command, game) {
  const jwt = getJWT();
  socket.write(getJWT() + ' ' + command + ' ' + game + '\r\n', 'utf-8', _ => {
    console.log('commande envoyée avec succès au manager.');
  });
}

module.exports = {
  getAllQueues,
  getActivesQueues,
  getQueueObject,
  getQueueValue,
  createQueue,
  deleteQueue,
  updateQueueObject
}
