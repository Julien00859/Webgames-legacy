module.exports = (req, res, next) => {
  //console.log(req);
  if (!req.user) {
    res.status(401).send('you should login !');
    return;
  }

  if (!req.user.admin && !req.user.type === 'manager') {
    res.status(401).send('admin or manager only !');
    return;
  }
  next();
}
