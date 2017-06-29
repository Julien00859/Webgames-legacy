const {Game} = require('../../queue/model/queue-model.js');

function getAllGames(req, res) {
  Game.findAll().then(games => {
    if (!games) {
      res.status(404).send({error: "Aucun jeux n'existe..."});
      return;
    }
    res.status(200).json(games);
  }).catch(error => res.status(500).json({error}));
}

module.exports = {
  getAllGames
}
