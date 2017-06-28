/*
g_name
g_state
g_directory
g_executable
*/

const {Game} = require('../model/queue-model');

function getAllStates(req, res) {
  Game.findAll().then(games => {
    if (!games) {
      res.status(404).send({error: "Aucun jeux n'existe..."});
    }
    const states = games.map(game => game.g_state);
    res.status(200).json(states);
  }).catch(error => res.status(500).json({error}));
}

function getState(req, res) {
  const {name} = req.body;
  Game.find({where: {g_name: name}}).then(game => {
    if (!game) {
      res.status(404).send({error: `Le jeu ${name} n'existe pas.`});
    }
    res.status(200).json(game.g_state);
  }).catch(error => res.status(500).json({error}));
}

function deleteGame(req, res) {
  const {name} = req.body;
  Game.destroy({where: {g_name: name}})..then(rowAffected => {
    res.status(200).json({success: 'jeu supprimé'});
  }).catch(error => res.status(500).send({error}));
}
