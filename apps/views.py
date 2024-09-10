from flask import render_template
from flask.views import MethodView
from flask_login import login_required
from functions import get_sorted_dates, update_json_file, delete_old_data, clean_old_files, log_error, random_quote  # Импортируйте необходимые функции и модули

class IndexView(MethodView):
    def __init__(self, db, upload_folder):
        self.db = db
        self.upload_folder = upload_folder

    decorators = [login_required]

    def get(self):
        try:
            # Получаем и сортируем даты
            msk_dates, spb_dates = get_sorted_dates(self.db)
            # Обновляем JSON-файл с датами
            update_json_file(msk_dates, spb_dates)
            # Удаляем устаревшие данные
            delete_old_data(self.db)
            # Очищаем старые файлы
            clean_old_files(self.upload_folder)
        except Exception as e:
            # Если произошла ошибка, логируем её
            log_error(e)
        
        # Возвращаем HTML-шаблон с данными для отображения на странице
        return render_template('index.html', msk_dates=msk_dates, spb_dates=spb_dates, quote=random_quote())

# Функция для регистрации маршрутов
def register_index_routes(app, db, upload_folder):
    app.add_url_rule('/', view_func=IndexView.as_view('index', db=db, upload_folder=upload_folder))
