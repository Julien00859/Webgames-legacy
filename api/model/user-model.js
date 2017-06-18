/*
u_name
u_email
u_hash
u_reset_password_token
u_reset_expiration
*/

const promisify = require('es6-promisify');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

function hashPassword(password) {
  return promisify(bcrypt.genSalt, bcrypt)(10)
    .then(salt => bcrypt.hash(password, salt))
    .then(hash => hash)
    .catch(error => error);
}

function verifyPassword(sentPassword, dbPassword) {
  return promisify(bcrypt.compare, bcrypt)(sentPassword, dbPassword)
    .then(response => response)
    .catch(error => error);

}

function generateJWT(user) {
  jwt.sign({
      _id: user.u_id,
      name: user.u_name,
      email: user.u_email
  }, process.env.SECRET, {expiresIn: '1h'});
}

module.exports = {
  hashPassword,
  verifyPassword,
  generateJWT
};
