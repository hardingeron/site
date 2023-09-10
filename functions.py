from PIL import Image
from PIL.ExifTags import TAGS
from models import Purcell
import os
from sqlalchemy import func, desc



from PIL import Image
from PIL.ExifTags import TAGS
from sqlalchemy import func
from models import Purcell



#-------------------------- ДЛЯ ОБРАБОТЧИКА /add

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


#-------------------------- ДЛЯ ОБРАБОТЧИКА /add >----> конец <----< ---------------------------------------------------------------



#-------------------------- ДЛЯ ОБРАБОТЧИКА /change

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


#-------------------------- ДЛЯ ОБРАБОТЧИКА /change >----> конец <----< ---------------------------------------------------------------
