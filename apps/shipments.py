from flask.views import MethodView
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, send_file
import os
import json
from models import Shipments;
from datetime import datetime;

class ListView(MethodView):
    decorators = [login_required]

    def get(self):
        # 1. Получаем все посылки из БД
        shipments = Shipments.query.order_by(Shipments.id.desc()).all()

        # 2. Загружаем inventory (как у тебя было)
        json_path = os.path.join(os.getcwd(), "documents", "inventory.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                inventory_items = json.load(f)
        except FileNotFoundError:
            inventory_items = []

        # 3. Передаём ВСЁ в шаблон
        return render_template(
            "shipments.html",
            shipments=shipments,
            inventory=inventory_items
        )

# POST обработчик для сохранения данных из модалки
class ShipmentSubmitView(MethodView):
    decorators = [login_required]

    def __init__(self, db):
        self.db = db

    def post(self):
        data = request.get_json()
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        weights = data.get("weightsHidden", "")  # "1.23 5.34 1.23"
        weight_list = [w for w in weights.split() if w.strip()]  # фильтруем пустые строки
        parcels_count = len(weight_list)
        
        if not data:
            return jsonify({"success": False, "message": "Нет данных"}), 400
        try:
            # создаем объект Shipments и заполняем поля
            parcel = Shipments(
                sender_name=data.get("senderName", ""),
                sender_surname=data.get("senderSurname", ""),
                sender_number=data.get("senderPhone", ""),

                recipient_name=data.get("recipientName", ""),
                recipient_surname=data.get("recipientSurname", ""),
                recipient_number=data.get("recipientPhone", ""),
                recipient_passport=data.get("recipientPassport", ""),

                weights=data.get("weightsHidden", ""),
                parcels_count=parcels_count,
                city_to=data.get("parcelCity", ""),
                cargo_cost=data.get("parcelCost", ""),
                address=data.get("parcelAddress", ""),

                description=", ".join(data.get("inventory", [])),  # объединяем массив тегов в строку

                payment_amount=data.get("paymentAmount", 0),
                payment_status=data.get("paymentStatus", ""),
                currency=data.get("currency", ""),
                order_date=datetime.now()  # <-- здесь текущая дата и время
                # sharedRecipient можно сохранить в отдельное поле, если нужно
            )

            self.db.session.add(parcel)
            self.db.session.commit()

            return jsonify({"success": True, "message": "Посылка успешно добавлена"})

        except Exception as e:
            self.db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500


def register_shipments_routes(app, db):
    app.add_url_rule('/shipments', view_func=ListView.as_view('shipments'))
    app.add_url_rule('/shipment_submit', view_func=ShipmentSubmitView.as_view('shipment_submit', db=db))