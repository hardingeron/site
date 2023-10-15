from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user
import mysql


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
    weight =  db.Column(db.String(50), nullable=True)
    responsibility = db.Column(db.String(50), nullable=True)
    number = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    flight = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(100))
    where_from = db.Column(db.String(20), nullable=True)
    



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


class Messages(db.Model):
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text)
    timestamp = db.Column(db.TIMESTAMP, server_default='CURRENT_TIMESTAMP')



class Forms(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.String(20))
    number = db.Column(db.Integer)
    sender_fio = db.Column(db.String(50))
    sender_phone = db.Column(db.String(15))
    recipient_fio = db.Column(db.String(50))
    recipient_phone = db.Column(db.String(15))
    passport = db.Column(db.String(20))
    city = db.Column(db.String(20))
    comment = db.Column(db.Text)
    price = db.Column(db.Integer)
    weights = db.Column(db.String(100))
    cost = db.Column(db.Integer)
    payment_status = db.Column(db.String(20))
    currency = db.Column(db.String(5))
    where_from = db.Column(db.String(30))