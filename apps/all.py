# views.py
from flask import render_template, request, jsonify
from flask.views import MethodView
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from functions import handle_uploaded_image, edit_parcel_, log_error  # Импортируйте необходимые функции
from models import Purcell  # Импортируйте модели

class AllView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def get(self):
        try:
            # Получаем текущую дату
            today = datetime.now().date()
            delta = timedelta(days=60)
            date_threshold = today - delta

            # Получаем данные для отображения, отсортированные по дате и номеру
            all_data = list(reversed(self.db.session.query(Purcell).filter(Purcell.date >= date_threshold)
                             .order_by(Purcell.date.asc(), Purcell.number.asc())
                             .all()))

            # Получаем даты последних 10 рейсов для отображения из уже полученных данных
            last_10_flights = list(set(row.flight for row in all_data))[:10]

            # Отображаем шаблон страницы 'all.html' с данными
            return render_template('all.html', all_data=all_data, last_10_flights=last_10_flights)
        except Exception as e:
            log_error(e)
            return jsonify({'success': False, 'message': 'Ошибка при обработке запроса'}), 500

class RemoveFromListView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def post(self):
        access = ['admin', 'Tbilisi']
        # Проверка прав доступа
        if current_user.role not in access:
            return jsonify({'success': False, 'message': 'თქვენ არ გაქვთ წვდომა'}), 404
        
        # Получаем значение data.id из запроса
        data_id = request.json.get('id')

        # Ищем запись в таблице Purcell по переданному id
        purcell_entry = self.db.session.query(Purcell).get(data_id)

        if purcell_entry:
            # Если запись найдена, удаляем ее
            self.db.session.delete(purcell_entry)
            self.db.session.commit()
            return jsonify({'success': True, 'message': 'ჩანაწერი წაშლილია'}), 200
        else:
            # Если запись не найдена, возвращаем сообщение об ошибке
            return jsonify({'success': False, 'message': f'Запись с id {data_id} не найдена'}), 404

class EditParcelView(MethodView):
    def __init__(self, db, app):
        self.db = db
        self.app = app

    decorators = [login_required]

    def post(self):
        try:
            # Получаем данные из формы
            data = request.form.to_dict()

            # Получаем переданную фотографию, если она есть
            photo = request.files.get('photo')

            # Обработка фотографии, если она была передана
            if photo and photo.filename != '':
                handle_uploaded_image(request.files['photo'], data['id'], self.app)

            edit_parcel_(self.db, data)

            # Возвращаем сообщение об успешной обработке
            return jsonify({'message': 'რედაქტირებამ წარმატებით ჩაიარა', 'success': True}), 200
        except Exception as e:
            return jsonify({'message': f'დაფიქსირდა შეცდომა : {e}', 'success': False}), 400

class EditDeliveryView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def post(self):
        access = ['admin', 'Moscow', 'SPB']
        # Проверка прав доступа
        if current_user.role not in access:
            return jsonify({'message': 'თქვენ არ გაქვთ წვდომა!', 'success': False}), 404
        
        data_id = request.json.get('id')  # Получаем ID из запроса

        # Находим запись в таблице Purcell по переданному ID
        purcell_entry = self.db.session.query(Purcell).get(data_id)

        if purcell_entry:
            # Проверяем, что статус доставки еще не 'yes'
            if purcell_entry.delivery != 'yes':
                # Изменяем статус доставки на 'yes'
                purcell_entry.delivery = 'yes'
                self.db.session.commit()
                return jsonify({'message': 'Посылка вручена', 'success': True}), 200
            else:
                # Если статус доставки уже 'yes', возвращаем ошибку 404
                return jsonify({'message': 'Данная посылка уже вручена!', 'success': False}), 404
        else:
            return jsonify({'message': 'Запись не найдена'}), 404

# Функция для регистрации маршрутов
def register_all_routes(app, db):
    app.add_url_rule('/all', view_func=AllView.as_view('all', db=db))
    app.add_url_rule('/removing_from_the_list', view_func=RemoveFromListView.as_view('removing_from_the_list', db=db))
    app.add_url_rule('/edit_parcel', view_func=EditParcelView.as_view('edit_parcel', db=db, app=app))
    app.add_url_rule('/delivery_status', view_func=EditDeliveryView.as_view('delivery_status', db=db))
