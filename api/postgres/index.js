const sequelize = require('sequelize');
const dburl = process.env.DBURL;
const db = new sequelize(dburl);

module.exports = db;
