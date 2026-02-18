import json
from flask.views import MethodView
from flask import request, render_template, jsonify, send_file
from openpyxl import load_workbook
from flask_login import login_required
from models import Forms, ParcelIssuance, Storage  # Импортируем модель для работы с БД
from sqlalchemy import func
from io import BytesIO
from openpyxl.styles import Font, Alignment, Border, Side
from datetime import datetime
import os
import asyncio
from bot import send_location_message
from .storage import loop

class ParcelSearch(MethodView):
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
        Обрабатывает POST-запросы для поиска посылок.
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
            return jsonify({'error': 'ამანათი მითითებული თრექინგით არ მოიძებნა'}), 404  # Уведомление, если ключ не найден

        # Получаем имя и дату из ключа
        recipient_name = all_data[recipient_key][5]
        date = all_data[recipient_key][3]

        # Ищем записи, которые соответствуют имени и дате
        result = []
        today = datetime.today()

        for key, values in all_data.items():
            if values[1] != "დაუბეგრავი":
                continue  # Пропускаем посылку, если она не в нужном состоянии

            if values[1] == "დაუბეგრავი" and values[5] == recipient_name and values[3] == date:
                matched_record = self.find_matching_record_in_db(values[5])
                if matched_record:
                    # Проверяем, существует ли посылка с таким tracking_number в базе данных
                    tracking_number = key
                    is_issued = self.check_if_issued(tracking_number)

                    # Вычисляем разницу в днях между сегодняшним днём и датой посылки
                    try:
                        parcel_date = datetime.strptime(values[3], "%d.%m.%Y")  # Пример: "18.08.2024"
                        days_difference = (today - parcel_date).days  # Разница в днях
                    except ValueError:
                        days_difference = None  # Если формат даты неверный

                    result.append({
                        'tracking': tracking_number,
                        'recipient': matched_record.recipient_fio,
                        'weight': values[7],
                        'date': values[3],
                        'days_ago': days_difference,  # Добавляем разницу в днях
                        'issued': is_issued,
                        'passport': matched_record.passport
                    })

        # Если не нашли ни одной посылки с состоянием "დაუბეგრავი"
        if not result:
            return jsonify({'error': 'ამანათი ყვითელშია ან ექვემდებარება გამბაჟებას!'}), 404

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

    def check_if_issued(self, tracking_number):
        """
        Проверяет, существует ли запись с указанным tracking_number в базе данных.
        Если такая запись найдена, считается, что посылка "выдана".
        """
        try:
            # Ищем запись с таким tracking_number
            parcel_record = ParcelIssuance.query.filter_by(tracking_number=tracking_number).first()

            # Если запись найдена, то посылка "выдана"
            if parcel_record:
                return True  # Посылка выдана
            else:
                return False  # Посылка не выдана

        except Exception as e:
            # Логируем ошибку или возвращаем False в случае сбоя
            print(f"Ошибка при проверке статуса посылки: {e}")
            return False



class ParcelProcessing(MethodView):
    decorators = [login_required]

    def __init__(self, db):
        super().__init__()
        self.db = db

    def post(self):
        """
        Обрабатывает POST-запрос для получения данных, сохранения их в базе данных
        и отправки местоположения через Telegram-бота.
        """
        try:
            data = request.json  # Получаем данные из запроса

            # Выводим полученные данные для отладки
            print("Полученные данные:", json.dumps(data, indent=4, ensure_ascii=False))

            # Проходим по всем записям и проверяем наличие по трекинг-номеру
            for record in data.get('records', []):
                tracking_number = record['tracking']
                recipient = record['recipient']
                is_resident = data.get('citizenship', False)
                passport = data.get('passport', '')

                # Проверяем, существует ли запись с таким tracking_number
                existing_record = ParcelIssuance.query.filter_by(tracking_number=tracking_number).first()

                if existing_record:
                    # Если запись уже существует, пропускаем её
                    print(f"Запись с tracking_number {tracking_number} уже существует.")
                    continue

                # Если записи с таким трекингом нет, создаем новую запись
                
                storage = Storage.query.filter_by(trecing=tracking_number).first()
                if storage:
                    location = storage.shelf  # Получаем местоположение (полку)
                    info = recipient  # Информация для отправки
                    date = storage.date  # Дата хранения

                    # Отправляем сообщение через Telegram-бота
                    asyncio.run_coroutine_threadsafe(send_location_message(tracking_number, location, info, date), loop)

                    # Удаляем запись из Storage
                    self.db.session.delete(storage)
                else:
                    # Если записи в Storage нет, отправляем уведомление с дефолтными значениями
                    asyncio.run_coroutine_threadsafe(send_location_message(tracking_number, '!', '!', '!'), loop)

                # Создаем новую запись в ParcelIssuance
                new_record = ParcelIssuance(
                    tracking_number=tracking_number,
                    recipient=recipient,
                    passport=passport,
                    is_resident=is_resident,
                    created_at=datetime.utcnow()  # Устанавливаем текущую дату и время
                )

                # Добавляем новую запись в сессию
                self.db.session.add(new_record)

            # Сохраняем все изменения в базе данных одним коммитом
            self.db.session.commit()

            return jsonify({'success': True})

        except Exception as e:
            print(f"Ошибка при обработке данных: {e}")
            self.db.session.rollback()  # Откатываем транзакцию в случае ошибки
            return jsonify({'error': 'Ошибка при обработке данных'}), 500

class DownloadForRs(MethodView):
    decorators = [login_required]  # Убедитесь, что пользователь авторизован

    def __init__(self):
        super().__init__()
    
    def post(self):
        try:
            
            # Получаем все записи из базы данных
            parcel_data = ParcelIssuance.query.all()

            # Загружаем шаблон Excel файла
            workbook = load_workbook('documents/ForRsToLoad.xlsx')
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
                sheet[f'A{row_idx}'] = data.tracking_number
                sheet[f'B{row_idx}'] = data.passport

                # Столбцы C и D: разделяем имя и фамилию
                recipient_split = data.recipient.split()
                if len(recipient_split) >= 2:
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
        

class ParcelSearchByName(MethodView):
    decorators = [login_required]  # Убедитесь, что пользователь авторизован

    def __init__(self):
        super().__init__()

    def post(self):
        data = request.json
        full_name_key = data.get('fullName')

        if not full_name_key:
            return jsonify([])

        try:
            with open('expertise_data.json', 'r', encoding='utf-8') as file:
                all_data = json.load(file)
        except FileNotFoundError:
            return jsonify({'error': 'Файл данных не найден'}), 500
        except json.JSONDecodeError:
            return jsonify({'error': 'Ошибка в формате JSON'}), 500

        result = []
        today = datetime.today()

        for key, values in all_data.items():
            if values[1] != "დაუბეგრავი":  
                continue  
            full_name_key = full_name_key.replace(' ', '')  # Убираем все пробелы
            if values[5] == full_name_key:  
                matched_record = self.find_matching_record_in_db(values[5])
                if matched_record:
                    tracking_number = key
                    is_issued = self.check_if_issued(tracking_number)

                    # Парсим дату из JSON
                    try:
                        parcel_date = datetime.strptime(values[3], "%d.%m.%Y")  # Формат: "18.08.2024"
                        days_difference = (today - parcel_date).days  # Разница в днях
                    except ValueError:
                        days_difference = None  # Если формат даты неверный

                    result.append({
                        'tracking': tracking_number,
                        'recipient': matched_record.recipient_fio,
                        'weight': values[7],
                        'date': values[3],
                        'days_ago': days_difference,  # Добавляем разницу в днях
                        'issued': is_issued,
                        'passport': matched_record.passport
                    })

        if not result:
            return jsonify({'error': 'ამანათი ყვითელშია ან ექვემდებარება გამბაჟებას!'}), 404

        # Сортируем по убыванию (от самой новой к самой старой)
        result.sort(key=lambda x: x['days_ago'] if x['days_ago'] is not None else float('inf'))

        return jsonify(result)

    def find_matching_record_in_db(self, recipient_fio):
        """
        Ищет запись в базе данных, сравнивая recipient_fio без пробелов.
        Возвращает объект с данными, если найдено.
        """
        try:
            recipient_fio_no_spaces = recipient_fio.replace(' ', '')

            matched_record = Forms.query.filter(
                func.replace(Forms.recipient_fio, ' ', '') == recipient_fio_no_spaces
            ).order_by(Forms.id.desc()).first()

            return matched_record

        except Exception as e:
            print(f"Ошибка при поиске записи: {e}")
            return None

    def check_if_issued(self, tracking_number):
        """
        Проверяет, существует ли запись с указанным tracking_number в базе.
        """
        try:
            parcel_record = ParcelIssuance.query.filter_by(tracking_number=tracking_number).first()
            return bool(parcel_record)  # Если запись есть, значит посылка выдана

        except Exception as e:
            print(f"Ошибка при проверке статуса посылки: {e}")
            return False




def register_parcel_delivery_routes(app, db):
    """
    Регистрирует маршруты для класса ParcelDelivery.
    """
    app.add_url_rule(
        '/ParcelDelivery',
        view_func=ParcelSearch.as_view('ParcelDelivery')
    )

    # Регистрируем маршрут для поиска
    app.add_url_rule('/search_by_mp', view_func=ParcelSearch.as_view('search_by_mp'), methods=['POST'])
    app.add_url_rule('/processRecords', view_func=ParcelProcessing.as_view('processRecords', db=db), methods=['POST'])
    app.add_url_rule('/downloadExcel', view_func=DownloadForRs.as_view('downloadExcel'), methods=['POST'])
    app.add_url_rule('/search_by_name', view_func=ParcelSearchByName.as_view('search_by_name'), methods=['POST'])
