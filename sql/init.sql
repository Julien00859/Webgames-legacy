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
  u_name nickname PRIMARY KEY,
  u_email email NOT NULL UNIQUE,
  u_password char(64) NOT NULL
);

CREATE TABLE tbgames (
  g_name varchar(24) PRIMARY KEY,
  g_enabled boolean NOT NULL DEFAULT TRUE
);

CREATE TABLE tbscores (
  u_name nickname,
  g_name varchar(24),
  play_count signedint NOT NULL,
  play_time interval SECOND NOT NULL,
  win_count signedint NULL,

  CONSTRAINT pk PRIMARY KEY (u_name, g_name),
  CONSTRAINT fk_user_name FOREIGN KEY (u_name)
    REFERENCES tbusers
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_game_name FOREIGN KEY (g_name)
    REFERENCES tbgames
    ON UPDATE CASCADE
    ON DELETE CASCADE
);
