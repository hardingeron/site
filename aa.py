from flask import Flask
from werkzeug.security import generate_password_hash



password_to_hash = "123"
hashed_password = generate_password_hash(password_to_hash, method='sha256')
print(hashed_password)


