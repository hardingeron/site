from flask.views import MethodView
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash, request, jsonify
import json
from datetime import datetime

class FeedbackView(MethodView):
    def __init__(self):
        pass

    decorators = [login_required]

    def get(self):

        json_file_path = 'documents/feedback_list.json'
        feedback_list = load_data(json_file_path)


        return render_template('feedback.html', feedback_list=feedback_list)

class FeedbackSubmitView(MethodView):
    def __init__(self):
        pass

    decorators = [login_required]

    def post(self):
        page = request.form['page']  # Получаем выбранную страницу
        feedback = request.form['feedback']  # Получаем текст фидбека
        print(f"Feedback received for {page}: {feedback}")

        json_file_path = 'documents/feedback_list.json'

        # Загружаем существующие данные
        feedback_list = load_data(json_file_path)

        # Текущая дата и время
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Создаем новую запись фидбека
        feedback_data = {
            "page": page,
            "idea": feedback,
            "user": current_user.role,  # Используем имя пользователя
            "approval": ""  # Поле для одобрения остается пустым
        }

        # Добавляем новую запись в структуру данных
        feedback_list[timestamp] = feedback_data

        # Сохраняем обновленные данные в файл
        save_data(json_file_path, feedback_list)

        # Вернуть ответ пользователю
        return redirect(url_for('feedback'))



def save_data(file_path, data):
    """Сохранить данные в JSON-файл."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)





def load_data(file_path):
    """Загрузить данные из JSON-файла с указанием кодировки utf-8."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        return {}
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return {}





def register_feedback_routes(app, db):
    app.add_url_rule('/feedback', view_func=FeedbackView.as_view('feedback'))
    app.add_url_rule('/submit_feedback', view_func=FeedbackSubmitView.as_view('submit_feedback'))