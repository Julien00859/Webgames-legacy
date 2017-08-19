CREATE TABLE tb_users (
    userid uuid PRIMARY KEY,
    nickname character varying (24) UNIQUE,
    email character varying (254) UNIQUE,
    password bytea NOT NULL,
    is_verified boolean NOT NULL DEFAULT FALSE,
    is_admin boolean NOT NULL DEFAULT FALSE,

    CONSTRAINT chk_nickname CHECK (nickname ~* '^[^@]{4,}$'),
    CONSTRAINT chk_email CHECK (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')
);

CREATE FUNCTION get_user_by_id(uuid) RETURNS tb_users AS $$
    SELECT *
    FROM tb_users
    WHERE userid = $1
$$ LANGUAGE SQL;

CREATE FUNCTION get_user_by_login(character varying (254)) RETURNS tb_users AS $$
    SELECT *
    FROM tb_users
    WHERE nickname = $1 OR email = $1
$$ LANGUAGE SQL;

CREATE FUNCTION create_user(uuid, character varying (24), character varying (254), bytea) RETURNS VOID AS $$
    INSERT INTO tb_users (userid, nickname, email, password) VALUES ($1, $2, $3, $4);
$$ LANGUAGE SQL;

CREATE FUNCTION set_user_verified(uuid) RETURNS VOID AS $$
    UPDATE tb_users SET is_verified = True WHERE userid = $1;
$$ LANGUAGE SQL;

CREATE TABLE tb_games (
    gameid smallserial PRIMARY KEY,
    name character varying (24) UNIQUE,
    player_count integer NOT NULL,
    image character varying (24) UNIQUE,
    ports integer ARRAY NOT NULL
);

CREATE TABLE tb_parties (
    partyid uuid PRIMARY KEY,
    gameid smallserial NOT NULL,

    CONSTRAINT fk_gameid FOREIGN KEY (gameid)
        REFERENCES tb_games(gameid)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE tb_rel_parties_users (
    partyid uuid NOT NULL,
    userid uuid NOT NULL UNIQUE,

    CONSTRAINT pk PRIMARY KEY (partyid, userid),
    CONSTRAINT fk_partyid FOREIGN KEY (partyid)
        REFERENCES tb_parties(partyid)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_userid FOREIGN KEY (userid)
        REFERENCES tb_users
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE FUNCTION create_party(patyid uuid, game_name character varying (24), users_ids uuid ARRAY) RETURNS character (2) AS $$
DECLARE
    uid uuid;
BEGIN
    INSERT INTO tb_parties (partyid, gameid) 
    VALUES (
        partyid,
        (SELECT gameid
        FROM tb_games
        WHERE name = game_name)
    );

    FOREACH uid IN ARRAY user_ids
    LOOP
        INSERT INTO tb_rel_parties_users (partyid, userid)
        VALUES (partyid, uid);
    END LOOP;

    return 'ok';
END;
$$ LANGUAGE plpgsql;
