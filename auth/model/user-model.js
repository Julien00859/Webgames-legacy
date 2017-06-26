/*
u_name
u_email
u_hash
u_reset_password_token
u_reset_expiration
*/

const {promisify} = require('util');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const Sequelize = require('sequelize');
const sequelize = require('../postgres');

const User = sequelize.define('user', {
  u_id: {
    primaryKey: true,
    type: Sequelize.UUID,
    defaultValue: Sequelize.UUIDV4,
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
    type: Sequelize.STRING
  },
  u_reset_password_expiration: {
    type: Sequelize.DATE
  }
});

function hashPassword(password) {
  return promisify(bcrypt.genSalt)(10)
    .then(salt => bcrypt.hash(password, salt))
    .then(hash => hash)
    .catch(error => error);
}

function verifyPassword(sentPassword, dbPassword) {
  return promisify(bcrypt.compare)(sentPassword, dbPassword)
    .then(response => response)
    .catch(error => error);

}

function generateJWT(user) {
  return jwt.sign({
      _id: user.u_id,
      username: user.u_name,
      mail: user.u_email
  }, process.env.SECRET, {
    expiresIn: '1h',
    subject: 'webgames'
  });
}

module.exports = {
  User,
  hashPassword,
  verifyPassword,
  generateJWT
};
