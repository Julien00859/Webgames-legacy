const sequelize = require('sequelize');
const db = new sequelize(process.env.DB_NAME, process.env.DB_USER, process.env.DB_SECRET, {
  host: process.env.DB_HOST,
  dialect: 'postgres',
  logging: false
});

module.exports = db;
