from flask.views import MethodView
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, send_file
import os
import json

class ListView(MethodView):
    decorators = [login_required]

    def get(self):
        # Определяем путь к JSON файлу
        json_path = os.path.join(os.getcwd(), "documents", "inventory.json")
        
        # Читаем JSON
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                inventory_items = json.load(f)
        except FileNotFoundError:
            inventory_items = []  # если файл не найден — пустой список

        # Передаём данные в шаблон
        return render_template("shipments.html", inventory=inventory_items)



def register_shipments_routes(app, db):
    app.add_url_rule('/shipments', view_func=ListView.as_view('shipments'))