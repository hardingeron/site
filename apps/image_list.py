

from flask import render_template, request, jsonify
from flask.views import MethodView
from flask_login import login_required
from datetime import datetime, timedelta
from models import Purcell


# Класс для отображения списка посылок с изображениями
class ParcelPicturesList(MethodView):
    def __init__(self, db, app):
        self.db = db
        self.app = app

    decorators = [login_required]

    def post(self):
        start_date = request.form['startDate']
        end_date = datetime.strptime(request.form['endDate'], '%Y-%m-%d')
        end_date += timedelta(days=1)
        city = request.form.get('images_city')

        # Запрос к базе данных для выбора записей в заданном диапазоне дат
        purcells = Purcell.query.filter(Purcell.date.between(start_date, end_date), Purcell.delivery == 'no', Purcell.city == city).all()

        return render_template('images_list.html', purcells=purcells, start_date=start_date, end_date=end_date)

# Класс для обновления статуса доставки посылки
class UpdateDeliveryStatus(MethodView):
    def __init__(self, db, app):
        self.db = db
        self.app = app

    decorators = [login_required]

    def post(self):
        data_id = request.json.get('id')
        purcell_entry = Purcell.query.get(data_id)

        if purcell_entry:
            if purcell_entry.delivery == 'yes':
                return jsonify({'message': 'ამანათი უკვე გაცემული იყო!', 'success': False}), 400

            purcell_entry.delivery = 'yes'
            self.db.session.commit()
            return jsonify({'message': 'ამანათი გაცემულია', 'success': True}), 200
        else:
            return jsonify({'message': 'ამანათი არ მოიძებნა', 'success': False}), 400

# Функция для регистрации маршрутов
def register_image_routes(app, db):
    app.add_url_rule('/images_list', view_func=ParcelPicturesList.as_view('parcel_pictures_list', db=db, app=app))
    app.add_url_rule('/images_list_delivery_status', view_func=UpdateDeliveryStatus.as_view('images_list_delivery_status', db=db, app=app))
