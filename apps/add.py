from flask import render_template, request, jsonify, flash, redirect, url_for
from flask.views import MethodView
from flask_login import login_required, current_user
from functions import get_last_record, generate_new_number, calculate_cost, handle_image, add_record, add_record_to_json, load_data # Ð˜Ð¼Ð¿Ð¾Ñ€Ñ‚Ð¸Ñ€ÑƒÐ¹Ñ‚Ðµ ÑƒÑ‚Ð¸Ð»Ð¸Ñ‚Ñ‹ Ð¸ Ñ„ÑƒÐ½ÐºÑ†Ð¸Ð¸
import json


class AddParcel(MethodView):
    def __init__(self, db, app):
        self.db = db
        self.app = app

    decorators = [login_required]

    def get(self):
        access = ['admin', 'Tbilisi', 'Batumi']
        if current_user.role not in access:
            flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
            return redirect(url_for('index'))

        json_file_path = 'documents/shipment_template.json'  # ÐŸÑƒÑ‚ÑŒ Ðº Ð²Ð°ÑˆÐµÐ¼Ñƒ JSON-Ñ„Ð°Ð¹Ð»Ñƒ

        # Ð—Ð°Ð³Ñ€ÑƒÐ·Ð¸Ñ‚ÑŒ Ð´Ð°Ð½Ð½Ñ‹Ðµ
        records = load_data(json_file_path)

        # ÐŸÐµÑ€ÐµÐ´Ð°Ñ‚ÑŒ Ð´Ð°Ð½Ð½Ñ‹Ðµ Ð² ÑˆÐ°Ð±Ð»Ð¾Ð½
        return render_template('add.html', records=records)

class SaveParcel(MethodView):
    def __init__(self, db, app):
        self.db = db
        self.app = app

    decorators = [login_required]

    def post(self):
        data = request.form.to_dict()
        last_record = get_last_record(self.db)

        new_record = generate_new_number(data, last_record, self.db)
        cost = calculate_cost(request.form.get('payment'), request.form.get('cost'), request.form.get('payment_currency'))
        
        try:
            handle_image(request.files['photo'], new_record, data['currentDateTime'], self.app)
        except Exception as e:
            response_data = {'success': False, 'message': f'ფოტოს შენახვისას დაფიქსირდა შეცდომა: {str(e)}'}
            return jsonify(response_data)
        
        try:
            add_record(new_record, data, cost, self.db, current_user.role)
        except Exception as e:
            response_data = {'success': False, 'message': f'ჩანაწერის შენახვისას დაფიქსირდა შეცდომა: {str(e)}'}
            return jsonify(response_data)
        
        response_data = {
            'success': True,
            'message': f'ამანათი წარმატებით დაემატა! № {new_record}'
        }
        
        # ÐÐ¾Ð²Ñ‹Ð¹ ÐºÐ¾Ð´ Ð´Ð»Ñ Ð´Ð¾Ð±Ð°Ð²Ð»ÐµÐ½Ð¸Ñ Ð·Ð°Ð¿Ð¸ÑÐ¸ Ð² JSON-Ñ„Ð°Ð¹Ð»
        name = data.get('sender', 'Unknown Sender')  # ÐŸÐ¾Ð»ÑƒÑ‡Ð¸Ñ‚ÑŒ Ð¸Ð¼Ñ Ð¾Ñ‚Ð¿Ñ€Ð°Ð²Ð¸Ñ‚ÐµÐ»Ñ
        sender_phone = data.get('sender_phone', 'Unknown Phone')  # ÐŸÐ¾Ð»ÑƒÑ‡Ð¸Ñ‚ÑŒ Ñ‚ÐµÐ»ÐµÑ„Ð¾Ð½ Ð¾Ñ‚Ð¿Ñ€Ð°Ð²Ð¸Ñ‚ÐµÐ»Ñ
        recipient = data.get('recipient', 'Unknown Recipient')  # ÐŸÐ¾Ð»ÑƒÑ‡Ð¸Ñ‚ÑŒ Ð¸Ð¼Ñ Ð¿Ð¾Ð»ÑƒÑ‡Ð°Ñ‚ÐµÐ»Ñ
        recipient_phone = data.get('recipient_phone', 'Unknown Phone')  # ÐŸÐ¾Ð»ÑƒÑ‡Ð¸Ñ‚ÑŒ Ñ‚ÐµÐ»ÐµÑ„Ð¾Ð½ Ð¿Ð¾Ð»ÑƒÑ‡Ð°Ñ‚ÐµÐ»Ñ
        
        json_file_path = 'documents/shipment_template.json'  # ÐŸÑƒÑ‚ÑŒ Ðº Ð²Ð°ÑˆÐµÐ¼Ñƒ JSON-Ñ„Ð°Ð¹Ð»Ñƒ
        add_record_to_json(json_file_path, name, sender_phone, recipient, recipient_phone)


        return jsonify(response_data)


def register_add_routes(app, db):
    app.add_url_rule('/add', view_func=AddParcel.as_view('add', db=db, app=app))
    app.add_url_rule('/saving_a_parcel', view_func=SaveParcel.as_view('saving_a_parcel', db=db, app=app))
