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
const Sequelize = require('sequelize');
const sequelize = require('../postgres');

const User = sequelize.define('user', {
  u_id: {
    primaryKey: true,
    type: Sequelize.UUIDV4,
    allowNull: false
  },
  u_name: {
    type: Sequelize.STRING(24),
    allowNull: false,
    unique: 'compositeIndex',
    validate: {
      len: [3, 24]
    }
  },
  u_email: {
    type: Sequelize.STRING,
    allowNull: false,
    unique: 'compositeIndex',
    validate: {
      isEmail: true
    }
  },
  u_hash: {
    type: Sequelize.STRING,
    allowNull: false
  },
  u_reset_password_token: {
    type: Sequelize.STRING(20)
  },
  u_reset_password_expiration: {
    type: Sequelize.DATE
  }
});

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
  return jwt.sign({
      _id: user.u_id,
      name: user.u_name,
      email: user.u_email
  }, process.env.SECRET, {expiresIn: '1h'});
}

module.exports = {
  User,
  hashPassword,
  verifyPassword,
  generateJWT
};
