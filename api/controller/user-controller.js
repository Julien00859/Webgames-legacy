/*
u_name
u_email
u_hash
u_reset_password_token
u_reset_expiration
*/

const pgp = require('../postgres');
const {hashPassword, verifyPassword, generateJWT} = require('../model/user-model');

function login() {
  const {name, mail, password} = req.body;
}

function resetPassword() {

}

function logout() {

}

module.exports.login = login;
module.exports.resetPassword = resetPassword;
module.exports.logout = logout;
