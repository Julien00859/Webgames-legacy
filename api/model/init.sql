DROP TABLE IF EXISTS tbscores;
DROP TABLE IF EXISTS tbusers;
DROP TABLE IF EXISTS tbgames;
DROP DOMAIN IF EXISTS signedint;
DROP DOMAIN IF EXISTS nickname;
DROP DOMAIN IF EXISTS email;

CREATE DOMAIN signedint AS int CHECK (VALUE >= 0);
CREATE DOMAIN nickname AS varchar(24) CHECK (VALUE ~ '^[[:graph:] ]{3,24}$');
CREATE DOMAIN email AS varchar(254) CHECK (VALUE ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');

CREATE TABLE tbusers (
  u_id serial PRIMARY KEY,
  u_name nickname NOT NULL UNIQUE,
  u_email email NOT NULL UNIQUE,
  u_hash char(64) NOT NULL,
  u_reset_password_token char(64) NULL,
  u_reset_password_expiration datetime NULL
);

CREATE TABLE tbgames (
  g_name varchar(24) PRIMARY KEY,
  g_enabled boolean NOT NULL DEFAULT TRUE,
  directory varchar,
  executable varchar,
  tcpPortCount tinyint,
  udpPortCount tinyint
);
