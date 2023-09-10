from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_login import login_required, login_user, logout_user, current_user
import os 
from models import Purcell, db, User, login_manager, Menu, Storage, Booking
from config import secret_key
from sqlalchemy import func, desc

from openpyxl import Workbook
from flask import send_file
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl import Workbook, load_workbook
from sqlalchemy import or_

import openpyxl

from bot import send_location_message
import asyncio

from PIL import Image
from PIL.ExifTags import TAGS
from sqlalchemy.exc import SQLAlchemyError
import re




from functions import get_last_record, generate_number_and_flight, calculate_cost, add_record, handle_image, handle_uploaded_image


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:QazEdcQweZxcQscEsz123@localhost/packages'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключает отслеживание изменений
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=6)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=6)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/purcells')
app.config['SECRET_KEY'] = secret_key

app.config.from_object(__name__)

db.init_app(app)

login_manager.init_app(app)
login_manager.login_view = 'login'





@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
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
            flash('მომხმარებები არ მოიძებნა ან პაროლი არ ემთხვევა', category='error')

    # Отображение страницы входа
    return render_template('login.html')


@app.teardown_request
def teardown_request(exception=None):
    db.session.close()






@app.route('/all', methods=['POST', 'GET'])
@login_required
def all():
    # Получаем текущую дату
    today = datetime.now().date()

    # Определяем временной интервал для данных, которые будут отображены
    delta = timedelta(days=60)
    date_threshold = today - delta

    # Получаем данные для отображения, отсортированные по дате и номеру
    all_data = list(reversed(Purcell.query.filter(Purcell.flight >= date_threshold)
                         .order_by(Purcell.flight.asc(), Purcell.number.asc())
                         .all()))

    # Получаем список всех элементов меню
    menu = Menu.query.all()

    # Получаем даты последних 10 рейсов для отображения
    last_10_flights = [flight.flight for flight in Purcell.query.with_entities(Purcell.flight).order_by(Purcell.flight.desc()).distinct().limit(10)]

    # Отображаем шаблон страницы 'all.html' с данными
    return render_template('all.html', menu=menu, all_data=all_data, last_10_flights=last_10_flights)



@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    try:
        today = datetime.now().date()
        delta = timedelta(days=90)
        date_threshold = today - delta

        # Попытка удаления старых данных
        old_data = Purcell.query.filter(Purcell.flight < date_threshold).delete()
        db.session.commit()

        # Попытка очистки старых загруженных файлов
        folder_path = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                file_extension = os.path.splitext(filename)[1].lower()
                file_modification_time = datetime.fromtimestamp(os.path.getmtime(file_path)).date()
                days_since_modification = (today - file_modification_time).days

                if file_extension in [".jpeg", ".jpg", ".png"] and days_since_modification > 90:
                    os.remove(file_path)

    except Exception as e:
        # Если произошла ошибка, выводим ее и продолжаем
        print(f"An error occurred: {e}")

    return redirect(url_for('all'))







@app.route('/add', methods=['POST', 'GET'])
@login_required
def add():
    try:
        # Проверка прав доступа
        if current_user.role != 'admin':
            flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
            return redirect(url_for('all'))

        # Получение последней записи
        last_record = get_last_record(db)
        
        # Генерация номера и рейса
        last, fl = generate_number_and_flight(last_record)
        
        if request.method == 'POST':
            # Расчет стоимости
            cost = calculate_cost(request.form.get('payment'), request.form.get('cost'))
            
            # Добавление записи в базу данных
            p_n = add_record(request.form, cost, db)
            
            # Обработка изображения
            handle_image(request.files['photo'], request.form['number'], request.form['flight'], app)
            
            # Успешное сообщение и перенаправление
            flash(f'ამანათი წარმატებით დაემატა მისი ნომერერია " {p_n} "', category='success')
            return redirect(url_for('add'))
        
        # Получение меню
        menu = Menu.query.all()
        
        # Рендеринг шаблона
        return render_template('add.html', menu=menu, last_record=last, fl=fl)
    except SQLAlchemyError as e:
        flash('Ошибка при обращении к базе данных: ' + str(e), category='error')
    except Exception as e:
        flash('Произошла неизвестная ошибка: ' + str(e), category='error')
        return redirect(url_for('add'))  # Перенаправление в случае ошибки





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/change', methods=['POST', 'GET'])
@login_required  # Защита: только для авторизованных пользователей
def change():
    # Проверка роли пользователя, доступной только админам
    if current_user.role != 'admin':
        flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
        return redirect(url_for('all'))

    # Обработка GET запроса для получения записи
    if request.method == 'GET':
        id = int(request.args.get('id'))
        myrecord = db.session.query(Purcell).filter_by(id=id).first()

    try:
        # Обработка POST запроса для обновления записи
        if request.method == 'POST':
            id = int(request.form['id'])
            myrecord = db.session.query(Purcell).filter_by(id=id).first()

            # Используем ORM для обновления полей записи
            for field in ['sender', 'sender_phone', 'recipient', 'recipient_phone', 'inventory',
                          'cost', 'passport', 'weight', 'responsibility', 'number', 'city', 'flight']:
                setattr(myrecord, field, request.form[field])

            # Обработка загруженного изображения
            if 'photo' in request.files and request.files['photo'].filename != '':
                handle_uploaded_image(request.files['photo'], request.form['number'], request.form['flight'], app)

            # Сохранение обновленной записи в базе данных
            db.session.commit()
            return redirect(url_for('all'))

    except ValueError:
        flash('ჩაწერეთ კორექტული მონაცემები!', category='error')

    # Получение списка меню и рендеринг шаблона
    menu = Menu.query.all()
    return render_template('change.html', menu=menu, edit=myrecord)



@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', message='Страница не найдена'), 404




@app.route('/storage', methods=['POST', 'GET'])
@login_required
def storage():
    menu=Menu.query.all()
    return render_template('storage.html', menu=menu)


@app.route('/save', methods=['POST'])
@login_required
def save():
    if current_user.role != 'admin':
        flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
        return redirect(url_for('all'))
    
    shelf = request.form['shelf']
    
    trecing = request.form['trecing']
    if not trecing.startswith(('mp', 'MP')):
        trecing = f'MP{trecing}'
    else:
        trecing = trecing.upper()

    date = datetime.now().date()

    if trecing and shelf:
        existing_record = Storage.query.filter_by(trecing=trecing).first()

        if existing_record:
            existing_record.shelf = shelf
            db.session.commit()
        else:
            record = Storage(shelf=shelf, trecing=trecing, date=date)
            db.session.add(record)
            db.session.commit()
    else:
        flash('შეავსეთ მოცემული ველები!', category='error')
    
    if not shelf:
        last_record = db.session.query(Storage.shelf).order_by(desc(Storage.id)).first()
        shelf = last_record[0] if last_record else None
    
    return jsonify({'last': shelf})






@app.route('/find', methods=['POST'])
@login_required
def find():
    trecing = request.form['trecing']
    info = request.form['info']

    # Выполняем поиск посылки в базе данных
    storage = Storage.query.filter_by(trecing=trecing).first()

    if storage:
        location = storage.shelf  # Местоположение посылки
        asyncio.run(send_location_message(trecing, location, info))  # асинхронный вызов функции
        if info:
            db.session.delete(storage)
            db.session.commit()
    else:
        location = "ამანათი არ მოიძებნა"
    
    # Возвращаем данные в формате JSON
    return jsonify({'shelf': location})




@app.route('/download', methods=['POST'])
@login_required
def download():
    flight = request.form['flight']
    
    # Создание нового файла Excel
    wb = Workbook()
    ws = wb.active
    
    # Запись данных в файл Excel
    ws.append(['ნომერი', 'მიმღები', 'ტელეფონი', 'გადახდა', 'ქალაქი', 'გაცემა'])
    
    # Получение данных из базы данных и добавление их в файл Excel
    data = Purcell.query.filter_by(flight=flight).all()
    
    for item in data:
        ws.append([item.number, item.recipient, item.recipient_phone, item.cost, item.city, ''])
        # ^ Здесь столбец "Выдача" перемещен в конец и оставлен пустым
    
    # Применение стилей к ячейкам
    header_font = Font(bold=True)
    header_alignment = Alignment(horizontal='center', vertical='center')
    data_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    border = Border(left=Side(border_style='thin'), right=Side(border_style='thin'), top=Side(border_style='thin'), bottom=Side(border_style='thin'))
    
    # Применение стилей к заголовкам
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = header_alignment
    
    # Применение стилей к данным
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = data_alignment
            cell.border = border
    
    # Автоматическое расширение ширины столбцов для помещения данных
    for column in ws.columns:
        max_length = 0
        for cell in column:
            value = cell.value
            if value:
                cell_length = len(str(value))
                if cell_length > max_length:
                    max_length = cell_length
        adjusted_width = (max_length + 2) * 1.2
        column_letter = column[0].column_letter
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Сохранение файла Excel
    filename = f'data.xlsx'
    wb.save(filename)
    
    # Возврат файла для скачивания
    return send_file(filename, as_attachment=True)



@app.route('/reservation', methods=['POST', 'GET'])
@login_required
def reservation():
    menu = Menu.query.all()
    selected_date = request.args.get('date')
    reis = request.args.get('route')
    data = Booking.query.filter_by(data=selected_date, fwc=reis).all()
    number_of_records = len(data)
    number_of_free_records = 55 - number_of_records

    sum_gel = 0
    sum_rub = 0
    sum_card_gel = 0
    sum_card_rub = 0
    male_count = 0
    female_count = 0
    came_count = 0

    for person in data:
        if person.gender == 'male':
            male_count += 1
        elif person.gender == 'female':
            female_count += 1
    
    for came in data:
        if came.action == 'yes':
            came_count += 1

    came_of_count_free = number_of_records - came_count

    for booking in data:
        payment_value = booking.payment
        
        if payment_value.startswith('+'):
            payment_value = payment_value[1:]  # Убираем начальный символ "+"
            
            if payment_value.endswith('GEL'):
                sum_gel += float(payment_value[:-3])  # Убираем "GEL" и преобразуем в число
            elif payment_value.endswith('RUB'):
                sum_rub += float(payment_value[:-3])  # Убираем "RUB" и преобразуем в число
        elif payment_value.startswith('C'):
            payment_value = payment_value[1:]  # Убираем начальный символ "C"
            
            if payment_value.endswith('GEL'):
                sum_card_gel += float(payment_value[:-3])  # Убираем "GEL" и преобразуем в число
            elif payment_value.endswith('RUB'):
                sum_card_rub += float(payment_value[:-3])  # Убираем "RUB" и преобразуем в число


    seat_data = {}

    for booking in data:
        seat_data[booking.position] = {
            'name': booking.flname,
            'phone': booking.phone,
            'payment': booking.payment,
            'gender': booking.gender,
            'pasport': booking.pasport,
            'comment': booking.comment,
            'destination': booking.destination,
            'reis': booking.data,
            'action': booking.action

        }

    return render_template('reservation.html', seat_data=seat_data, 
                                               d=selected_date,
                                               menu=menu, 
                                               reis=reis,
                                               number_of_records=number_of_records, 
                                               number_of_free_records=number_of_free_records,
                                               sum_gel=sum_gel,
                                               sum_rub=sum_rub,
                                               sum_card_gel=sum_card_gel,
                                               sum_card_rub=sum_card_rub,
                                               male_count=male_count,
                                               female_count=female_count,
                                               came_count=came_count,
                                               came_of_count_free=came_of_count_free)



@app.route('/reservation_big', methods=['POST', 'GET'])
@login_required
def reservation_big():
    menu = Menu.query.all()
    selected_date = request.args.get('date')
    reis = request.args.get('route')
    data = Booking.query.filter_by(data=selected_date, fwc=reis).all()
    number_of_records = len(data)
    number_of_free_records = 59 - number_of_records

    sum_gel = 0
    sum_rub = 0
    sum_card_gel = 0
    sum_card_rub = 0
    male_count = 0
    female_count = 0
    came_count = 0

    for person in data:
        if person.gender == 'male':
            male_count += 1
        elif person.gender == 'female':
            female_count += 1
    
    for came in data:
        if came.action == 'yes':
            came_count += 1

    came_of_count_free = number_of_records - came_count

    for booking in data:
        payment_value = booking.payment
        
        if payment_value.startswith('+'):
            payment_value = payment_value[1:]  # Убираем начальный символ "+"
            
            if payment_value.endswith('GEL'):
                sum_gel += float(payment_value[:-3])  # Убираем "GEL" и преобразуем в число
            elif payment_value.endswith('RUB'):
                sum_rub += float(payment_value[:-3])  # Убираем "RUB" и преобразуем в число
        elif payment_value.startswith('C'):
            payment_value = payment_value[1:]  # Убираем начальный символ "C"
            
            if payment_value.endswith('GEL'):
                sum_card_gel += float(payment_value[:-3])  # Убираем "GEL" и преобразуем в число
            elif payment_value.endswith('RUB'):
                sum_card_rub += float(payment_value[:-3])  # Убираем "RUB" и преобразуем в число


    seat_data = {}

    for booking in data:
        seat_data[booking.position] = {
            'name': booking.flname,
            'phone': booking.phone,
            'payment': booking.payment,
            'gender': booking.gender,
            'pasport': booking.pasport,
            'comment': booking.comment,
            'destination': booking.destination,
            'reis': booking.data,
            'action': booking.action

        }

    return render_template('reservation_big.html', seat_data=seat_data, 
                                               d=selected_date,
                                               menu=menu, 
                                               reis=reis,
                                               number_of_records=number_of_records, 
                                               number_of_free_records=number_of_free_records,
                                               sum_gel=sum_gel,
                                               sum_rub=sum_rub,
                                               sum_card_gel=sum_card_gel,
                                               sum_card_rub=sum_card_rub,
                                               male_count=male_count,
                                               female_count=female_count,
                                               came_count=came_count,
                                               came_of_count_free=came_of_count_free)



@app.route('/save_data', methods=['POST'])
@login_required
def save_data():
    if request.method == 'POST':
        selected_date = request.form.get('selected_date')
        seat_number = request.form.get('seat_number')
        flname = request.form.get('flname').upper()
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        pasport = request.form.get('pasport')
        comment = request.form.get('comment')
        payment = request.form.get('payment')
        fwc = request.form.get('reis')
        destination = request.form.get('destination')
        pay = request.form.get('payment_method')
        pay_method = request.form.get('payment_method_card')
        payment = re.sub(r'[^0-9]', '', payment) 
        if payment == "":
            payment = 0   

        if pay_method is not None:
            payment = f"{pay}{payment}{pay_method}"
        else:
            payment = f"-{payment}"
        
        # Проверяем, существует ли уже запись с таким flname
        existing_booking = Booking.query.filter_by(flname=flname, data=selected_date, fwc=fwc).first()
        if existing_booking:
            return jsonify({'success': False, 'message': 'ამ სახელსა და გვარზე ადგილი უკვე დაჯავშნილია!!!!'}), 400
        else:
            booking = Booking(flname=flname, gender=gender, phone=phone, pasport=pasport, comment=comment, payment=payment, data=selected_date, position=seat_number, fwc=fwc, destination=destination)
            db.session.add(booking)
            db.session.commit()

            return jsonify({"message": "Данные успешно сохранены"})




@app.route('/booking', methods=['POST', 'GET'])
@login_required
def booking():
    menu = Menu.query.all()
    return render_template('booking.html', menu=menu)


@app.route('/edit_booking', methods=['POST'])
@login_required
def edit_booking():
    if request.method == 'POST':
        seat_number = request.form.get('seat_number')
        old_seat_number = request.form.get('old_seat_number')  # Получаем старое место
        gender = request.form.get('gender')
        flname = request.form.get('flname').upper()
        phone = request.form.get('phone')
        pasport = request.form.get('pasport')
        comment = request.form.get('comment')
        payment = request.form.get('payment')
        destination = request.form.get('destination')
        reis = request.form.get('reis')
        selected_date = request.form.get('selected_date')
        pay = request.form.get('payment_method')
        pay_method = request.form.get('payment_method_card')
        payment = re.sub(r'[^0-9]', '', payment)
        if payment == "":
            payment = 0
        
        if pay_method != None:
            payment = f"{pay}{payment}{pay_method}"
        else:
            payment = f"-{payment}"

        existing_booking = Booking.query.filter_by(fwc=reis, data=selected_date, position=old_seat_number).first() #новое место
        existing_booking_old = Booking.query.filter_by(fwc=reis, data=selected_date, position=seat_number).first() #старое место 
        if seat_number == old_seat_number:
            if existing_booking_old:
                existing_booking_old.gender = gender
                existing_booking_old.flname = flname
                existing_booking_old.phone = phone
                existing_booking_old.pasport = pasport
                existing_booking_old.payment = payment
                existing_booking_old.destination = destination
                existing_booking_old.comment = comment
                db.session.commit()
                return jsonify({'success': True, 'message': 'message'})

        if existing_booking:
            return jsonify({'success': False, 'message': 'ადგილი დაკავებულია'})
        elif existing_booking is None:
            existing_booking_old.gender = gender
            existing_booking_old.flname = flname
            existing_booking_old.phone = phone
            existing_booking_old.pasport = pasport
            existing_booking_old.payment = payment
            existing_booking_old.destination = destination
            existing_booking_old.comment = comment
            existing_booking_old.position = old_seat_number
            db.session.commit()
            return jsonify({'success': True, 'message': 'message'})
        

@app.route('/booking_del', methods=['POST'])
@login_required
def booking_del():
    if request.method == 'POST':
        seat_number = request.form.get('s_n')
        reis = request.form.get('reis')
        selected_date = request.form.get('selected_date')
        
        existing_booking = Booking.query.filter_by(fwc=reis, data=selected_date, position=seat_number).first() #новое место
        if existing_booking:

            db.session.delete(existing_booking)
            db.session.commit()

            
        return jsonify({'success': True, 'message': 'Бронирование успешно удалено'})




@app.route('/download_ved', methods=['POST'])
@login_required
def download_ved():
    reis = request.form.get('reis')
    selected_date = request.form.get('selected_date')
    filtered_data = Booking.query.filter(
        Booking.fwc == reis,
        Booking.data == selected_date,
        Booking.action == 'yes').all()

    workbook = openpyxl.load_workbook('vedom.xlsx')
    sheet = workbook.active

    start_row = 7
    col_letters = ['D', 'E', 'F', 'G']

    # Устанавливаем стиль шрифта по умолчанию с размером 10
    font = Font(size=10)
    for row_idx, data in enumerate(filtered_data, start=start_row):
        for col_idx, col_letter in enumerate(col_letters):
            cell = sheet[f'{col_letter}{row_idx}']
            if col_letter == 'D':
                cell.value = data.pasport
            elif col_letter == 'E':
                cell.value = data.flname
            elif col_letter == 'F':
                cell.value = data.position
            elif col_letter == 'G':
                cell.value = 'Москва'
            cell.font = font  # Применяем стиль шрифта к ячейке

    new_filename = 'Ведомость.xlsx'
    workbook.save(new_filename)
    workbook.close()

    return send_file(new_filename, as_attachment=True)





def apply_styles_to_cell(sheet, cell, value):
    bold_font = Font(bold=True)
    sheet[cell] = value
    sheet[cell].alignment = Alignment(horizontal='center', vertical='center')
    sheet[cell].font = bold_font



@app.route('/ticket', methods=['POST'])
@login_required
def generate_ticket():
    try:
        s_n = request.form.get('s_n')
        reis = request.form.get('reis')
        selected_date = request.form.get('selected_date')

        # Загружаем шаблон Excel-файла
        template_path = 'ticket.xlsx'
        workbook = load_workbook(template_path)
        sheet = workbook.active

        # По вашим указаниям, заполняем ячейки данными
        booking = Booking.query.filter(
            Booking.fwc == reis,
            Booking.data == selected_date,
            Booking.position == s_n
        ).first()

        if booking:
            bold_font = Font(bold=True)

            apply_styles_to_cell(sheet, 'G5', booking.flname)
            apply_styles_to_cell(sheet, 'G26', booking.flname)

            apply_styles_to_cell(sheet, 'S5', booking.pasport)
            apply_styles_to_cell(sheet, 'S26', booking.pasport)

            apply_styles_to_cell(sheet, 'N8', booking.data)
            apply_styles_to_cell(sheet, 'N29', booking.data)

            apply_styles_to_cell(sheet, 'W8', booking.destination)
            apply_styles_to_cell(sheet, 'W29', booking.destination)

            apply_styles_to_cell(sheet, 'A11', booking.position)
            apply_styles_to_cell(sheet, 'A32', booking.position)


            sheet['A14'] = '11 : 00'
            sheet['A14'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['A14'].font = bold_font

            sheet['A35'] = '11 : 00'
            sheet['A35'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['A35'].font = bold_font


            if booking.gender == 'male':
                sheet['G8'] = 'М / მმ'
            elif booking.gender == 'female':
                sheet['G8'] = 'Ж / მდ'
            sheet['G8'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['G8'].font = bold_font


            if booking.gender == 'male':
                sheet['G29'] = 'М / მმ'
            elif booking.gender == 'female':
                sheet['G29'] = 'Ж / მდ'
            sheet['G29'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['G29'].font = bold_font

            # Обработка оплаты
            payment_value = booking.payment
            sheet['A7'] = '₾'
            sheet['A7'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['A7'].font = bold_font

            sheet['D7'] = 200#payment_value[1:]  # Убираем первую букву
            sheet['D7'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['D7'].font = bold_font

            sheet['A28'] = '₾'
            sheet['A28'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['A28'].font = bold_font

            sheet['D28'] = 2000#payment_value[1:]  # Убираем первую букву
            sheet['D28'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['D28'].font = bold_font


        # Генерируем имя для сохраняемого файла
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_filename = f'bileti.xlsx'

        # Сохраняем файл
        workbook.save(output_filename)

        # Отправляем файл в ответе с правильными заголовками
        return send_file(
            output_filename,
            as_attachment=True,
            download_name=output_filename
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})



@app.route('/booking_action', methods=['POST'])
@login_required
def action():
    form_data = request.form  # Получение данных из полей формы
    old_seat_number = form_data.get('old_seat_number')
    reis = form_data.get('reis')
    selected_date = form_data.get('selected_date')

    payment = form_data.get('payment')
    pay = request.form.get('payment_method')
    pay_method = request.form.get('payment_method_card')
    payment = re.sub(r'[^0-9]', '', payment)
    if payment == "":
        payment = 0
        
    if pay_method != None:
        payment = f"{pay}{payment}{pay_method}"
    else:
        payment = f"-{payment}"
    booking = Booking.query.filter_by(fwc=reis, data=selected_date, position=old_seat_number).first()
    if booking:
        booking.action = 'yes'  # Изменение значения столбца 'action'
        booking.payment = payment
        db.session.commit()  # Сохранение изменений в базе данных

    # Далее вы можете использовать полученные данные как вам нужно

    # Верните какой-то ответ, например:
    return jsonify(success=True, message="Data received successfully")



    




if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', debug=True)

# with app.app_context():
#     db.create_all()




