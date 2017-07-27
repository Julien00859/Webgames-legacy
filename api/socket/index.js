const net = require('net');
const jwt = require('jsonwebtoken')
const {MANAGER_HOST, MANAGER_TCP_PORT, JWT_SECRET} = require("../config");
const socket = new net.Socket();
const token = jwt.sign({id: 1, type: 'api'}, JWT_SECRET);
let attempt = 5;
let toSend = [];

function tryConnect() {
  console.log(`Try to connect the Queue Manager at ${MANAGER_HOST}:${MANAGER_TCP_PORT} (${attempt} attemps left)`);
  socket.connect(MANAGER_TCP_PORT, MANAGER_HOST);
}
tryConnect();

function send(line) {
  if (!socket.connecting)
    socket.write(`${token} ${line}\r\n`);
  else
    toSend.push(line);
}

socket.on('connect', () => {
  console.log(`[WebGames] Connected to the Queue Manager.`);
  if (toSend.length)
    for (let line of toSend)
      socket.write(line);
})

socket.on('data', data => {
  if (Buffer.isBuffer(data))
    data = data.toString();
  for (let line of data.split('\r\n')) {
    args = line.split(' ');
    switch (args[0]) {
      case 'ping':
        send(`pong ${args[1]}`);
        break;
    }
  }
});

socket.on('error', err => {
  if ((err.code === 'ECONNREFUSED' || err.code === 'EADDRNOTAVAIL') && attempt--)
    setTimeout(tryConnect, 2000);
  else
    console.error(`[WebGames] Connection to the Queue Manager closed due to ${err}.`);
});
socket.on('close', with_err => {
  if (!with_err)
    console.log('[WebGames] Connection to the Queue Manager closed.')
});
socket.on('end', _ => console.log('[WebGames] The Queue Manager closed the connection.'));

module.exports = socket;
