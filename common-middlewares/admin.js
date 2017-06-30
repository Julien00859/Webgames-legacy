module.exports = (req, res, next) => {
  if (!req.user.admin) {
    res.status(401).send('admin only !');
    return;
  }
  next();
}
