const http = require('http');
const path = require('path');
const express = require('express');
const app = express();

const PORT = process.env.PORT || 5000;

router.use('/api/auth', require('admin'));
router.use('/api/queue', require('queue'));
router.use('/api/admin', require('admin'));

http.createServer(app).listen(PORT, _ => {
  console.log(`[WebGames] Admin page running on http://localhost:${PORT}`);
});

app.use(router);
