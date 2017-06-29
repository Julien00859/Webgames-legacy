/*
g_name
g_status
g_path
g_executable
*/

const {Game} = require('../model/queue-model');
const socket = require('../../socket');

function getJWT() {
  return jwt.sign({
    id: 1,
    type: 'api'
  }, process.env.SECRET, {
    expiresIn: '12h',
    subject: 'webgames'
  });
}

function getAllStates(req, res) {
  Game.findAll().then(games => {
    if (!games) {
      res.status(404).send({error: "Aucun jeux n'existe..."});
      return;
    }
    const states = games.map(game => game.g_status);
    res.status(200).json(states);
  }).catch(error => res.status(500).json({error}));
}

function getState(req, res) {
  const {name} = req.params;
  Game.find({where: {g_name: name}}).then(game => {
    if (!game) {
      res.status(404).send({error: `Le jeu ${name} n'existe pas.`});
      return;
    }
    res.status(200).json(game.g_state);
  }).catch(error => res.status(500).json({error}));
}

function onSocketCommand(req, res) {
  const {command, game} = req.body;
  const jwt = getJWT();
  socket.write(getJWT() + ' ' + command + ' ' + game + '\r\n', 'utf-8', _ => {
    res.status(200).send('commande envoyée avec succès au manager.');
  });
}

function removeGame(req, res) {
  const {name} = req.body;
  Game.destroy({where: {g_name: name}}).then(rowAffected => {
    res.status(200).json({success: 'jeu supprimé'});
  }).catch(error => res.status(500).send({error}));
}

module.exports = {
  getAllStates,
  getState,
  onSocketCommand,
  removeGame
}
