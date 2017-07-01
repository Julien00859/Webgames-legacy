const {Game} = require('../../queue/model/queue-model.js');

function updateGame(req, res) {
  Game.update(req.body, {where: {g_name: req.body.g_name}, fields: Object.keys(req.body), returning: true})
    .spread((rowAffected, update) => res.status(200).send('infos du jeu mises à jour.'))
    .catch(error =>  res.status(500).send({error: error.toString()}));
}

module.exports = {
  updateGame
}
