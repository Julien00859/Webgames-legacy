function validateRegister(req, res, next) {
  const {username, mail, password} = req.body;
  const mailRegex = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
  const errors = {};

  if (username === '' || username < 3 || username > 24) {
    errors.username = "Le nom d'utilisateur est soit vide / trop court / trop long.";
  }

  if (mail === '' || !(mailRegex.test(username))) {
    errors.mail = "L'e-mail est vide ou n'est pas valide.";
  }

  if (password === '') {
    errors.password = 'Le mot de passe est vide.';
  }

  if (Object.keys(errors).length > 0) {
    return res.status(500).send({errors});
  }
  next();
}

function validateLogin() {
  const {username, password} = req.body;
  const errors = {};

  if (username === '') {
    errors.username = "Le nom d'utilisateur ne peut être vide.";
  }

  if (password === '') {
    errors.password = 'Le mot de passe est vide.';
  }

  if (Object.keys(errors).length > 0) {
    return res.status(500).send({errors});
  }
  next();
}
