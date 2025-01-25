import json
from flask.views import MethodView
from flask import request, render_template, jsonify
from flask_login import login_required
from models import Forms  # Импортируем модель для работы с БД
from sqlalchemy import func

class ParcelDelivery(MethodView):
    decorators = [login_required]

    def __init__(self):
        super().__init__()

    def get(self):
        """
        Отображает страницу с таблицей для посылок.
        """
        return render_template('parcel_delivery.html')

    def post(self):
        """
        Обрабатывает POST-запрос для поиска данных (это основной метод для '/ParcelDelivery').
        """
        # Получаем JSON с фронтенда
        data = request.json
        recipient_key = data.get('recipient')

        if not recipient_key:
            return jsonify([])  # Пустой список, если ключ не задан

        # Загружаем JSON-файл
        try:
            with open('expertise_data.json', 'r', encoding='utf-8') as file:
                all_data = json.load(file)
        except FileNotFoundError:
            return jsonify({'error': 'Файл данных не найден'}), 500
        except json.JSONDecodeError:
            return jsonify({'error': 'Ошибка в формате JSON'}), 500

        # Проверяем наличие ключа
        if recipient_key not in all_data:
            return jsonify([])  # Пустой список, если ключ не найден

        # Получаем имя и дату из ключа
        recipient_name = all_data[recipient_key][5]
        date = all_data[recipient_key][3]

        # Ищем записи, которые соответствуют имени и дате
        result = []
        for key, values in all_data.items():
            if values[5] == recipient_name and values[3] == date:
                # Проверяем базу данных на соответствие
                matched_record = self.find_matching_record_in_db(values[5])
                if matched_record:
                    result.append({
                        'tracking': key,
                        'recipient': matched_record.recipient_fio,
                        'weight': values[7],
                        'date': values[3],
                        'issued': values[0] == 'გასატანი'  # Условие "выдана"
                    })

        return jsonify(result)  # Возвращаем список записей

    def search(self):
        """
        Обрабатывает POST-запрос для поиска данных на /search.
        """
        # Получаем JSON с фронтенда
        data = request.json
        recipient_key = data.get('recipient')

        if not recipient_key:
            return jsonify([])  # Пустой список, если ключ не задан

        # Загружаем JSON-файл
        try:
            with open('expertise_data.json', 'r', encoding='utf-8') as file:
                all_data = json.load(file)
        except FileNotFoundError:
            return jsonify({'error': 'Файл данных не найден'}), 500
        except json.JSONDecodeError:
            return jsonify({'error': 'Ошибка в формате JSON'}), 500

        # Проверяем наличие ключа
        if recipient_key not in all_data:
            return jsonify([])  # Пустой список, если ключ не найден

        # Получаем имя и дату из ключа
        recipient_name = all_data[recipient_key][5]
        date = all_data[recipient_key][3]

        # Ищем записи, которые соответствуют имени и дате
        result = []
        for key, values in all_data.items():
            if values[5] == recipient_name and values[3] == date:
                matched_record = self.find_matching_record_in_db(values[5])
                if matched_record:
                    result.append({
                        'tracking': key,
                        'recipient': matched_record.recipient_fio,
                        'weight': values[7],
                        'date': values[3],
                        'issued': values[0] == 'გასატანი'  # Условие "выдана"
                    })

        return jsonify(result)  # Возвращаем список записей

    def find_matching_record_in_db(self, recipient_fio):
        """
        Ищет запись в базе данных, сравнивая recipient_fio без пробелов.
        Возвращает оригинальное значение recipient_fio, если совпадает.
        """
        # Удаляем все пробелы из имени в запросе
        recipient_fio_no_spaces = recipient_fio.replace(' ', '')

        # Ищем первую запись, которая соответствует условию
        matched_record = Forms.query.filter(
            func.replace(Forms.recipient_fio, ' ', '') == recipient_fio_no_spaces
        ).order_by(Forms.id.desc()).first()

        return matched_record  # Возвращаем найденную запись или None, если не нашли совпадений

        

def register_parcel_delivery_routes(app, db):
    """
    Регистрирует маршруты для класса ParcelDelivery.
    """
    app.add_url_rule(
        '/ParcelDelivery',
        view_func=ParcelDelivery.as_view('ParcelDelivery')
    )

    # Регистрируем маршрут для поиска
    app.add_url_rule('/search', view_func=ParcelDelivery.as_view('search'), methods=['POST'])
