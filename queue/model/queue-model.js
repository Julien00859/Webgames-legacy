const Sequelize = require('sequelize');
const sequelize = require('../../postgres');

const Game = sequelize.define('game', {
  g_name: {
    primaryKey: true,
    type: Sequelize.STRING(50)
  },
  g_status: {
    type: Sequelize.BOOLEAN,
    allowNull: false,
    defaultValue: true
  },
  g_numbers_players_needed: {
    type: Sequelize.INT,
    allowNull: false
  },
  g_path: {
    type: Sequelize.STRING
  },
  g_executable: {
    type: Sequelize.STRING
  }
});

module.exports = {
  Game
}
