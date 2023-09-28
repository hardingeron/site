from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_login import login_required, login_user, logout_user, current_user
import os 
from models import Purcell, db, User, login_manager, Menu, Storage, Booking, Messages
from config import secret_key
from sqlalchemy import func, desc

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
from openpyxl.drawing.image import Image


from flask_socketio import SocketIO
from flask_socketio import emit




import qrcode


from functions import get_last_record, generate_number_and_flight, calculate_cost, add_record, handle_image, handle_uploaded_image, get_reservation_data


app = Flask(__name__)

# socketio = SocketIO(app, cors_allowed_origins="https://vipost.ge")
socketio = SocketIO(app)

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

    # Получаем даты последних 10 рейсов для отображения из уже полученных данных
    last_10_flights = list(set(row.flight for row in all_data))[:10]

    # Получаем список всех элементов меню

    # Отображаем шаблон страницы 'all.html' с данными
    return render_template('all.html', all_data=all_data, last_10_flights=last_10_flights)





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
    return render_template('index.html')
    # return redirect(url_for('all'))







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
            handle_image(request.files['photo'], p_n, request.form['flight'], app)
            
            # Успешное сообщение и перенаправление
            flash(f'ამანათი წარმატებით დაემატა მისი ნომერერია " {p_n} "', category='success')
            return redirect(url_for('add'))
        
        
        # Рендеринг шаблона
        return render_template('add.html', last_record=last, fl=fl)
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



@app.route('/change', methods=['GET'])
@login_required
def change_get():
    try:
        # Проверка прав доступа
        if current_user.role != 'admin':
            flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
            return redirect(url_for('all'))

        # Получение id записи из параметров запроса
        id = int(request.args.get('id'))
        myrecord = db.session.query(Purcell).filter_by(id=id).first()

        # Получение списка меню и рендеринг шаблона
        return render_template('change.html', edit=myrecord)
    except SQLAlchemyError as e:
        flash('Ошибка при обращении к базе данных: ' + str(e), category='error')
        return redirect(url_for('all'))
    except Exception as e:
        flash('Произошла неизвестная ошибка: ' + str(e), category='error')
        return redirect(url_for('all'))
    

@app.route('/change', methods=['POST'])
@login_required
def change_post():
    try:
        # Проверка прав доступа
        if current_user.role != 'admin':
            flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
            return redirect(url_for('all'))

        # Получение id записи из формы
        id = int(request.form['id'])
        myrecord = db.session.query(Purcell).filter_by(id=id).first()

        # Обновление полей записи
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
        return redirect(url_for('all'))
    except SQLAlchemyError as e:
        flash('შეცდომა მოხდა მოანცემთა ბაზიდან ამოკითხვისას: ' + str(e), category='error')
        return redirect(url_for('all'))
    except Exception as e:
        flash('ამოუცნობი შეცდომა: ' + str(e), category='error')
        return redirect(url_for('all'))




@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', message='Страница не найдена'), 404




@app.route('/storage', methods=['POST', 'GET'])
@login_required
def storage():
    return render_template('storage.html')


@app.route('/save', methods=['POST'])
@login_required
def save():
    if current_user.role != 'admin':
        flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
        return redirect(url_for('all'))
    
    # Получение данных из формы
    shelf = request.form.get('shelf')
    trecing = request.form.get('trecing')

    # Валидация данных
    if not shelf or not trecing:
        return jsonify({'error': 'შეავსეთ მოცემული ველები!'})
    
    # Форматирование номера trecing
    if not trecing.startswith(('mp', 'MP')):
        trecing = f'MP{trecing}'
    else:
        trecing = trecing.upper()

    date = datetime.now().date()

    # Поиск существующей записи
    existing_record = Storage.query.filter_by(trecing=trecing).first()

    try:
        if existing_record:
            # Обновление существующей записи
            existing_record.shelf = shelf
        else:
            # Создание новой записи
            record = Storage(shelf=shelf, trecing=trecing, date=date)
            db.session.add(record)

        db.session.commit()
        # Storage.query.order_by(desc(Storage.id)).first().shelf
        # Получение последнего значения shelf
        last_shelf = shelf

        return jsonify({'last': last_shelf})
    except SQLAlchemyError as e:
        return jsonify({'error': 'მოხდა შეცდომა მონაცემთა ბაზაში მონაცემების შენახვისას.'})
    except Exception as e:
        return jsonify({'error': 'მოხდა ამოუცნობი შეცდომა.'})






@app.route('/find', methods=['POST'])
@login_required
def find():
    trecing = request.form['trecing']
    info = request.form['info']
    print('aaaaaaaaaaaaaaa')
    # Выполняем поиск посылки в базе данных
    storage = Storage.query.filter_by(trecing=trecing).first()

    if storage:
        print('bbbbbb')
        location = storage.shelf  # Местоположение посылки
        print(trecing, location, info)
        asyncio.run(send_location_message(trecing, location, info))  # асинхронный вызов функции
        if info:
            db.session.delete(storage)
            db.session.commit()
            print('ccccccccc')
    else:
        location = "ამანათი არ მოიძებნა"
        print('dddddddddd')
    
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
    selected_date = request.args.get('date')
    reis = request.args.get('route')
    reservation_data = get_reservation_data(selected_date, reis, 55)
    return render_template('reservation.html', **reservation_data)



@app.route('/reservation_big', methods=['POST', 'GET'])
@login_required
def reservation_big():
    selected_date = request.args.get('date')
    reis = request.args.get('route')
    reservation_data = get_reservation_data(selected_date, reis, 59)
    return render_template('reservation_big.html', **reservation_data)



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
    return render_template('booking.html')


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

        print(booking)
        if booking:
            db.session.commit()  # Сохранение изменений в базе данных
            bold_font = Font(bold=True)

            apply_styles_to_cell(sheet, 'G5', booking.flname)
            
            apply_styles_to_cell(sheet, 'S5', booking.pasport)

            apply_styles_to_cell(sheet, 'N8', booking.data)

            apply_styles_to_cell(sheet, 'W8', booking.destination)

            apply_styles_to_cell(sheet, 'A11', booking.position)


            sheet['A14'] = '11 : 00'
            sheet['A14'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['A14'].font = bold_font


            if booking.gender == 'male':
                sheet['G8'] = 'М / მმ'
            elif booking.gender == 'female':
                sheet['G8'] = 'Ж / მდ'
            sheet['G8'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['G8'].font = bold_font


            # Обработка оплаты
            payment_value = booking.payment
            sheet['A7'] = '₾'
            sheet['A7'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['A7'].font = bold_font

            sheet['D7'] = 200#payment_value[1:]  # Убираем первую букву
            sheet['D7'].alignment = Alignment(horizontal='center', vertical='center')
            sheet['D7'].font = bold_font


            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            data = f"თანხა {booking.payment}, მგზავრის სახელი და გვარი {booking.flname}, ბილეთის ამოღების დრო {timestamp}, პასპორტის მონაცემები {booking.pasport}, კომენტარი {booking.comment} "
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=8.8,
                border=0,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img.save("qr_code.png")


            # Вставьте QR-код в Excel
            img = Image("qr_code.png")
            img.width = img.width // 3.2  # Уменьшите размер изображения, если необходимо
            img.height = img.height // 3.2
            sheet.add_image(img, "X10")






        # Генерируем имя для сохраняемого файла
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



@app.route('/chat', methods=['POST', 'GET'])
def chat():
    messages = Messages.query.order_by(Messages.timestamp.desc()).limit(50).all()
    messages.reverse()  # Обратный порядок сообщений
    return render_template('chat.html', messages=messages)


# @app.route('/send_message', methods=['POST'])
# def send_message():
#     try:
#         data = request.get_json()
#         message_content = data.get('message')
#         user_id = current_user.get_id()
#         user = User.query.filter_by(id=user_id).first()
        
#         if user:
#             # Создайте новую запись сообщения в базе данных
#             new_message = Messages(user_id=user.login, content=message_content)
#             db.session.add(new_message)
#             db.session.commit()

#             return jsonify({'success': True, 'message': 'Сообщение успешно отправлено'})
#         else:
#             return jsonify({'success': False, 'message': 'Пользователь не найден'})
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)})
    

@socketio.on('new_message')
def handle_new_message(data):
    message_content = data['message']
    user_id = current_user.get_id()
    user = User.query.filter_by(id=user_id).first()
    timestamp = datetime.now().strftime('%H:%M:%S')

    # Создайте новое сообщение и добавьте его в базу данных
    new_message = Messages(user_id=user.login, content=message_content)
    print(new_message)
    db.session.add(new_message)
    db.session.commit()

    # Отправьте новое сообщение всем клиентам через WebSocket
    emit('new_message', {'user_id': user.login, 'timestamp': timestamp, 'content': message_content}, broadcast=True)




# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)


# with app.app_context():
#     db.create_all()




