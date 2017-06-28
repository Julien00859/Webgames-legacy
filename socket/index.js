const net = require('net');
const SOCKET_PORT = process.env.SOCKET_PORT || 4071;
const SOCKET_HOST = process.env.SOCKET_HOST || 'localhost';

const socket = new net.Socket();

socket.connect(SOCKET_PORT, SOCKET_HOST, _ => {
  console.log(`[WebGames] TCP Socket connected on port ${SOCKET_PORT}`);
});

socket.on('end', _ => console.log('[WebGames] TCP Socket disconnected.'));

module.exports = server;
