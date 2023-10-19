from PIL import Image
from PIL.ExifTags import TAGS
from models import Purcell
import os
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json



from PIL import Image
from PIL.ExifTags import TAGS
from sqlalchemy import func
from models import Purcell, Booking, Storage, Forms




#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА /add
#===========================================================================================================================================================

# Функция для получения последней записи в базе данных
def get_last_record(selected_date, db): 
    last_record = db.session.query(Purcell).filter(Purcell.flight == selected_date).order_by(Purcell.number.desc()).first()
    if last_record:
        number = last_record.number
    else:
        number = 1
    return number

def generate_new_number(date, number):
    while True:
        existing_record = Purcell.query.filter_by(number=int(number), flight=date).first()
        if existing_record is None:
            break
        number += 1
    return number


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
def add_record(last, form_data, cost, db, user_role):
    date = form_data['date']
    
    try:
        add = Purcell(
            sender=form_data['sender'].upper(),
            sender_phone=form_data['sender_phone'],
            recipient=form_data['recipient'].upper(),
            recipient_phone=form_data['recipient_phone'],
            inventory=form_data['inventory'].replace('\n', ' ').replace('\r', ' '),
            cost=cost,
            passport=form_data['passport'],
            weight=form_data['weight'].upper(),
            responsibility=form_data['responsibility'].upper(),
            number=last,
            city=form_data['city'],
            flight=date,
            image=f"static/purcells/{last}-{date}.jpeg",
            where_from=user_role
        )
        
        # Добавляем запись в сессию и фиксируем изменения в базе данных
        db.session.add(add)
        db.session.commit()
        
        return last
    except Exception as e:
        # Обработка ошибки и возвращение сообщения об ошибке
        return f"Ошибка при сохранении записи: {str(e)}"


# Функция для обработки изображения
def handle_image(file, number, flight, app):
    filename = f"{number}-{flight}.jpeg"
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
def handle_uploaded_image(file, number, flight, app):
    # Формирование имени файла на основе номера и рейса
    filename = f"{number}-{flight}.jpeg"
    
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
            elif payment_value.endswith('USD'):
                sum_usd += float(payment_value[:-3])  # Убираем "USD" и преобразуем в число
            elif payment_value.endswith('EUR'):
                sum_eur += float(payment_value[:-3])  # Убираем "EUR" и преобразуем в число

        elif payment_value.startswith('C'):
            payment_value = payment_value[1:]  # Убираем начальный символ "C"
            
            if payment_value.endswith('GEL'):
                sum_card_gel += float(payment_value[:-3])  # Убираем "GEL" и преобразуем в число
            elif payment_value.endswith('RUB'):
                sum_card_rub += float(payment_value[:-3])  # Убираем "RUB" и преобразуем в число
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
            'action': booking.action

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
        'came_of_count_free': came_of_count_free
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
    unique_dates_cities = db.session.query(Forms.date, Forms.where_from).filter(Forms.date.isnot(None)).distinct()

    # Списки для дат Москвы и Санкт-Петербурга
    msk_dates = []
    spb_dates = []

    # Разбираем полученные даты и города
    for date, city in unique_dates_cities:
        if city == 'Москва':
            msk_dates.append(date)
        elif city == 'Санкт-Петербург':
            spb_dates.append(date)

    # Сортировка дат по убыванию (от новых к старым)
    msk_dates.sort(key=lambda x: datetime.strptime(x, '%d-%m-%Y'), reverse=True)
    spb_dates.sort(key=lambda x: datetime.strptime(x, '%d-%m-%Y'), reverse=True)

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
    delta = timedelta(days=90)
    date_threshold = today - delta

    # Попытка удаления старых данных из базы данных
    old_data = Purcell.query.filter(Purcell.flight < date_threshold).delete()
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
            if file_extension in [".jpeg", ".jpg", ".png"] and days_since_modification > 90:
                os.remove(file_path)



#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА />----> конец <----< ---------------------------------------------------------------
#===========================================================================================================================================================






#===========================================================================================================================================================
#-------------------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
#===========================================================================================================================================================

def log_error(error):
    # Здесь вы можете добавить логику логирования ошибок, например, в файл, базу данных или на сервер
    print(f"An error occurred: {error}")


#===========================================================================================================================================================
#-------------------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ >----> конец <----< ---------------------------------------------------------------
#===========================================================================================================================================================
