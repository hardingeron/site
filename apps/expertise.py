from flask.views import MethodView
from flask import request, render_template, jsonify, send_file
from flask_login import login_required
from models import Expertise  # Замените на ваш файл с моделями
from sqlalchemy import func, desc, update
from functions import trecing_redactor, find_duplicates_in_json, allowed_file, xml_convertor, status_checker
import json
from werkzeug.utils import secure_filename
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl import load_workbook
from io import BytesIO

class ExpertiseView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def get(self):
        # Получаем выбранную дату из параметров запроса
        selected_date = request.args.get('selected_date', None)

        if selected_date:
            latest_date = selected_date
        else:
            # Если дата не выбрана, получаем самую свежую дату
            latest_date = self.db.session.query(self.db.func.max(Expertise.date)).scalar()

        # Получаем все записи с самой свежей или выбранной датой
        expertise_records = Expertise.query.filter_by(date=latest_date).all()

        # Получаем все уникальные даты и сортируем по убыванию
        unique_dates = self.db.session.query(func.distinct(Expertise.date)).order_by(desc(Expertise.date)).all()
        unique_dates_list = [date[0].strftime('%Y-%m-%d') for date in unique_dates]

        # Передаем данные в шаблон
        return render_template('expertise.html', records=expertise_records, date=latest_date, unique_dates_list=unique_dates_list)

# Регистрируем маршрут для просмотра экспертизы



class ExpertiseAddRecordView(MethodView):
    def __init__(self, db):
        self.db = db
    decorators = [login_required]

    def post(self):
        try:
            # Получаем данные из POST-запроса
            data = request.get_json()
            tracking = trecing_redactor(data['tracking'])

            # Загрузка данных из JSON-файла
            with open('expertise_data.json', 'r', encoding='utf-8') as json_file:
                expertise_data = json.load(json_file)

            # Получение записи по ключу data['tracking']
            tracking_key = tracking
            if tracking_key in expertise_data:
                record_data = expertise_data[tracking_key]
            else:
                return jsonify({'error': 'ამანათი არ არსებობს!'}), 404  # Или другой HTTP-статус по вашему выбору

            # Создаем новую запись
            new_record = Expertise(
                Number=data['Number'],
                tracking=tracking,
                comment=data['comment'],
                date=data['date'],
                status=record_data[1],
                weight=record_data[7],
                recipient=record_data[5]
            )

            # Добавляем запись в базу данных
            self.db.session.add(new_record)
            self.db.session.commit()

            # Формируем список экспертиз
            expertise_list = [{
                'id': new_record.id,
                'status': new_record.status,
                'recipient': new_record.recipient,
                'weight': new_record.weight,
                'Number': new_record.Number,
                'tracking': new_record.tracking,
                'comment': new_record.comment,
                'date': new_record.date.strftime('%Y-%m-%d')
            }]

            # Ищем дубликаты в JSON-файле
            duplicates = find_duplicates_in_json('expertise_data.json', tracking)
            print(duplicates)

            id_trecing = int(new_record.id)

            # Добавляем дубликаты в базу данных
            for duplicate_key in duplicates:
                id_trecing += 1
                dup_data = expertise_data[duplicate_key]
                duplicate_record = Expertise(
                    Number=data['Number'],
                    tracking=duplicate_key,
                    comment='თანაგზავნილი',
                    date=data['date'],
                    status=dup_data[1],
                    weight=dup_data[7],
                    recipient=dup_data[5]
                )
                self.db.session.add(duplicate_record)

                n = {
                    'id': id_trecing,
                    'status': dup_data[1],
                    'recipient': dup_data[5],
                    'weight': dup_data[7],
                    'Number': data['Number'],
                    'tracking': duplicate_key,
                    'comment': 'თანაგზავნილი',
                    'date': new_record.date.strftime('%Y-%m-%d')
                }
                expertise_list.append(n)

            self.db.session.commit()
            # Возвращаем данные о новой записи
            return jsonify(expertise_list), 200

        except Exception as e:
            return jsonify({'error': 'Error adding record'}), 500


class ExpertiseDeleteRecordView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def post(self):
        try:
            # Получаем данные из POST-запроса
            data = request.get_json()

            # Получаем ID записи, которую нужно удалить
            record_id = data.get('id')

            # Проверяем, что ID был передан
            if record_id is not None:
                # Находим запись в базе данных по ID
                record_to_delete = Expertise.query.get(record_id)

                # Проверяем, что запись существует
                if record_to_delete:
                    # Удаляем запись из базы данных
                    self.db.session.delete(record_to_delete)
                    self.db.session.commit()

                    return jsonify({'message': 'Record deleted successfully'}), 200
                else:
                    return jsonify({'error': 'Record not found'}), 404
            else:
                return jsonify({'error': 'ID not provided'}), 400

        except Exception as e:
            return jsonify({'error': 'Error deleting record'}), 500



class RSXmlUploadView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def post(self):
        print('aaaaaaaaaaaaaaaaaaaaaaaa')
        try:
            if "xmlFile" in request.files:
                xml_file = request.files["xmlFile"]
                date_value = request.form.get('date')

                # Проверка, что файл имеет разрешенное расширение (xml)
                if xml_file and allowed_file(xml_file.filename):
                    # Сохранение XML-файла с именем Export.xml в корневую папку
                    xml_file.save(secure_filename("Export.xml"))

                    # Вызов функции xml_convertor после успешной загрузки файла
                    xml_convertor()

                    # Чтение данных из JSON-файла
                    with open('expertise_data.json', 'r', encoding='utf-8') as json_file:
                        expertise_data = json.load(json_file)

                    # Создаем список для значений tracking, которые будем обновлять
                    tracking_values = list(expertise_data.keys())

                    # Обновляем записи в базе данных
                    for tracking_key, values in expertise_data.items():
                        update_stmt = (
                            update(Expertise)
                            .where(Expertise.tracking == tracking_key)
                            .values(status=values[1])
                        )
                        self.db.session.execute(update_stmt)

                    # Сохраняем изменения в базе данных только один раз в конце
                    self.db.session.commit()

                    # Возвращение JSON-ответа
                    return jsonify({'success': True, 'message': 'ბაზა წარმატებით განახლდა'})

            # В случае ошибки
            return jsonify({'success': False, 'message': 'ფაილის ფორმატი არასწორია!'})

        except Exception as e:
            return jsonify({'error': 'Error processing file'}), 500



class TrecCheckerView(MethodView):

    def post(self):
        try:
            # Получаем данные из запроса
            trecing_value = trecing_redactor(request.form.get('trecing_value', ''))

            # Читаем содержимое файла expertise_data.json
            with open('expertise_data.json', 'r', encoding='utf-8') as json_file:
                expertise_data = json.load(json_file)

            # Проверяем наличие ключа в объекте
            if trecing_value in expertise_data:
                result = expertise_data[trecing_value]
                information = status_checker(result)
                return jsonify({'success': True, 'result': information})
            else:
                return jsonify({'success': False, 'message': 'Запись не найдена.'})

        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})



class ExpertiseExportView(MethodView):
    def __init__(self):
        pass

    def post(self):
        date = request.form.get('date')

        # Получаем данные из базы данных, отфильтрованные по дате
        expertise_data = Expertise.query.filter_by(date=date).all()

        workbook = load_workbook('documents/expertise.xlsx')
        sheet = workbook.active

        start_row = 2  # Начинаем с второй строки, так как первая строка содержит заголовки
        col_letters = ['C', 'D', 'E', 'F', 'G', 'H']

        # Устанавливаем стиль шрифта по умолчанию с размером 10
        font = Font(size=10)
        alignment = Alignment(horizontal='center', vertical='center')
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

        # Заполняем данные
        for row_idx, data in enumerate(expertise_data, start=start_row):
            for col_idx, col_letter in enumerate(col_letters):
                cell = sheet[f'{col_letter}{row_idx}']
                if col_letter == 'D':
                    cell.value = data.recipient
                elif col_letter == 'E':
                    cell.value = data.weight
                elif col_letter == 'F':
                    cell.value = data.Number
                elif col_letter == 'G':
                    cell.value = data.tracking
                elif col_letter == 'H':
                    cell.value = data.comment
                # Пропускаем запись в столбец 'C', просто применяем форматирование
                elif col_letter == 'C':
                    pass
                cell.font = font  # Применяем стиль шрифта к ячейке
                cell.alignment = alignment  # Центрируем содержимое ячейки
                cell.border = thin_border  # Добавляем границы

        # Сохраняем файл в оперативной памяти
        output = BytesIO()
        workbook.save(output)
        workbook.close()
        output.seek(0)  # Возвращаемся в начало буфера

        # Отправляем файл напрямую из памяти
        return send_file(output, as_attachment=True, download_name='expertise-list.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def register_expertise_routes(app, db):
    app.add_url_rule('/expertise', view_func=ExpertiseView.as_view('expertise', db=db))
    app.add_url_rule('/expertise_add_record', view_func=ExpertiseAddRecordView.as_view('expertise_add_record', db=db))
    app.add_url_rule('/expertise_deleted', view_func=ExpertiseDeleteRecordView.as_view('expertise_deleted', db=db))
    app.add_url_rule('/rs_xml', view_func=RSXmlUploadView.as_view('rs_xml', db=db))
    app.add_url_rule('/trecing_checker', view_func=TrecCheckerView.as_view('trecing_checker'))
    app.add_url_rule('/expertise_export', view_func=ExpertiseExportView.as_view('expertise_export'))