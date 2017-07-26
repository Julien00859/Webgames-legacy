const net = require('net');
const {MANAGER_HOST, MANAGER_PORT} = require("../config");

const socket = new net.Socket();

socket.connect(MANAGER_PORT, MANAGER_HOST, _ => {
  console.log(`[WebGames] Connected to the Queue Manager.`);
});

socket.on('end', _ => console.log('[WebGames] Queue Manager disconnected.'));

module.exports = socket;
