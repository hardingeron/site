from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
from flask_login import login_user
from models import User  # Импорт модели пользователя

class LoginView(MethodView):
    def get(self):
        return render_template('login.html')

    def post(self):
        # Получение данных из формы
        login_input = request.form.get('login')
        password = request.form.get('psw')

        # Поиск пользователя по введенному логину
        user = User.query.filter_by(login=login_input).first()

        # Проверка существования пользователя и совпадения пароля
        if user and user.check_password(password):
            # Если логин и пароль совпадают, авторизуем пользователя
            login_user(user)
            return redirect(url_for('index'))
        else:
            # Если логин или пароль неверные, выводим сообщение об ошибке
            flash('მომხმარებელი არ მოიძებნა', category='error')

        return render_template('login.html')

# Экспортируем маршрут для регистрации
def register_auth_routes(app):
    app.add_url_rule('/login', view_func=LoginView.as_view('login'))
