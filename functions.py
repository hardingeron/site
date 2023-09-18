from PIL import Image
from PIL.ExifTags import TAGS
from models import Purcell
import os
from sqlalchemy import func, desc



from PIL import Image
from PIL.ExifTags import TAGS
from sqlalchemy import func
from models import Purcell, Booking


#===========================================================================================================================================================
#-------------------------- ДЛЯ ОБРАБОТЧИКА /add
#===========================================================================================================================================================

# Функция для получения последней записи в базе данных
def get_last_record(db):
    # Используем SQLAlchemy для запроса к базе данных
    # Получаем запись с максимальным номером рейса
    # Сортируем по убыванию номера, чтобы получить самую последнюю запись
    return db.session.query(Purcell).filter(
        Purcell.flight == db.session.query(func.max(Purcell.flight)).scalar_subquery()
    ).order_by(Purcell.number.desc()).first()

# Функция для генерации номера и рейса
def generate_number_and_flight(last_record):
    if last_record:
        # Если есть последняя запись, увеличиваем номер на 1
        last = int(last_record.number) + 1
        fl = last_record.flight
    else:
        # Если нет записей, начинаем с номера 1
        last = 1
        fl = False
    return last, fl

# Функция для расчета стоимости
def calculate_cost(payment_type, cost_amount):
    if payment_type == 'paid':
        cost = f"+{cost_amount}"
    elif payment_type == 'not_paid':
        cost = f"-{cost_amount}"
    else:
        cost = f"+{cost_amount}(ბარათით)"
    return cost

# Функция для добавления записи в базу данных
def add_record(form_data, cost, db):
    number = int(form_data['number'])
    flight = form_data['flight']
    
    while True:
        print('1')
        existing_record = Purcell.query.filter_by(number=number, flight=flight).first()
        if existing_record is None:
            break
        number += 1
    
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
        number=number,
        city=form_data['city'],
        flight=flight,
        image=f"static/purcells/{number}-{flight}.jpeg"
    )
    
    # Добавляем запись в сессию и фиксируем изменения в базе данных
    db.session.add(add)
    db.session.commit()
    return number

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



