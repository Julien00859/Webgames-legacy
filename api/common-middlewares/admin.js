module.exports = (req, res, next) => {
  if (!req.user) {
    res.status(401).send('you should login !');
    return;
  }

  if (!req.user.admin) {
    res.status(401).send('admin only !');
    return;
  }
  next();
}
