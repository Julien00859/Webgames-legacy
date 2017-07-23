/*
g_name
g_status
g_path
g_executable
*/

const {Game} = require('../model/queue-model');

function getAllStates(req, res) {
  Game.findAll().then(games => {
    if (!games) {
      res.status(204).send({error: "No games..."});
      return;
    }
    const states = games.map(game => {
      return {
        g_name: game.g_name,
        g_status: game.g_status,
        g_numbers_players_needed: game.g_numbers_players_needed
      }
    });
    res.status(200).json(states);
  }).catch(error => res.status(500).json({error}));
}

function getState(req, res) {
  const {name} = req.params;
  Game.find({where: {g_name: name}}).then(game => {
    if (!game) {
      res.status(204).send({error: `Game ${name} does not exist.`});
      return;
    }
    res.status(200).json(game.g_state);
  }).catch(error => res.status(500).json({error}));
}

function getActives(req, res) {
  Game.findAll().then(games => {
    if (!games) {
      res.status(204).send({error: "No games..."});
      return;
    }
    const actives = games.filter(game => game.g_status);
    res.status(200).json(actives);
  }).catch(error => res.status(500).json({error}));
}

function removeGame(req, res) {
  const {name} = req.body;
  Game.destroy({where: {g_name: name}}).then(rowAffected => {
    res.status(200).json({success: 'game deleted'});
  }).catch(error => res.status(500).send({error}));
}

module.exports = {
  getAllStates,
  getState,
  getActives,
  removeGame
}
