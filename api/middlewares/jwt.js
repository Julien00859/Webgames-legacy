const jwt = requirer('express-jwt');

module.exports = jwt({secret: process.env.SECRET});
