/*
User
u_id
u_admin
u_name
u_email
u_hash
u_reset_password_token
u_reset_expiration
*/

//const {promisify} = require('util');
const promisify = require('es6-promisify');
const fs = require('fs');
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const crypto = require('crypto');
const nodemail = require('nodemailer');
const handlebars = require('handlebars');
const blacklist = require('express-jwt-blacklist');
const {User, hashPassword, verifyPassword, generateJWT} = require('../model/user-model');
const production = process.env.NODE_ENV === 'production';

passport.use(new LocalStrategy({
    usernameField: 'username',
    passwordField: 'password',
    passReqToCallback: false,
    session: true
  }, (username, password, done) => {
    User.find({where: {u_name: username}}).then(user => {
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
  const {password} = req.body;

  hashPassword(password)
    .then(hash => saveUserInDb(req, res, hash))
    .catch(error => res.status(500).json({error}));
}

function saveUserInDb(req, res, hash) {
  const {username, mail} = req.body;
  // .spread(user, created) = .then([user, created])
  User.findOrCreate({where: {u_name: username}, defaults: {u_email: mail, u_hash: hash}}).spread((user, created) => {
    if (!created) { // existe déjà
      return res.status(400).json({error: `le nom d'utilisateur ${user.u_name} est déjà utilisé.`});
    }
    res.status(200).json({success: 'Utilisateur créé avec succès !'});
  }).catch(error => {
    return res.status(500).send({error});
  });
}

function login(req, res) {
  const {username, password} = req.body;

  // NOTE
  // passport.authenticate does not support promisify
  // you have to pass req, res to this method
  passport.authenticate('local',
    {successRedirect: '/', failureRedirect: '/login'}, (error, user) => {
    if (error) {
      return res.status(500).json({error});
    }

    if (!user) {
      return res.status(404).json({error: `utilisateur (${username}) non trouvé / mauvais mot de passe.`});
    }

    const token = generateJWT(user);
    res.status(200).json({token});
  })(req, res);
}

function loginAdmin(req, res) {
  const {username, password} = req.body;

  passport.authenticate('local',
    {successRedirect: '/admin', failureRedirect: '/login'}, (error, user) => {
    if (error) {
      return res.status(500).json({error});
    }

    if (!user) {
      return res.status(404).json({error: `utilisateur (${username}) non trouvé / mauvais mot de passe.`});
    }

    if (!user.u_admin) {
      return res.status(404).json({error: `admin only !`});
    }

    const token = generateJWT(user);
    res.status(200).json({success: "Connecté en tant qu'admin", token});
  })(req, res);
}

function getResetToken(req, res) {
  const {mail} = req.body;
  // récupération de l'utilisateur
  User.find({wbere: {u_email: mail}}).then(user => {
    if (!user) {
      res.status(404).json({error: "Cette e-mail n'appartient à aucun compte utilisateur."});
      return;
    }

    // ajout du token + date d'expiration à son compte
    const token = crypto.randomBytes(20).toString('hex');
    user.update({
      u_reset_password_token: token,
      u_reset_expiration: Date.now() + 3600000
    }).then(rowAffected => {
      // envoi du mail avec le id utilisateur + token
      // title, content, url, action
      const id = user.u_id;
      const options = {
        title: 'Réinitialisation du mot de passe',
        content: `Vous recevez ce mail car vous avez perdu votre mot de passe,
          cliquez sur le lien ci-dessous pour changer de mot de passe.`,
        url: `http://${req.hostname}/api/account/${id}/reset/${token}`,
        action: 'Changer de mot de passe'
      };

      sendMail(mail, options).then(info => {
        res.status(200).json({success: `Email envoyé avec succès à ${mail}. Vous avez 1 heure.`});
      }).catch(error => res.status(500).json({error: error.toString()}));
    }).catch(error => res.status(500).json({error: error.toString()})); // sinon possible d'avoir {} et pas l'erreur
  }).catch(error => res.status(500).json({error}));
}

async function sendMail(mail, options) {
  const transporter = nodemail.createTransport({
    host: production ? process.env.HOSTMAIL : 'localhost',
    port: production ? 465 : 1025, // port pour maildev
    secure: production ? true : false,
    ignoreTLS: production ? false : true,
    auth: production ? {
      user: process.env.USERMAIL,
      pass: process.env.PASSMAIL
    } : false
  });

  const template = await promisify(fs.readFile, fs)('./templates/email.hbs', 'utf-8');
  const emailHtml = handlebars.compile(template)(options);

  const mailOptions = {
    from: 'WebGames <admin@webgames.com>',
    to: mail,
    subject: options.title,
    html: emailHtml
  };

  return promisify(transporter.sendMail, transporter)(mailOptions);
}

function resetPasswordForm(req, res) {
  const {id, token} = req.params;
  User.findById(id).then(user => {
    if (!user) {
      res.status(404).json({error: 'utilisateur non trouvé... Hack ?'});
      return;
    }

    if (user.u_reset_expiration < Date.now()) {
      res.status(400).json({error: 'Token de réinitialisation de mot de passe expiré'});
      return;
    }

    if (token !== user.u_reset_password_token) {
      res.status(400).json({error: 'Token de réinitialisation de mot de passe invalide'});
      return;
    }

    res.status(200).redirect('/account/forgot/form');
  }).catch(error => {
    res.status(500).json({error});
  });
}

function resetPassword(req, res) {
  const {id, token, password} = req.body;

  User.find({wbere: {u_id: id, u_reset_password_token: token, u_reset_expiration: {$gte: Date.now()}}}).then(user => {
    if (!user) {
      res.status(404).json({error: "Cette e-mail n'appartient à aucun compte utilisateur."});
      return;
    }

    hashPassword(password)
    .then(hash => {
      user.update({
        u_hash: hash
      }).then(rowAffected => {
        res.status(200).json({success: 'mot de passe changé avec succès !'});
      }).catch(error => {
        res.status(500).json({error});
      });
    });
  }).catch(error => {
    res.status(500).json({error});
  });
}

function getAccount(req, res) {
  const {id} = req.query;
  User.findById(id).then(user => {
    res.status(200).json(userJSON(user));
  }).catch(error => {
    res.status(500).json({error});
  });
}

function getCurrentAccount(req, res) {
  const simpleUserJson = {
    username: req.user.username,
    mail: req.user.mail
  }
  res.status(200).json(simpleUserJson);
}

function userJSON(user) {
  return {
    admin: user.u_admin,
    username: user.u_name,
    mail: user.u_email
  }
}

function updateAccount(req, res) {
  User.update(req.body, {where: {u_id: req.user.id}, fields: Object.keys(req.body), returning: true}).spread((rowAffected, update) => {
    // get updated profile
    // could maybe use update value instead search the user in db
    User.findById(req.user.id).then(user => {
      const token = generateJWT(user);
      revokeToken(req.user).then(_ => res.status(200).json({token}));
    }).catch(error => res.status(500).send({error: error.toString()}));
  }).catch(error => res.status(500).send({error: error.toString()}));
}

function revokeToken(user) {
  return new Promise(r => blacklist.revoke(user, r));
}

function destroySession(req) {
  return new Promise(r => req.logout(r))
}

function logout(req, res) {
  Promise.all([
    revokeToken(req.user),
    destroySession(req)
  ]).then(_ => res.status(200).send('disconnected').redirect('/'));
}

function unregister(req, res) {
  User.destroy({where: {u_id: req.user.id}}).then(rowAffected => {
    res.status(200).json({success: 'désinscription faite !'});
  }).catch(error => res.status(500).send({error}));
}

module.exports = {
  register,
  login,
  loginAdmin,
  resetPasswordForm,
  resetPassword,
  getResetToken,
  getAccount,
  getCurrentAccount,
  updateAccount,
  logout,
  unregister
}
