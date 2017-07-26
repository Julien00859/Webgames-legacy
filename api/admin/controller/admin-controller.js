const {Game} = require('../../queue/model/queue-model.js');
const {JWT_SECRET} = require("../../config")
//const socket = require('../../socket');

function getJWT() {
  return jwt.sign({
    id: 1,
    type: 'api'
  }, JWT_SECRET, {
    expiresIn: '12h',
    subject: 'webgames'
  });
}

function updateGame(req, res) {
  Game.update(req.body, {where: {g_name: req.body.g_name}, fields: Object.keys(req.body), returning: true})
    .spread((rowAffected, update) => {
      res.status(200).json({success: 'infos du jeu mises à jour.'});
      socketCommand('update', req.body.g_name);
    })
    .catch(error =>  res.status(500).send({error: error.toString()}));
}

function socketCommand(command, game) {
  const jwt = getJWT();
  socket.write(getJWT() + ' ' + command + ' ' + game + '\r\n', 'utf-8', _ => {
    console.log('commande envoyée avec succès au manager.');
  });
}

module.exports = {
  updateGame
}
