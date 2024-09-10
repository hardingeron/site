from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import timedelta
from flask_login import login_required, logout_user, current_user
import os 
from models import db, login_manager
from config import secret_key, db_url_key
from functions import get_reservation_data
from apps.auth import register_auth_routes  # Импорт маршрутов авторизации
from apps.views import register_index_routes  # Импортируйте функцию регистрации маршрутов
from apps.all import register_all_routes
from apps.documents import register_documents_routes
from apps.add import register_add_routes
from apps.storage import register_storage_routes
from apps.image_list import register_image_routes
from apps.reservation import register_reservation_routes
from apps.list import register_list_routes
from apps.list_edit import register_list_edit_routes
from apps.expertise import register_expertise_routes

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = db_url_key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключает отслеживание изменений
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=8)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/purcells')
app.config['SECRET_KEY'] = secret_key

app.config.from_object(__name__)

db.init_app(app)

login_manager.init_app(app)
login_manager.login_view = 'login'



#-------------------------------------------------------------------------------------------------#
# ------------------------------               /login               ------------------------------#
register_auth_routes(app)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /index               ------------------------------#
register_index_routes(app, db, app.config['UPLOAD_FOLDER'])
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /all                 ------------------------------#
register_all_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /documents           ------------------------------#
register_documents_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /add                 ------------------------------#
register_add_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /storage             ------------------------------#
register_storage_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /images_list         ------------------------------#
register_image_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /reservation         ------------------------------#
register_reservation_routes(app, db)



@app.route('/reservation_big', methods=['POST', 'GET'])
@login_required
def reservation_big():
    access = ['admin', 'Tbilisi', 'Moscow']
    if current_user.role not in access:
        flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
        return redirect(url_for('index'))
    selected_date = request.args.get('date')
    reis = request.args.get('route')
    reservation_data = get_reservation_data(selected_date, reis, 59)
    return render_template('reservation_big.html', **reservation_data)


#-------------------------------------------------------------------------------------------------#
# ------------------------------               /list                ------------------------------#
register_list_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /list_edit           ------------------------------#
register_list_edit_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /expertise           ------------------------------#
register_expertise_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               other                ------------------------------#
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# @app.teardown_request
# def teardown_request(exception=None):
#     db.session.close()


@app.teardown_request
def teardown_request(exception=None):
    db.session.remove()

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', message='Страница не найдена'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message='Внутренняя ошибка сервера'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



