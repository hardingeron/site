from flask import request, flash, redirect, url_for, render_template, jsonify
from flask_login import login_required, current_user
from flask.views import MethodView
import random
from datetime import datetime
from sqlalchemy import func
from models import Forms, Purcell
from sqlalchemy.sql import extract
import re


class AnalysisRoute(MethodView):
    def __init__(self):
        pass


    decorators = [login_required]

    def get(self):
        access = ['admin', 'Tbilisi', 'Moscow']
        if current_user.role not in access:
            flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
            return redirect(url_for('index'))
        return render_template('analysis.html')
    

class AnalysisBatumi(MethodView):
    decorators = [login_required]

    def post(self):
        # Получаем текущий год
        current_year = datetime.now().year

        # Получаем все записи из базы данных за текущий год
        records = Forms.query.filter(func.year(func.str_to_date(Forms.date, '%d-%m-%Y')) == current_year, Forms.city == 'BATUMI').all()
        print(records)

        # Месяцы
        months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]

        # Словари для хранения данных по месяцам
        monthly_data = {month: {"weight": 0, "packages": 0, "profit_lari": 0, "profit_rub": 0} for month in months}

        # Обрабатываем каждую запись
        for record in records:
            # Извлекаем месяц из даты
            month = record.date.split('-')[1]  # Получаем месяц (например, из 20-06-2025 получаем 06)
            month_name = months[int(month) - 1]  # Получаем название месяца

            # Шаг 2: Суммируем вес
            monthly_data[month_name]["weight"] += sum(map(float, record.weights.split()))

            # Шаг 3: Считаем количество пакетов (записей)
            monthly_data[month_name]["packages"] += 1

            # Шаг 4: Суммируем profit_lari, если валюта GEL
            if record.currency == 'GEL':
                monthly_data[month_name]["profit_lari"] += record.cost

            # Шаг 5: Суммируем profit_rub, если валюта RUB
            if record.currency == 'RUB':
                monthly_data[month_name]["profit_rub"] += record.cost


        # Формируем итоговый ответ
        return jsonify({
            "months": months,
            "weight": [monthly_data[month]["weight"] for month in months],
            "packages": [monthly_data[month]["packages"] for month in months],
            "profit_lari": [monthly_data[month]["profit_lari"] for month in months],
            "profit_rub": [monthly_data[month]["profit_rub"] for month in months],
        })
    

class AnalysisTbilisi(MethodView):
    decorators = [login_required]

    def post(self):
        # Получаем текущий год
        current_year = datetime.now().year

        # Получаем все записи из базы данных за текущий год
        records = Forms.query.filter(func.year(func.str_to_date(Forms.date, '%d-%m-%Y')) == current_year, Forms.city == 'TBILISI').all()
        print(records)
        # Месяцы
        months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]

        # Словари для хранения данных по месяцам
        monthly_data = {month: {"weight": 0, "packages": 0, "profit_lari": 0, "profit_rub": 0} for month in months}

        # Обрабатываем каждую запись
        for record in records:
            # Извлекаем месяц из даты
            month = record.date.split('-')[1]  # Получаем месяц (например, из 20-06-2025 получаем 06)
            month_name = months[int(month) - 1]  # Получаем название месяца

            # Шаг 2: Суммируем вес
            monthly_data[month_name]["weight"] += sum(map(float, record.weights.split()))

            # Шаг 3: Считаем количество пакетов (записей)
            monthly_data[month_name]["packages"] += 1

            # Шаг 4: Суммируем profit_lari, если валюта GEL
            if record.currency == 'GEL':
                monthly_data[month_name]["profit_lari"] += record.cost

            # Шаг 5: Суммируем profit_rub, если валюта RUB
            if record.currency == 'RUB':
                monthly_data[month_name]["profit_rub"] += record.cost


        # Формируем итоговый ответ
        return jsonify({
            "months": months,
            "weight": [monthly_data[month]["weight"] for month in months],
            "packages": [monthly_data[month]["packages"] for month in months],
            "profit_lari": [monthly_data[month]["profit_lari"] for month in months],
            "profit_rub": [monthly_data[month]["profit_rub"] for month in months],
        })


class AnalysisSPB(MethodView):
    decorators = [login_required]

    def post(self):
        print('Запрос на анализ Санкт-Петербурга')

        current_year = datetime.now().year

        # Получаем записи за текущий год
        records = Purcell.query.filter(
            extract('year', Purcell.date) == current_year,
            Purcell.city == 'S.P.B'
        ).all()

        # Месяцы
        months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]

        # Подготовка данных
        monthly_data = {month: {"weight": 0, "packages": 0, "profit_lari": 0, "profit_rub": 0} for month in months}

        for record in records:
            month = record.date.month  # Получаем номер месяца (1-12)
            month_name = months[month - 1]  # Преобразуем в название

            # Вес (конвертируем в число)
            try:
                monthly_data[month_name]["weight"] += float(record.weight)
            except (ValueError, TypeError) as e:
                print(f"Ошибка при обработке веса: {e}, данные: {record.weight}")

            # Количество посылок
            monthly_data[month_name]["packages"] += 1


            pattern = r'(\d+\.?\d*)\s*(GEL|RUB)'
            match = re.search(pattern, record.cost)
            if match:
                amount = float(match.group(1))  # Число
                currency = match.group(2)  # Валюта

                # Добавляем в нужную категорию
                if currency == 'GEL':
                    monthly_data[month_name]["profit_lari"] += amount
                elif currency == 'RUB':
                    monthly_data[month_name]["profit_rub"] += amount

        return jsonify({
            "months": months,
            "weight": [monthly_data[month]["weight"] for month in months],
            "packages": [monthly_data[month]["packages"] for month in months],
            "profit_lari": [monthly_data[month]["profit_lari"] for month in months],
            "profit_rub": [monthly_data[month]["profit_rub"] for month in months],
        })



class AnalysisMoscow(MethodView):
    decorators = [login_required]

    def post(self):
        print('Запрос на анализ Москвы')

        current_year = datetime.now().year

        # Получаем записи за текущий год для Москвы
        records = Purcell.query.filter(
            extract('year', Purcell.date) == current_year,
            Purcell.city == 'Moscow'
        ).all()

        # Месяцы
        months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]

        # Подготовка данных
        monthly_data = {month: {"weight": 0, "packages": 0, "profit_lari": 0, "profit_rub": 0} for month in months}

        for record in records:
            month = record.date.month  # Получаем номер месяца (1-12)
            month_name = months[month - 1]  # Преобразуем в название

            # Вес (конвертируем в число)
            try:
                monthly_data[month_name]["weight"] += float(record.weight)
            except (ValueError, TypeError) as e:
                print(f"Ошибка при обработке веса: {e}, данные: {record.weight}")

            # Количество посылок
            monthly_data[month_name]["packages"] += 1

            pattern = r'(\d+\.?\d*)\s*(GEL|RUB)'
            match = re.search(pattern, record.cost)
            if match:
                amount = float(match.group(1))  # Число
                currency = match.group(2)  # Валюта

                # Добавляем в нужную категорию
                if currency == 'GEL':
                    monthly_data[month_name]["profit_lari"] += amount
                elif currency == 'RUB':
                    monthly_data[month_name]["profit_rub"] += amount

        return jsonify({
            "months": months,
            "weight": [monthly_data[month]["weight"] for month in months],
            "packages": [monthly_data[month]["packages"] for month in months],
            "profit_lari": [monthly_data[month]["profit_lari"] for month in months],
            "profit_rub": [monthly_data[month]["profit_rub"] for month in months],
        })

def register_analysis_routes(app, db):
    app.add_url_rule('/analysis', view_func=AnalysisRoute.as_view('analysis'))
    app.add_url_rule('/batumi_data', view_func=AnalysisBatumi.as_view('batumi_data'))
    app.add_url_rule('/tbilisi_data', view_func=AnalysisTbilisi.as_view('tbilisi_data'))
    app.add_url_rule('/spb_data', view_func=AnalysisSPB.as_view('spb_data'))
    app.add_url_rule('/moscow_data', view_func=AnalysisMoscow.as_view('moscow_data'))