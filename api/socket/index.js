const net = require('net');
const {MANAGER_HOST, MANAGER_PORT} = require("../config");
const socket = new net.Socket();
let attempt = 0;

socketConnection();

function socketConnection() {
  socket.connect(MANAGER_PORT, MANAGER_HOST, _ => {
    console.log(`[WebGames] Connected to the Queue Manager.`);
  });
}

socket.on('error', err => {
  if (err.code === 'ECONNREFUSED' || err.code === 'EADDRNOTAVAIL') {
    console.log(attempt);
    if (attempt < 5) {
      setTimeout(_ => socketConnection(), 2000);
      attempt++;
    } else {
      console.error('Impossible to connect to Queue Manager.');
    }
  }
});

socket.on('end', _ => console.log('[WebGames] Queue Manager disconnected.'));

module.exports = socket;
