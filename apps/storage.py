from flask import render_template, request, jsonify, redirect, url_for, flash
from flask.views import MethodView
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from models import Storage
from functions import format_trecing, save_record, validate_input
import asyncio
import threading
from bot import send_location_message



# Функция для запуска асинхронного цикла в отдельном потоке
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Создаём новый асинхронный цикл
loop = asyncio.new_event_loop()

# Запускаем новый поток с асинхронным циклом
t = threading.Thread(target=start_loop, args=(loop,))
t.start()



# Вьюха для отображения страницы хранения посылок
class StorageView(MethodView):
    def __init__(self):
        pass

    decorators = [login_required]

    def get(self):
        access = ['admin', 'Tbilisi']
        if current_user.role not in access:
            flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
            return redirect(url_for('index'))
        
        return render_template('storage.html')

# Вьюха для сохранения новых записей о посылках
class StorageSaveView(MethodView):
    def __init__(self, db):
        self.db = db
    decorators = [login_required]

    def post(self):
        try:
            shelf = request.form.get('shelf')
            trecing = request.form.get('trecing')

            trecing_list = trecing.split()

            if not validate_input(shelf, trecing):
                return jsonify({'success': False, 'message': 'დამატება ვერ მოხერხდა: შეავსეთ მოცემული ველები!'})

            date = datetime.now().date()

            for record in trecing_list:
                formatted_trecing = format_trecing(record)

                try:
                    save_record(shelf, formatted_trecing, date, self.db)
                except SQLAlchemyError:
                    return jsonify({'success': False, 'message': 'დაიკარგა მონაცემთა ბაზასთან კავშირი!'})

            return jsonify({'success': True})  # Убираем last_shelf из ответа
        except Exception:
            return jsonify({'error': 'მოხდა ამოუცნობი შეცდომა.'})

        

# Вьюха для поиска и получения местоположения посылки
class StorageFindView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def post(self):
        trecing = request.form['trecing']
        info = request.form['info']
        # Выполняем поиск посылки в базе данных
        storage = Storage.query.filter_by(trecing=trecing).first()
        if storage:
            location = storage.shelf  # Местоположение посылки
            asyncio.run_coroutine_threadsafe(send_location_message(trecing, location, info, storage.date), loop)
            if info:
                self.db.session.delete(storage)
                self.db.session.commit()
        else:
            location = "ამანათი არ მოიძებნა"
        
        # Возвращаем данные в формате JSON
        return jsonify({'shelf': location})





# Функция регистрации маршрутов
def register_storage_routes(app, db):
    app.add_url_rule('/storage', view_func=StorageView.as_view('storage'))
    app.add_url_rule('/save', view_func=StorageSaveView.as_view('save', db=db))
    app.add_url_rule('/find', view_func=StorageFindView.as_view('find', db=db))


