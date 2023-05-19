from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user
import os  
from functools import wraps
from models import Purcell, db, User, login_manager, Menu
from config import secret_key
import mysql




app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://hardinger:ЙфяУвсЙцуЯчсЙысУыя123@localhost/packages'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:QazEdcQweZxcQscEsz123@localhost/packages'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключает отслеживание изменений
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=6)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=6)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/images')
app.config['SECRET_KEY'] = secret_key

app.config.from_object(__name__)

db.init_app(app)

login_manager.init_app(app)
login_manager.login_view = 'login'






@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('login')
        password = request.form.get('psw')

        user = User.query.filter_by(login=login_input).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('მომხმარებელი ამ მონაცემებით არ მოიძებნა', category='error')

    return render_template('login.html')

@app.teardown_request
def teardown_request(exception=None):
    db.session.close()






@app.route('/all', methods=['POST', 'GET'])
@login_required
def all():
    today = datetime.now().date()
    delta = timedelta(days=60)
    date_threshold = today - delta
    all_data = list(reversed(Purcell.query.filter(Purcell.flight >= date_threshold).all()))
    menu = Menu.query.all()
    return render_template('all.html', menu=menu, all_data=all_data)


@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    today = datetime.now().date()
    delta = timedelta(days=90)
    date_threshold = today - delta
    old_data = Purcell.query.filter(Purcell.flight < date_threshold).delete()
    db.session.commit()
    return redirect(url_for('all'))






@app.route('/add', methods=['POST', 'GET'])
@login_required
def add():
    if current_user.role != 'admin':
        flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
        return redirect(url_for('all'))
    
    else:
        last_record = db.session.query(Purcell).order_by(Purcell.id.desc()).first()
        
        if last_record:
                last = int(last_record.number) + 1
                fl = last_record.flight
        else:
            last = 1
            fl = False

        if request.method == 'POST':   

            try:
                add = Purcell(sender = request.form['sender'].upper(),
                            sender_phone = request.form['sender_phone'],
                            recipient = request.form['recipient'].upper(),
                            recipient_phone = request.form['recipient_phone'],
                            inventory = request.form['inventory'].upper(),
                            cost = request.form['cost'].upper(),
                            passport = request.form['passport'].upper(),
                            weight =  request.form['weight'].upper(),
                            responsibility = request.form['responsibility'].upper(),
                            number = int(request.form['number']),
                            city = request.form['city'],
                            flight = request.form['flight'],
                            image = f"static/images/{request.form['number']}-{request.form['flight']}.jpeg")
                file = request.files['photo']
                filename = f"{request.form['number']}-{request.form['flight']}.jpeg"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


                db.session.add(add)
                db.session.commit()
                flash('ამანათი წარმატებით დაემატა', category='success')
                return redirect(url_for('add'))
            except:
                flash('გთხოვთ ჩაწეროთ კორექტული მონაცემები', category='error')
        menu=Menu.query.all()
        return render_template('add.html', menu=menu, last_record=last, fl=fl)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/change', methods=['POST', 'GET'])
@login_required
def change():
    if current_user.role != 'admin':
        flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
        return redirect(url_for('all'))
    else:
    
        if request.method == 'GET':
            flight = request.args.get('flight')
            number = request.args.get('number')

            myrecord = db.session.query(Purcell).filter_by(flight=flight, number=number).first()

        try:

            if request.method == 'POST':
                myrecord = db.session.query(Purcell).filter_by(flight=request.form['flight'], number=int(request.form['number'])).first()
                session = db.session()
                myrecord.sender = request.form['sender']
                myrecord.sender_phone = request.form['sender_phone']
                myrecord.recipient = request.form['recipient']
                myrecord.recipient_phone = request.form['recipient_phone']
                myrecord.inventory = request.form['inventory']
                myrecord.cost = request.form['cost']
                myrecord.passport = request.form['passport']
                myrecord.weight = request.form['weight']
                myrecord.responsibility = request.form['responsibility']
                myrecord.number = int(request.form['number'])
                myrecord.city = request.form['city']
                myrecord.flight = request.form['flight']
                session.commit()
                return redirect(url_for('all'))

        except ValueError:
            flash('ჩაწერეთ კორექტული მონაცემები!', category='error')
        menu=Menu.query.all()
        return render_template('change.html', menu=menu, edit=myrecord)




@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', message='Страница не найдена'), 404



if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', debug=True)

# with app.app_context():
#     db.create_all()