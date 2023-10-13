from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash



# Генерация хеша пароля
password = "ViPost_QazEdcQweZxcQscEsz123"  # Замените это на пароль пользователя
hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

# Вывод хеша пароля
print("Хеш пароля:", hashed_password)

