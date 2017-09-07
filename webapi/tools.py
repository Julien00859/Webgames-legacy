#!./venv/bin/python

import bcrypt
from uuid import uuid4
from getpass import getpass

print("UUID:", uuid4())
print("PWD Hash:", bcrypt.hashpw(getpass().encode(), bcrypt.gensalt()))