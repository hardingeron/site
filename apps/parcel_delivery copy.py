import json
from flask.views import MethodView
from flask import request, render_template, jsonify, send_file
from openpyxl import load_workbook
from flask_login import login_required
from models import Forms, ParcelIssuance  # Импортируем модель для работы с БД
from sqlalchemy import func
from io import BytesIO
from openpyxl.styles import Font, Alignment, Border, Side

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
        Обрабатывает POST-запросы как для основного запроса, так и для поиска.
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
                print(f'sssssssssssssss {matched_record.passport}')
                if matched_record:
                    result.append({
                        'tracking': key,
                        'recipient': matched_record.recipient_fio,
                        'weight': values[7],
                        'date': values[3],
                        'issued': values[0] == 'გასატანი',  # Условие "выдана"
                        'passport': matched_record.passport
                    })

        return jsonify(result)  # Возвращаем список записей

    def find_matching_record_in_db(self, recipient_fio):
        """
        Ищет запись в базе данных, сравнивая recipient_fio без пробелов.
        Возвращает оригинальное значение recipient_fio, если совпадает.
        """
        try:
            # Удаляем все пробелы из имени в запросе
            recipient_fio_no_spaces = recipient_fio.replace(' ', '')

            # Ищем первую запись, которая соответствует условию
            matched_record = Forms.query.filter(
                func.replace(Forms.recipient_fio, ' ', '') == recipient_fio_no_spaces
            ).order_by(Forms.id.desc()).first()

            # Если запись не найдена, возвращаем None
            if matched_record is None:
                return None

            return matched_record  # Возвращаем найденную запись

        except Exception as e:
            # Логируем ошибку или возвращаем None в случае сбоя
            print(f"Ошибка при поиске записи: {e}")
            return None
        

class DownloadForRs(MethodView):
    decorators = [login_required]

    def __init__(self):
        super().__init__()

    def post(self):
        try:
            # Получаем все записи из базы данных
            parcel_data = ParcelIssuance.query.all()

            # Загружаем шаблон Excel файла
            workbook = load_workbook('documents/templ_6.xls')
            sheet = workbook.active

            start_row = 2  # Начинаем с второй строки
            col_letters = ['A', 'B', 'C', 'D', 'E']

            # Устанавливаем стиль шрифта по умолчанию с размером 10
            font = Font(size=10)
            alignment = Alignment(horizontal='center', vertical='center')
            thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

            # Заполняем данные
            for row_idx, data in enumerate(parcel_data, start=start_row):
                # Заполняем столбцы
                # Столбец A: tracking_number
                sheet[f'A{row_idx}'] = data.tracking_number

                # Столбец B: passport
                sheet[f'B{row_idx}'] = data.passport

                # Столбцы C и D: разделяем имя и фамилию
                recipient_split = data.recipient.split()
                if len(recipient_split) >= 2:
                    # Имя и фамилия
                    sheet[f'C{row_idx}'] = recipient_split[0]  # Имя
                    sheet[f'D{row_idx}'] = recipient_split[-1]  # Фамилия
                else:
                    sheet[f'C{row_idx}'] = data.recipient  # Если только одно слово в recipient
                    sheet[f'D{row_idx}'] = ""

                # Столбец E: is_resident (меняем 0 на 1 и 1 на 0)
                sheet[f'E{row_idx}'] = 1 if data.is_resident == 0 else 0

                # Применяем стиль
                for col_letter in col_letters:
                    cell = sheet[f'{col_letter}{row_idx}']
                    cell.font = font
                    cell.alignment = alignment
                    cell.border = thin_border

            # Сохраняем файл в оперативной памяти
            output = BytesIO()
            workbook.save(output)
            workbook.close()
            output.seek(0)

            # Отправляем файл обратно пользователю
            return send_file(output, as_attachment=True, download_name='parcel_data.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        except Exception as e:
            # В случае ошибки возвращаем сообщение
            return jsonify({'error': str(e)}), 500

        

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
