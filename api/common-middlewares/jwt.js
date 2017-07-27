const jwt = require('express-jwt');
const blacklist = require('express-jwt-blacklist');
const {JWT_SECRET} = require("../config");

module.exports = jwt({
  secret: JWT_SECRET,
  isRevoked: blacklist.isRevoked,
  getToken: function (req) {
    if (req.headers.authorization && req.headers.authorization.split(' ')[0] === 'Bearer') {
      return req.headers.authorization.split(' ')[1];
    } else if (req.cookies && req.cookies.jwt) {
      return req.cookies.jwt;
    }
    return null;
  }
});
