const pgp = require('pg-promise');
const dburl = process.env.DBURL;
const db = pgp(dburl);

module.exports = db;
