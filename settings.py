from os import environ

WGHOST = environ.get("WGHOST", "127.0.0.1")
WGPORT = int(environ.get("WGPORT", 80))

# Leave default value empty that ayncpg can manage them
PGHOST = environ.get("PGHOST", None)
PGPORT = environ.get("PGPORT", None)
PGUSER = environ.get("PGUSER", None)
PGDATABASE = environ.get("PGDATBASE", "webgames")
PGPASSWORD = environ.get("PGPASSWORD", None)

LOGLEVEL = environ.get("WGLOGLEVEL", "WARNING")
TOKENLENGTH = environ.get("WGTOKENLENGTH", None)
TOKENVALIDITY = environ.get("WGTOKENVALIDITY", "1d")
PWDSALT = environ.get("WGPWDSALT", "super_secret_key").encode()
