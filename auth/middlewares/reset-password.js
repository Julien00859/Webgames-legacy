function resetPasswordMiddleware(req, res, next) {
  const {id, token} = req.query;
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

    next();
  }).catch(error => {
    res.status(500).json({error});
  });
}

module.exports = resetPasswordMiddleware;
