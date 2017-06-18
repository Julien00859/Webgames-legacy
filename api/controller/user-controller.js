/*
tbusers
u_name
u_email
u_hash
u_reset_password_token
u_reset_expiration
*/

const promisify = require('es6-promisify');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const {User, hashPassword, verifyPassword, generateJWT} = require('../model/user-model');

passport.use(new LocalStrategy({
    usernameField: 'username',
    passwordField: 'password',
    passReqToCallback: false,
    session: false
  }, (username, password, done) => {
    User.findOne({where: {u_name: username}}).then(user => {
      if (!user) return done(null, false); // no user
      return verifyPassword(password, user.u_hash)
        .then(response => {
          if (response) { // password ok
            return done(null, user); // user
          }
          return done(null, false); // password ko
        }).catch(error => done(error));
    }).catch(error => done(error));
  }
));

function register(req, res) {
  const {username, mail, password} = req.body;
  const hash =
    hashPassword(password)
      .then(hash => hash)
      .catch(error => res.status(500).send({error}));

  console.log(hash);

  // .spread(user, created) = .then([user, created])
  User.findOrCreate({where: {u_name: username}, defaults: {u_email: mail, u_hash: hash}}).spread((user, created) => {
    if (!created) {
      return res.status(400).send({error: `le nom d'utilisateur ${user.u_email} est indisponible`});
    }
    res.status(200).send({success: 'Utilisateur créé avec succès !'});
    return res.redirect('/');
  });
}

function login(req, res) {
  const {username, mail, password} = req.body;

  promisify(passport.authenticate, passport)('local').then((user) => {
    if (!user) {
      return res.status(404).send({error: `utilisateur (${username}) non trouvé`});
    }
    const token = generateJWT(user);
    return res.send(200).send({token});
  }).catch(error => {
    return res.status(500).send({error});
  });
}

function resetPassword() {

}

function logout() {

}

module.exports = {
  register,
  login,
  resetPassword,
  logout
}
