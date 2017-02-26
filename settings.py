from os import environ

WGSSL = bool(environ.get("WGSSL", False))
WGHOST = environ.get("WGHOST", "127.0.0.1")
WGPORT = int(environ.get("WGPORT", 443 if WGSSL else 80))

# Leave default value empty that ayncpg can manage them
PGHOST = environ.get("PGHOST", None)
PGPORT = environ.get("PGPORT", None)
PGUSER = environ.get("PGUSER", None)
PGDATABASE = environ.get("PGDATBASE", "webgames")
PGPASSWORD = environ.get("PGPASSWORD", None)

LOGLEVEL = environ.get("WGLOGLEVEL", "DEBUG")
TOKENLENGTH = environ.get("WGTOKENLENGTH", 16)
PWDSALT = environ.get("WGPWDSALT", "super_secret_key").encode()
