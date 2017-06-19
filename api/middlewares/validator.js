function validateRegister(req, res, next) {
  req.checkBody('username', "Le nom d'utilisateur est vide").notEmpty();
  req.checkBody('username', "Le nom d'utilisateur doit être compris entre 3 et 24 caractères").len(3, 24);
  req.checkBody('mail', "L'e-mail est vide ou n'est pas valide.").notEmpty();
  req.checkBody('mail', "L'e-mail n'est pas valide (example@example.com).").isEmail();
  req.checkBody('password', 'Le mot de passe est vide / trop court / trop long.').notEmpty()
  req.checkBody('password', 'Le mot de passe doit être compris entre 8 et 72 caractères').len(8, 72);

  const errors = req.validationErrors();
  if (errors) {
    return res.status(500).json({error: errors.map(err => err.msg)});
  }

  next();
}

function validateLogin(req, res, next) {
  req.checkBody('username', "Le nom d'utilisateur est vide").notEmpty();
  req.checkBody('username', "Le nom d'utilisateur doit être compris entre 3 et 24 caractères").len(3, 24);
  req.checkBody('password', 'Le mot de passe est vide / trop court / trop long.').notEmpty()
  req.checkBody('password', 'Le mot de passe doit être compris entre 8 et 72 caractères').len(8, 72);

  const errors = req.validationErrors();
  if (errors) {
    return res.status(500).json({error: errors.map(err => err.msg)});
  }

  next();
}

module.exports = {
  validateRegister,
  validateLogin
}
