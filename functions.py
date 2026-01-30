from PIL import Image
from PIL.ExifTags import TAGS
from models import Purcell
import os
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json

from flask import jsonify

from PIL import Image
from PIL.ExifTags import TAGS
from sqlalchemy import func
from models import Purcell, Booking, Storage, Forms, Shipments
import re
import xml.etree.ElementTree as ET
from openpyxl.styles import Alignment, Font
import random

#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА /add
#===========================================================================================================================================================

# Функция для получения последней записи в базе данных
# def get_last_record(db): 
#     last_record = db.session.query(Purcell).order_by(Purcell.id.desc()).first()
#     print(last_record)
#     if last_record:
#         number = int(last_record.number) + 1
#         print(number, 'awwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
#     else:
#         number = 1
#     return number

# Функция для получения последней записи в базе данных
def get_last_record(db): 
    last_record = db.session.query(Purcell).order_by(Purcell.id.desc()).first()
    print(last_record)
    if last_record:
        number = int(last_record.number) + 1
        # Проверяем, если номер посылки больше или равен 5, то устанавливаем его в 1
        if number >= 1000:
            number = 1
    else:
        number = 1 
    return number

from datetime import datetime

def generate_new_number(data, last_record, db):
    current_date = datetime.utcnow().date()
    
    # Преобразуем дату в строку в формате YYYY-MM-DD
    current_date_str = current_date.strftime('%Y-%m-%d')
    
    while True:
        existing_record = db.session.query(Purcell).filter_by(number=int(last_record), date=current_date_str).first()
        
        # Если запись не существует, прерываем цикл
        if existing_record is None:
            break
        
        # Иначе увеличиваем номер
        last_record += 1
        
        # Проверяем, если номер посылки больше или равен 5, то устанавливаем его в 1
        if last_record >= 1000:
            last_record = 1
    
    return last_record


# Функция для расчета стоимости
def calculate_cost(payment_type, cost_amount, currency):
    if payment_type == 'paid':
        cost = f"+ {cost_amount} {currency}"
    elif payment_type == 'not_paid':
        cost = f"- {cost_amount} {currency}"
    else:
        cost = f"+ {cost_amount} {currency}💳"
    return cost

# Функция для добавления записи в базу данных
def add_record(last, data, cost, db, user_role):
    data['currentDateTime'] = data['currentDateTime'].replace(":", ".")
    if data['departureStatus'] == 'selected':
        check_box = '+'
    else:
        check_box = '-'

    try:
        add = Purcell(
            sender=data['sender'].upper(),
            sender_phone=data['sender_phone'],
            recipient=data['recipient'].upper(),
            recipient_phone=data['recipient_phone'],
            inventory=data['inventory'].replace('\n', ' ').replace('\r', ' '),
            cost=cost,
            passport=data['passport'],
            weight=data['weight'].upper(),
            responsibility=data['responsibility'].upper(),
            number=last,
            city=data['city'],
            flight=data['currentDateTime'],
            image=f"static/purcells/{last}-{data['currentDateTime']}.jpeg",
            where_from=user_role,
            departure_status = check_box
        )
        # Добавляем запись в сессию и фиксируем изменения в базе данных
        db.session.add(add)
        db.session.commit()
        
        return last
    except Exception as e:
        # Обработка ошибки и возвращение сообщения об ошибке
        return f"Ошибка при сохранении записи: {str(e)}"


# Функция для обработки изображения
def handle_image(file, number, date, app):
    date = date.replace(":", ".")
    filename = f"{number}-{date}.jpeg"
    print(filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # Сохраняем загруженное изображение
    file.save(image_path)
    
    # Открываем изображение с помощью Pillow
    image = Image.open(image_path)
    image_exif = image._getexif()
    
    # Обрабатываем ориентацию изображения
    if image_exif is not None:
        for tag, value in image_exif.items():
            if TAGS.get(tag) == 'Orientation':
                if value == 3:
                    image = image.rotate(180, expand=True)
                elif value == 6:
                    image = image.rotate(270, expand=True)
                elif value == 8:
                    image = image.rotate(90, expand=True)
    
    # Сжимаем изображение с заданным качеством
    compress_quality = 50
    image.save(image_path, 'JPEG', quality=compress_quality)

#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА /add >----> конец <----< ---------------------------------------------------------------
#===========================================================================================================================================================



#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА /change
#===========================================================================================================================================================
def handle_uploaded_image(file, parcel_id, app):
    # Формирование имени файла на основе номера и рейса
    purcell_entry = Purcell.query.get(parcel_id)
    date = purcell_entry.flight
    date = date.replace(":", ".")

    filename = f"{purcell_entry.number}-{date}.jpeg"
    
    # Полный путь до места сохранения изображения
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Сохранение загруженного изображения на диск
    file.save(image_path)

    # Обработка изображения перед сохранением
    process_image(image_path)


def process_image(image_path):
    # Открытие изображения с помощью библиотеки PIL
    image = Image.open(image_path)
    
    # Получение метаданных (EXIF) изображения
    image_exif = image._getexif()
    
    if image_exif is not None:
        # Поворот изображения в соответствии с ориентацией из метаданных
        for tag, value in image_exif.items():
            if TAGS.get(tag) == 'Orientation':
                if value == 3:
                    image = image.rotate(180, expand=True)
                elif value == 6:
                    image = image.rotate(270, expand=True)
                elif value == 8:
                    image = image.rotate(90, expand=True)

    # Качество сжатия изображения (значение от 0 до 100)
    compress_quality = 75  # Задайте желаемое значение качества сжатия
    
    # Сохранение обработанного изображения в формате JPEG
    image.save(image_path, 'JPEG', quality=compress_quality)


def edit_parcel_(db, data):
    # Находим запись по id
    purcell_entry = Purcell.query.get(data['id'])

    # Обновляем значения записи
    purcell_entry.sender = data['sender']
    purcell_entry.sender_phone = data['sender_phone']
    purcell_entry.recipient = data['recipient']
    purcell_entry.recipient_phone = data['recipient_phone']
    purcell_entry.inventory = data['inventory'].replace('\n', ' ').replace('\r', ' ')
    purcell_entry.cost = data['cost']
    purcell_entry.passport = data['passport']
    purcell_entry.weight = data['weight']
    purcell_entry.responsibility = data['responsibility']
    purcell_entry.city = data['city']
    purcell_entry.departure_status = data['departureStatus']

    # Сохраняем изменения в базе данных
    db.session.commit()

    # Возвращаем сообщение об успешном обновлении записи



#===========================================================================================================================================================
#                                               ДЛЯ ОБРАБОТЧИКА /change >----> конец <----< 
#===========================================================================================================================================================



#===========================================================================================================================================================
#                                                ДЛЯ ОБРАБОТЧИКА /reservation /reservation_big
#===========================================================================================================================================================
def get_reservation_data(selected_date, reis, bus):
    data = Booking.query.filter_by(data=selected_date, fwc=reis).all()
    number_of_records = len(data)
    number_of_free_records = bus - number_of_records

    sum_gel = 0
    sum_rub = 0
    sum_usd = 0
    sum_eur = 0
    sum_card_gel = 0
    sum_card_rub = 0
    sum_card_usd = 0
    sum_card_eur = 0
    male_count = 0
    female_count = 0
    came_count = 0
    sum_gel_p = 0
    sum_gel_pc = 0
    sum_rub_p = 0
    sum_rub_pc = 0


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
                sum_gel_p += 1
            elif payment_value.endswith('RUB'):
                sum_rub += float(payment_value[:-3])  # Убираем "RUB" и преобразуем в число
                sum_rub_p += 1
            elif payment_value.endswith('USD'):
                sum_usd += float(payment_value[:-3])  # Убираем "USD" и преобразуем в число
            elif payment_value.endswith('EUR'):
                sum_eur += float(payment_value[:-3])  # Убираем "EUR" и преобразуем в число

        elif payment_value.startswith('C'):
            payment_value = payment_value[1:]  # Убираем начальный символ "C"
            
            if payment_value.endswith('GEL'):
                sum_card_gel += float(payment_value[:-3])  # Убираем "GEL" и преобразуем в число
                sum_gel_pc += 1
            elif payment_value.endswith('RUB'):
                sum_card_rub += float(payment_value[:-3])  # Убираем "RUB" и преобразуем в число
                sum_rub_pc += 1
            elif payment_value.endswith('USD'):
                sum_card_usd += float(payment_value[:-3])  # Убираем "USD" и преобразуем в число
            elif payment_value.endswith('EUR'):
                sum_card_eur += float(payment_value[:-3])  # Убираем "EUR" и преобразуем в число

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
            'action': booking.action,
            'date_of_birth': booking.date_of_birth

        }

    return {
        'seat_data': seat_data,
        'd': selected_date,
        'reis': reis,
        'number_of_records': number_of_records,
        'number_of_free_records': number_of_free_records,
        'sum_gel': sum_gel,
        'sum_rub': sum_rub,
        'sum_usd': sum_usd,
        'sum_eur': sum_eur,
        'sum_card_gel': sum_card_gel,
        'sum_card_rub': sum_card_rub,
        'sum_card_usd': sum_card_usd,
        'sum_card_eur': sum_card_eur,
        'male_count': male_count,
        'female_count': female_count,
        'came_count': came_count,
        'came_of_count_free': came_of_count_free,
        'sum_gel_p': sum_gel_p,
        'sum_gel_pc': sum_gel_pc,
        'sum_rub_p': sum_rub_p,
        'sum_rub_pc': sum_rub_pc
    }






#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА /reservation /reservation_big >----> конец <----< ---------------------------------------------------------------
#===========================================================================================================================================================



#===========================================================================================================================================================
#                                                ДЛЯ ОБРАБОТЧИКА /storage   /add
#===========================================================================================================================================================


def validate_input(shelf, trecing):
    return bool(shelf) and bool(trecing)


def format_trecing(trecing):
    if not trecing.startswith(('mp', 'MP')):
        trecing = f'MP{trecing}'
    else:
        trecing = trecing.upper()
    return trecing


def save_record(shelf, trecing, date, db):
    existing_record = Storage.query.filter_by(trecing=trecing).first()
    if existing_record:
        existing_record.shelf = shelf
    else:
        record = Storage(shelf=shelf, trecing=trecing, date=date)
        db.session.add(record)
    db.session.commit()
    return shelf


#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА /storage /add >----> конец <----< ---------------------------------------------------------------
#===========================================================================================================================================================




#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА /
#===========================================================================================================================================================
def get_sorted_dates(db):
    # Запрос уникальных дат и городов из базы данных
    unique_dates_cities = (db.session.query(Shipments.send_date, Shipments.city_from).filter(Shipments.send_date.isnot(None)).distinct()
)
    print(unique_dates_cities, 'uniquedatescities!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    # Списки для дат Москвы и Санкт-Петербурга
    msk_dates = []
    spb_dates = []

    # Разбираем полученные даты и города
    for send_date, city_from in unique_dates_cities:
        if city_from == 'Москва':
            msk_dates.append(send_date)
        elif city_from == 'Санкт-Петербург':
            spb_dates.append(send_date)
    
    print(msk_dates, spb_dates, 'mskdates spbdates!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    # Сортировка дат по убыванию (от новых к старым)
    msk_dates.sort(reverse=True)
    spb_dates.sort(reverse=True)

    msk_dates = [d.strftime('%d-%m-%Y') for d in msk_dates]
    spb_dates = [d.strftime('%d-%m-%Y') for d in spb_dates]
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print(msk_dates, spb_dates, 'mskdates spbdates!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    # Возвращаем отсортированные даты
    return msk_dates, spb_dates




def update_json_file(msk_dates, spb_dates):
    # Создание словаря с датами для Москвы и Санкт-Петербурга
    data = {
        "msk_dates": msk_dates,
        "spb_dates": spb_dates
    }

    try:
        # Открытие JSON-файла для записи
        with open("static/json/dates.json", "w") as json_file:
            # Запись данных в файл в формате JSON
            json.dump(data, json_file)
    except Exception as e:
        # Логирование ошибки
        log_error(e)


def delete_old_data(db):
    # Получение текущей даты
    today = datetime.now().date()

    # Определение временного порога (90 дней назад)
    delta = timedelta(days=180)
    date_threshold = today - delta

    # Попытка удаления старых данных из базы данных
    old_data = Purcell.query.filter(Purcell.date < date_threshold).delete()
    db.session.commit()


def clean_old_files(upload_folder):
    # Получение текущей даты
    today = datetime.now().date()
    
    # Проверка файлов в указанной папке
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            # Получение расширения файла
            file_extension = os.path.splitext(filename)[1].lower()

            # Получение даты последнего изменения файла
            file_modification_time = datetime.fromtimestamp(os.path.getmtime(file_path)).date()
            
            # Вычисление количества дней с момента последнего изменения файла
            days_since_modification = (today - file_modification_time).days

            # Проверка расширения и старости файла, если он старше 90 дней и имеет указанные расширения, удалить его
            if file_extension in [".jpeg", ".jpg", ".png"] and days_since_modification > 150:
                os.remove(file_path)



#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА />----> конец <----< ---------------------------------------------------------------
#===========================================================================================================================================================


#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА /booking 
#===========================================================================================================================================================

# Функция для обработки оплаты
def process_payment(payment, pay, pay_method):
    payment = re.sub(r'[^0-9]', '', payment)
    if payment == "":
        payment = 0
    if pay_method is not None:
        payment = f"{pay}{payment}{pay_method}"
    else:
        payment = f"-{payment}"
    return payment

# Функция для сохранения данных в базу данных
def save_booking_to_db(db, selected_date, seat_number, flname, gender, phone, pasport, comment, payment, fwc, destination, date_of_birth):
    booking = Booking(
        flname=flname,
        gender=gender,
        phone=phone,
        pasport=pasport,
        comment=comment,
        payment=payment,
        data=selected_date,
        position=seat_number,
        fwc=fwc,
        destination=destination,
        date_of_birth=date_of_birth
    )
    db.session.add(booking)
    db.session.commit()


# Функция для обновления данных бронирования
def update_booking(db, booking, gender, flname, phone, pasport, payment, destination, comment, seat_number, date_of_birth):
    booking.gender = gender
    booking.flname = flname
    booking.phone = phone
    booking.pasport = pasport
    booking.payment = payment
    booking.destination = destination
    booking.comment = comment
    booking.position = seat_number
    booking.date_of_birth = date_of_birth
    db.session.commit()


# Функция для получения существующего бронирования
def get_existing_booking(reis, selected_date, seat_number):
    return Booking.query.filter_by(fwc=reis, data=selected_date, position=seat_number).first()

#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА />----> конец <----< ---------------------------------------------------------------
#===========================================================================================================================================================

#===========================================================================================================================================================
#-------------------------- вспомогательные для манифеста <----< ---------------------------------------------------------------
#===========================================================================================================================================================

def manifest_filter(filtered_forms):
    # Здесь вы можете добавить код для обработки отфильтрованных записей,
    # сохранения файла и т.д. В примере я просто возвращаю JSON с данными.
    return filtered_forms



#===========================================================================================================================================================
#-------------------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
#===========================================================================================================================================================

def log_error(error):
    # Здесь вы можете добавить логику логирования ошибок, например, в файл, базу данных или на сервер
    print(f"An error occurred: {error}")


def trecing_redactor(trecing):
    trecing_red = trecing.upper()
    if not trecing_red.startswith("MP"):
        trecing_red = "MP" + trecing_red
    return trecing_red
    


#===========================================================================================================================================================
#-------------------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ >----> конец <----< ---------------------------------------------------------------
#===========================================================================================================================================================



#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА /expertise>---->  <----< ---------------------------------------------------------------
#===========================================================================================================================================================
    

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in 'xml'


def xml_convertor():
    # Определение пространства имен
    namespace = {'ss': 'urn:schemas-microsoft-com:office:spreadsheet'}

    # Чтение XML файла
    xml_file_path = 'Export.xml'
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Извлечение данных из столбцов
    data_columns = [
        "სტატუსი",
        "დაბეგვრის ტიპი",
        "გზავნილის ნომერი",
        "ატვირთვის თარიღი",
        "ჩამოსვლის თარიღი",
        "სახელი და გვარი",
        "ქვეყანა",
        "წონა",
    ]

    # Создание словаря для хранения данных
    data_dict = {}

    # Итерация по строкам (Row) в таблице
    for row in root.findall('.//ss:Row', namespace):
        # Создание списка для хранения данных текущей строки
        row_data = []
        
        # Итерация по ячейкам (Cell) в строке
        cells = row.findall('ss:Cell', namespace)
        # Извлечение данных из нужных ячеек
        for i, data_column in enumerate(data_columns):
            # Ищем ячейку с данными по текущему столбцу
            cell_data = cells[i].find('.//ss:Data[@ss:Type="String"]', namespace)
            # Если ячейка найдена, добавляем данные в список
            if cell_data is not None:
                row_data.append(cell_data.text)
            else:
                # Если ячейка не найдена, добавляем пустое значение
                row_data.append(None)
        
        # Используем "გზავნილის ნომერი" в качестве ключа в словаре
        if row_data:
            data_dict[row_data[2]] = row_data

    # Преобразование словаря данных в JSON
    json_data = json.dumps(data_dict, ensure_ascii=False, indent=2)

    # Сохранение JSON в файл
    json_file_path = 'expertise_data.json'
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)






# стили для экселя

def apply_styles_to_cell(sheet, cell, value):
    bold_font = Font(bold=True)
    sheet[cell] = value
    sheet[cell].alignment = Alignment(horizontal='center', vertical='center')
    sheet[cell].font = bold_font



#-------------
def random_names():
    names = [
    "ALEXANDER IVANOV", "EKATERINA PETROVA", "DMITRY SMIRNOV", "ANNA FEDOROVA", "SERGEI KOZLOV",
    "MARIA NOVIKOVA", "IVAN SOKOLOV", "ANASTASIA KUZNETSOVA", "ARTEM POPOV", "OLGA MOROZOVA",
    "VLADIMIR KUZMIN", "IRINA PAVLOVA", "NIKOLAI ZAKHAROV", "YULIA SEMENOVA", "PAVEL KONDRATOV",
    "SVETLANA SMIRNOVA", "ANDREI FEDOROV", "ELENA VASILIEVA", "ANDREY LEBEDEV", "TATIANA KUZNETSOVA",
    "ALEXEY MEDVEDEV", "NATALIA YAKOVLEVA", "VIKTORIA PROKOPIEVA", "MIKHAIL SOKOLOV", "ANGELINA KONOVALENKO",
    "RUSLAN VORONIN", "YANA PETROVA", "IGOR KARPOV", "VALERIA STEPANOVA", "ANTONINA MALININA", "KONSTANTIN ZAITSEV",
    "MARINA ROMANOVA", "PAVEL SERGEYEV", "OLGA KIRILLOVA", "ILYA KUZNETSOV", "KSENIA MOROZOVA", "DENIS POPOV",
    "VICTORIA KOVALENKO", "YURY ANTONOV", "JULIA KOROLEVA", "ALEXANDRA SIDOROVA", "MAXIM KUZMIN", "LARISA PAVLOVA",
    "SERGEY GORSHKOV", "ANNA KONONOVA", "ALEKSEI FOMIN", "EKATERINA KOROLEVA", "ARSENII VOLKOV", "IRINA ZAKHAROVA",
    "ALEKSANDR GORBUNOV", "ALEXANDRA KUZNETSOVA", "ANDREI MOROZOV", "VICTORIA SEMENOVA", "MAXIM FEDOROV",
    "OLGA PETROV", "KIRILL KONDRATOV", "YULIA ROMANOVA", "DENIS KOVALENKO", "SVETLANA ZAKHAROVA",
    "ANTONINA SIDOROVA", "DMITRY LEBEDEV", "EKATERINA SERGEYEVA", "ILYA KIRILLOV", "MARIA GORBUNOVA",
    "IGOR MALININ", "ANNA KUZMINA", "ARTEM ZAITSEV", "ELENA KONOVA", "NIKOLAI GORSHKOV", "VALERIA PAVLOVA",
    "SERGEY PROKOPIEV", "ANGELINA MEDVEDEVA", "VLADIMIR ANTONOV", "TATIANA KOROLEVA", "ANDREY VORONIN",
    "LARISA YAKOVLEVA", "PAVEL KARPOV", "NATALIA KIRKOROVA", "MIKHAIL ZAITSEV", "KSENIA SOKOLOVA",
    "YURY KUZNETSOV", "MARINA KUZMINA", "ALEKSANDR FOMIN", "ELENA VORONOVA", "ALEXEI KIRILLOV",
    "VALERIYA KUZNETSOVA", "VIKTOR KOROLEV", "ANNA SMIRNOVA", "ANDREY SOKOLOV", "OLGA GORBUNOVA",
    "ALEKSANDRA ROMANOVA", "DMITRIY KUZMIN", "EKATERINA ZAKHAROVA", "MAXIM KARPOV", "YANA KONONOVA",
    "VLADIMIR LEBEDEV", "MARIYA KIRKOROVA", "ANDREY PETUKHOV", "DARIA SMOLYAKOVA", "ALEXEY KONDRATENKO", 
    "SVETLANA IVANOVA", "IGOR SEMYONOV", "MARINA LUKINA", "ANDREI SOKOLOVSKY", "EKATERINA KAZAKOVA",
    "VLADIMIR PETROVICH", "ANNA DUBROVSKAYA", "DMITRY STEPANOV", "ELENA FEDOTOVA", "ALEXANDER ROMANOV",
    "OLGA GAVRILOVA", "MAXIM TARASOV", "YULIA KORNEEVA", "NIKOLAI SHIROKOV", "MARIA TIMOFEEVA",
    "PAVEL VASILIEV", "EKATERINA KOSHKINA", "DMITRIY MOROZOV", "NATALIA KOVALEVSKAYA", "ANDREY KOZLOV",
    "SVETLANA EGOROVA", "SERGEY BORISOV", "ANASTASIA EGOROVA", "ALEXANDER BELIAKOV", "EKATERINA LEBEDEVA",
    "DMITRY KUZMIN", "ANNA ZAKHAROVA", "YURY LARIN", "TATIANA FROLOVA", "ANDREY LUKIN", "ELENA ZAITSEVA",
    "ALEXEY SMIRNOV", "MARINA PAVLOVA", "ANTON KISELEV", "IRINA KARPOVA", "DMITRIY TITOV", "EKATERINA ZAITSEVA",
    "VLADIMIR LEBEDIN", "OLGA KUZNETSOVA", "NIKOLAI BELIAEV", "ANASTASIA SMIRNOVA", "IGOR ZHDANOV",
    "MARIA BELYAEVA", "ANDREY KURAEV", "EKATERINA ORLOVA", "ALEXANDER PAVLOV", "ANNA KUZMINA", "VLADIMIR RODIN",
    "SVETLANA YAKOVLEVA", "DMITRY DMITRIEV", "YULIA GRIGORIEVA", "VLADIMIR NIKOLAEV", "TATIANA PETROVA",
    "MAXIM KUZNETSOV", "EKATERINA NOVIKOVA", "ANDREI ZUBKOV", "NATALIA MOROZOVA", "SERGEY BORISOV",
    "ALEXANDRA SOKOLOVA", "DMITRY PETROV", "ELENA KONSTANTINOVA", "VLADIMIR GAVRILOV", "ANNA SMIRNOVA",
    "NIKOLAI KISELEV", "MARIA KOMAROVA", "ANDREY TIMOFEEV", "OLGA SMIRNOVA", "VLADIMIR VORONOV",
    "IRINA IVANOVA", "DMITRY EGOROV", "EKATERINA KAZANTSEVA", "ANDREY ZHDANOV", "MARIA SEMENOVA",
    "MAXIM EGOROV", "YULIA KISELEVA", "ALEXANDER KUZNETSOV", "ANASTASIA GAVRILOVA",
    "VLADIMIR KISELEV", "EKATERINA PAVLOVA", "DMITRY BORISOV", "MARIA ZHDANOVA", "ANDREY KUZNETSOV",
    "EKATERINA SERGEEVA", "SERGEY PAVLOV", "TATIANA SHIROKOVA", "ALEXANDER FROLOV", "ANNA PETROVA",
    "NIKOLAI EGOROV", "MARIA KOVALEVSKAYA", "ANDREY ZINOVIEV", "ELENA LUKINA", "DMITRY ZHUKOV",
    "SVETLANA KULIKOVA", "VLADIMIR ZAKHAROV", "IRINA ZHDANOVA", "ANDREI KUZNETSOV", "EKATERINA PONOMAREVA",
    "DMITRY SOKOLOV", "MARIA SHIROKOVA",
    ]
    return random.choice(names)



# expertise 

def find_duplicates_in_json(json_file_path, tracking):
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        expertise_data = json.load(json_file)

    # Ищем дубликаты
    duplicates = [key for key, value in expertise_data.items()
                  if key != tracking and value[3] == expertise_data[tracking][3] and value[5] == expertise_data[tracking][5]]
    return duplicates


def status_checker(trecing):
    if len(trecing) < 2:
        return 'არასწორი მონაცემების ფორმატი'

    status_type = trecing[0]
    status_detail = trecing[1]

    if status_type == 'გასატანი' and status_detail == 'დაუბეგრავი':
        return 'დაუბეგრავი!'
    elif status_type == 'გასატანი' and status_detail == 'დაბეგვრადი':
        return 'დაბეგვრადი დასრულებული!'
    elif status_type == 'დასადეკლარირებელი' and status_detail == 'დაბეგვრადი':
        return 'დაბეგვრადი! არ არის მზად!'
    elif status_detail == 'გაურკვეველი':
        return 'ყვითელი!'
    else:
        return 'ამოუცნობიუ სტატუსი'


def random_quote():
    # Загружаем цитаты из JSON файла
    with open('documents/quotes.json', 'r', encoding='utf-8') as file:
        quotes = json.load(file)['quotes']
    
    # Выбираем случайную цитату
    return random.choice(quotes)







#  добавка проверка пользователей для отправлениия шаблон




def load_data(file_path):
    """Загрузить данные из JSON-файла."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(file_path, data):
    """Сохранить данные в JSON-файл."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def add_record_to_json(file_path, name, sender_phone, recipient, recipient_phone):
    """Добавить запись в JSON-файл, если ее еще нет."""
    # Загрузить текущие данные
    data = load_data(file_path)
    
    # Проверить, существует ли запись
    if name not in data:
        # Добавить новую запись
        data[name] = {
            "sender phone": sender_phone,
            "recipient": recipient,
            "recipient phone": recipient_phone
        }
        # Сохранить обновленные данные
        save_data(file_path, data)
        print(f"Запись для {name} добавлена.")
    else:
        print(f"Запись для {name} уже существует.")