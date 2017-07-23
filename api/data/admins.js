const bcrypt = require('bcrypt');

const admins = [
  {u_admin: true, u_name: 'Mathieu', u_email: 'math7745@hotmail.fr', u_hash: bcrypt.hashSync('abricot2000', 10)},
  {u_admin: true, u_name: 'Julien', u_email: 'julien.castiaux@gmail.com', u_hash: bcrypt.hashSync('pommepoire', 10)}
];

module.exports = admins;
