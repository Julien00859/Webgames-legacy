function parseBool(data) {
  if (typeof data === "boolean")
    return data;
  if (typeof data !== "string")
    return false;
  return ["yes", "y", "true", "1"].includes(data.toLowerCase().trim());
}

// Web API default configuration
const API_PORT = parseInt(process.env.API_PORT || 5000);
const NODE_ENV = process.env.NODE_ENV || "development";
const JWT_SECRET = process.env.JWT_SECRET; // Must be set in environ
const USE_SSL = parseBool(process.env.USE_SSL || false);

// Postgress access default configuration
const POSTGRES_HOST = process.env.POSTGRES_HOST || "localhost";
const POSTGRES_USER = process.env.POSTGRES_USER || "webgames";
const POSTGRES_DB = process.env.POSTGRES_DB || "webgames";
const POSTGRES_PASSWORD = process.env.POSTGRES_PASSWORD; // Must be set in environ

// Redis access default configuration
const REDIS_HOST = process.env.REDIS_HOST || "localhost";
const REDIS_PORT = parseInt(process.env.REDIS_PORT || 6379);
const REDIS_DB_API = parseInt(process.env.REDIS_DB_API || 1);
const REDIS_PASSWORD = process.env.REDIS_PASSWORD; // Must be set in environ

// Mail access default configuration
const MAIL_HOST = process.env.MAIL_HOST || "localhost";
const MAIL_PORT = parseInt(process.env.MAIL_PORT || (USE_SSL ? 465 : 1025));
const MAIL_USE_AUTH = parseBool(process.env.MAIL_USE_AUTH || false);
const MAIL_USER = process.env.MAIL_USER || "webgames";
const MAIL_PASSWORD = process.env.MAIL_PASSWORD; // Must be set in environ

// Queue Manager access default configuration
const MANAGER_HOST = process.env.MANAGER_HOST || "localhost";
const MANAGER_TCP_PORT = parseInt(process.env.MANAGER_TCP_PORT || 4170);

module.exports = {
  API_PORT,
  USE_SSL,
  JWT_SECRET,
  NODE_ENV,
  POSTGRES_HOST,
  POSTGRES_USER,
  POSTGRES_DB,
  POSTGRES_PASSWORD,
  REDIS_HOST,
  REDIS_PORT,
  REDIS_DB_API,
  REDIS_PASSWORD,
  MAIL_HOST,
  MAIL_PORT,
  MAIL_USER_AUTH,
  MAIL_USER,
  MAIL_PASSWORD,
  MANAGER_HOST,
  MANAGER_TCP_PORT
}
