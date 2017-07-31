module.exports = (req, res, next) => {
  //console.log(req);
  if (!req.user) {
    console.log('no user');
    res.status(401).send('you should login !');
    return;
  }

  if (!req.user.admin && !req.user.type === 'manager') {
    console.log('admin or manager only !!');
    res.status(401).send('admin or manager only !');
    return;
  }
  console.log('admin or manager. You have access.');
  next();
}
