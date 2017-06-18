const Sequelize = require('sequelize');
const sequelize = require('../postgres');

const Game = sequelize.define('game', {
  g_name: {
    primaryKey: true,
    type: Sequelize.STRING(24)
  },
  g_enabled: {
    type: Sequelize.BOOLEAN,
    allowNull: false,
    defaultValue: true
  },
  g_directory: {
    type: Sequelize.STRING
  },
  g_executable: {
    type: Sequelize.STRING
  },
  g_tcp_port_count: {
    type: Sequelize.INTEGER
  },
  g_udp_port_count: {
    type: Sequelize.INTEGER
  }
});

module.exports = {
  Game
}
