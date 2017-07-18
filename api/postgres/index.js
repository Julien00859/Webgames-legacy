const sequelize = require('sequelize');
const dburl = process.env.DBURL;
const db = new sequelize(dburl, {logging: false});

module.exports = db;
