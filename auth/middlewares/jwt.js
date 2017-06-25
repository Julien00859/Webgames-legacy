const jwt = require('express-jwt');
const blacklist = require('express-jwt-blacklist');

module.exports = jwt({secret: process.env.SECRET, isRevoked: blacklist.isRevoked});
