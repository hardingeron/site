from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user
import mysql
import uuid
import random

db = SQLAlchemy()

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Purcell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=True)
    sender_phone = db.Column(db.String(50), nullable=True)
    recipient = db.Column(db.String(50), nullable=True)
    recipient_phone = db.Column(db.String(50), nullable=True)
    inventory = db.Column(db.String(200), nullable=True)
    cost = db.Column(db.String(50), nullable=True)
    passport = db.Column(db.String(50), nullable=True)
    weight = db.Column(db.String(50), nullable=True)
    responsibility = db.Column(db.String(50), nullable=True)
    number = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    flight = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(100))
    where_from = db.Column(db.String(20), nullable=True)
    departure_status = db.Column(db.String(10), nullable=True)
    delivery = db.Column(db.String(3), default='no')

class Temporarylink(db.Model):
    __tablename__ = 'Temporarylink'  # Используй именно то имя, что в БД\

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def is_expired(self):
        return datetime.utcnow() > self.created_at + timedelta(minutes=30)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=True)
    psw = db.Column(db.String(500), nullable=True)
    role = db.Column(db.String(20), nullable=True)


    def check_password(self, password):
        return check_password_hash(self.psw, password)
    


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    url = db.Column(db.String(50), nullable=True)



class Storage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shelf = db.Column(db.String(50))
    trecing = db.Column(db.String(20))
    date = db.Column(db.Date, default=datetime.now().date())


class Expertise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='not completed', nullable=False)
    recipient = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.String(10), nullable=False)
    Number = db.Column(db.String(10), nullable=False)
    tracking = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.String(50), nullable=True)
    date = db.Column(db.Date, nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.Date)
    position = db.Column(db.Integer)
    flname = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    pasport = db.Column(db.String(20))
    comment = db.Column(db.String(250))
    payment = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    fwc = db.Column(db.String(20))
    destination = db.Column(db.String(50))
    action = db.Column(db.String(20))
    date_of_birth = db.Column(db.String(20))

class Temporaryparcel(db.Model):
    __tablename__ = 'Temporaryparcel'  # <- Обязательно укажи так, как в БД

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(8), unique=True, nullable=False)  # Уникальный номер посылки
    sender_first_name = db.Column(db.String(100), nullable=False)
    sender_last_name = db.Column(db.String(100), nullable=False)
    sender_phone = db.Column(db.String(20), nullable=False)
    sender_passport = db.Column(db.String(50), nullable=False)

    recipient_first_name = db.Column(db.String(100), nullable=False)
    recipient_last_name = db.Column(db.String(100), nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    recipient_passport = db.Column(db.String(50), nullable=False)

    city = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    invoice_path = db.Column(db.String(255), nullable=False)  # путь к PDF
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tracking_number = self.generate_unique_number()

    @staticmethod
    def generate_unique_number():
        while True:
            number = str(random.randint(10000000, 99999999))
            if not Temporaryparcel.query.filter_by(tracking_number=number).first():
                return number






class Forms(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.String(20))
    number = db.Column(db.Integer)
    sender_fio = db.Column(db.String(50))
    sender_phone = db.Column(db.String(15))
    recipient_fio = db.Column(db.String(50))
    recipient_phone = db.Column(db.String(15))
    passport = db.Column(db.String(20))
    sender_passport = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(20))
    comment = db.Column(db.Text)
    price = db.Column(db.Integer)
    weights = db.Column(db.String(100))
    cost = db.Column(db.Integer)
    payment_status = db.Column(db.String(20))
    currency = db.Column(db.String(5))
    where_from = db.Column(db.String(30))
    added_to_the_manifest = db.Column(db.String(10), default='no')
    address = db.Column(db.Text(300))
    company_comment = db.Column(db.Text, nullable=True)
    pdf_adress = db.Column(db.String(255), nullable=True)




class ParcelIssuance(db.Model):
    __tablename__ = 'ParcelIssuance'  # Указываем имя таблицы явно
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracking_number = db.Column(db.String(20), nullable=False)
    recipient = db.Column(db.String(100), nullable=False)
    passport = db.Column(db.String(50), nullable=False)
    is_resident = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)




# Стол для отправлении из России 
class Shipments(db.Model):
    __tablename__ = "Shipments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # добавим id для ключа
    city_from = db.Column(db.String(15))          # Город отправления
    sender_name = db.Column(db.String(50))       # Имя отправителя
    sender_surname = db.Column(db.String(50))    # Фамилия отправителя
    sender_number = db.Column(db.String(15))     # Номер отправителя
    recipient_name = db.Column(db.String(50))    # Имя получателя
    recipient_surname = db.Column(db.String(50)) # Фамилия получателя
    recipient_number = db.Column(db.String(15))  # Номер получателя
    recipient_passport = db.Column(db.String(50))# Паспорт получателя
    parcels_count = db.Column(db.Integer)        # Количество посылок
    address = db.Column(db.String(100))          # Адрес
    weights = db.Column(db.String(200))          # Веса
    city_to = db.Column(db.String(50))           # Город получения
    payment_status = db.Column(db.String(5))     # Статус оплаты
    cargo_cost = db.Column(db.String(15))        # Стоимость груза
    description = db.Column(db.String(1000))     # Опись
    shipment_number = db.Column(db.Integer)      # Номер посылки
    order_date = db.Column(db.DateTime)              # Дата оформления
    send_date = db.Column(db.Date)               # Дата отправки
    currency = db.Column(db.String(5))           # Валюта оплаты
    payment_amount = db.Column(db.Integer)       # Оплата
    sequence = db.Column(db.Integer)             # Очерёдность