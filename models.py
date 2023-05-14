from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user


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
    



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=True)
    psw = db.Column(db.String(500), nullable=True)

    def check_password(self, password):
        return check_password_hash(self.psw, password)
    


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    url = db.Column(db.String(50), nullable=True)

