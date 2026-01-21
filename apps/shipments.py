from flask.views import MethodView
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, send_file
import os
import json
from models import Shipments;
from datetime import datetime;
from decimal import Decimal

class ListView(MethodView):
    decorators = [login_required]

    def get(self):
        date_param = datetime.strptime(request.args.get('date'), "%d-%m-%Y").date() 
        city_param = request.args.get('where_from')  # Получите значение параметра "city"

        # 1. Получаем все посылки из БД
        shipments = (Shipments.query.filter_by(send_date=date_param,city_from=city_param).order_by(Shipments.id.desc()).all())

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
        weights = data.get("weightsHidden", "")  # "1.23 5.34 1.23"
        weight_list = [w for w in weights.split() if w.strip()]  # фильтруем пустые строки
        parcels_count = len(weight_list)
        total_weight = sum(Decimal(w) for w in weight_list)


        # 🔹 Данные из URL
        date_param = datetime.strptime(data.get("date"), "%d-%m-%Y").date()        # например "01-03-2025"
        where_from_param = data.get("where_from")  # например "Москва"
        # datetime.strptime(data.get("date"), "%d-%m-%Y").date()
        last_shipment = (
        Shipments.query.filter(Shipments.send_date == date_param,Shipments.city_from == where_from_param).order_by(Shipments.shipment_number.desc()).first())
        if last_shipment is None:
            shipment_number = 1
        else:
            shipment_number = last_shipment.shipment_number + 1

        print("Дата из URL:", date_param)
        print("Город отправки из URL:", where_from_param)

        shared_recipient = data.get("sharedRecipient")  # True или False
        if shared_recipient:
            payment_amount = 0
            payment_status = "+"
            sequence = 1
        else:
            payment_amount = data.get("paymentAmount", 0)
            payment_status = data.get("paymentStatus", "")
            sequence = 0

        inventory = data.get("inventory", [])
        clean_inventory = [
            item.replace("×", "").strip()
            for item in inventory
                            ]

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
                total_weight=total_weight,
                parcels_count=parcels_count,
                city_to=data.get("parcelCity", ""),
                cargo_cost=data.get("parcelCost", ""),
                address=data.get("parcelAddress", ""),
                shipment_number=shipment_number,
                city_from=where_from_param,
                send_date=date_param,

                description = ", ".join(clean_inventory),

                payment_amount=payment_amount,
                payment_status=payment_status,
                currency=data.get("currency", ""),
                order_date=datetime.now(),  # <-- здесь текущая дата и время
                sequence=sequence
                # sharedRecipient можно сохранить в отдельное поле, если нужно
            )

            self.db.session.add(parcel)
            self.db.session.commit()

            return jsonify({"success": True, "message": "Посылка успешно добавлена"})

        except Exception as e:
            self.db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500


class ExportShipmentsView(MethodView):
    decorators = [login_required]

    def __init__(self, db):
        self.db = db

    def post(self):
        data = request.get_json()
        shipment_ids = data.get("shipment_ids", [])
        print(shipment_ids)

        return jsonify({"status": "ok"})

def register_shipments_routes(app, db):
    app.add_url_rule('/shipments', view_func=ListView.as_view('shipments'))
    app.add_url_rule('/shipment_submit', view_func=ShipmentSubmitView.as_view('shipment_submit', db=db))
    app.add_url_rule('/export_shipments', view_func=ExportShipmentsView.as_view('export_shipments', db=db))