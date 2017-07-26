const jwt = require('express-jwt');
const blacklist = require('express-jwt-blacklist');
const {JWT_SECRET} = require("../config")

module.exports = jwt({secret: JWT_SECRET, isRevoked: blacklist.isRevoked});
