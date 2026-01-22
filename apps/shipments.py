from flask.views import MethodView
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, send_file
import os
import json
from models import Shipments;
from datetime import datetime;
from decimal import Decimal
from io import BytesIO
import random
from openpyxl import load_workbook
from models import Forms
from functions import random_names
from helper.shipments_helper import weight_list


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
        
        # получаем общий вес и количество посылок
        total_weight, parcels_count = weight_list(data)


        # 🔹 Данные из URL
        date_param = datetime.strptime(data.get("date"), "%d-%m-%Y").date()        # например "01-03-2025"
        where_from_param = data.get("where_from")  # например "Москва"

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
    



class DownloadManifest(MethodView):
    decorators = [login_required]

    def __init__(self, db):
        self.db = db

    def post(self):   # 🔥 ВАЖНО
        data = request.get_json() or {}
        shipment_ids = data.get("shipment_ids", [])

        if not shipment_ids:
            return jsonify({"error": "shipment_ids пуст"}), 400

        # Фильтруем записи в таблице Shipments
        filtered_forms = Shipments.query.filter(
            Shipments.id.in_(shipment_ids)  # 🔹 фильтр по списку ID
        ).all()

        # Загрузка существующего Excel-файла
        try:
            wb = load_workbook('documents/Sample-Form.xlsx')  # Замените 'Sample-Form.xlsx' на имя вашего существующего файла
            ws = wb.active
        except FileNotFoundError:
            # Обработайте ситуацию, когда файл не найден
            return jsonify({"error": "Sample-Form.xlsx not found"}), 404

        # Обработка данных и запись в Excel
        row_num = ws.max_row + 1  # начинаем с новой строки

        for form in filtered_forms:
            weights = [float(weight) for weight in form.weights.split()]
            price_chance = [15, 20, 25, 10]
            count = 0
            price = random.choice(price_chance)
            vl = 'USD'
            if form.sender_name:
                if form.sender_name == 'DAMIR':
                    s_n = random_names()
                else:
                    s_n = f'{form.sender_name} {form.sender_surname}'
            else:
                s_n = random_names()
            purc_count = len(weights)
            
            for weight in weights:
                if purc_count != 1:
                    count += 1
                    if form.city_from == 'Москва':
                        number = f'{form.city_to}     {form.shipment_number}/{count}'
                    else:
                        number = f'{form.city_to}    0{form.shipment_number}/{count}'
                else:
                    if form.city_from == 'Москва':
                        number = f'{form.city_to}     {form.shipment_number}'
                    else:
                        number = f'{form.city_to}    0{form.shipment_number}'
                # Добавляем данные в соответствующие столбцы
                ws.cell(row=row_num, column=1, value=s_n.split()[0])  # Имя отправителя
                ws.cell(row=row_num, column=2, value=s_n.split()[-1])  # Фамилия отправителя
                ws.cell(row=row_num, column=3, value='Russian Federation')
                if form.city_from == 'Москва':
                    ws.cell(row=row_num, column=4, value='MOSCOW')
                else:
                    ws.cell(row=row_num, column=4, value='S.P.B')
                ws.cell(row=row_num, column=5, value=form.recipient_name)  # Имя получателя
                ws.cell(row=row_num, column=6, value=form.recipient_surname)  # Фамилия получателя
                ws.cell(row=row_num, column=7, value=form.recipient_passport)
                ws.cell(row=row_num, column=8, value='Georgia')
                ws.cell(row=row_num, column=9, value=number)
                ws.cell(row=row_num, column=10, value=form.city_to)
                ws.cell(row=row_num, column=11, value=form.recipient_number)
                ws.cell(row=row_num, column=12, value=price)
                ws.cell(row=row_num, column=13, value=vl)
                ws.cell(row=row_num, column=14, value=weight)  # Значение веса

                row_num += 1  # Переходим к следующей строке

       # Сохраняем изменения в оперативной памяти (BytesIO)
        output = BytesIO()
        wb.save(output)
        wb.close()
        output.seek(0)  # Возвращаемся в начало буфера

        # Возврат файла для скачивания
        return send_file(output, as_attachment=True, download_name='manifest.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def register_shipments_routes(app, db):
    app.add_url_rule('/shipments', view_func=ListView.as_view('shipments'))
    app.add_url_rule('/shipment_submit', view_func=ShipmentSubmitView.as_view('shipment_submit', db=db))
    app.add_url_rule('/export_shipments', view_func=ExportShipmentsView.as_view('export_shipments', db=db))
    app.add_url_rule('/download_manifest', view_func=DownloadManifest.as_view('download_manifest', db=db))