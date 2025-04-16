from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import timedelta
from flask_login import login_required, logout_user, current_user
import os 
import uuid
import tempfile

from flask import send_file
from io import BytesIO
from fpdf import FPDF
import qrcode

from datetime import datetime
from werkzeug.utils import secure_filename
from models import db, login_manager, Forms, Temporarylink, Temporaryparcel
from config import secret_key, db_url_key
from functions import get_reservation_data
from apps.auth import register_auth_routes  # Импорт маршрутов авторизации
from apps.views import register_index_routes  # Импортируйте функцию регистрации маршрутов
from apps.all import register_all_routes
from apps.documents import register_documents_routes
from apps.add import register_add_routes
from apps.storage import register_storage_routes
from apps.image_list import register_image_routes
from apps.reservation import register_reservation_routes
from apps.list import register_list_routes
from apps.list_edit import register_list_edit_routes
from apps.expertise import register_expertise_routes
from apps.feedback import register_feedback_routes
from apps.parcel_delivery import register_parcel_delivery_routes
from apps.analysis import register_analysis_routes

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = db_url_key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключает отслеживание изменений
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=8)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/purcells')
app.config['SECRET_KEY'] = secret_key
UPLOAD_INVOICE = os.path.join(os.getcwd(), 'documents', 'invoice')
os.makedirs(UPLOAD_INVOICE, exist_ok=True)
app.config['UPLOAD_INVOICE'] = UPLOAD_INVOICE

app.config.from_object(__name__)

db.init_app(app)

login_manager.init_app(app)
login_manager.login_view = 'login'




#-------------------------------------------------------------------------------------------------#
# ------------------------------               /login               ------------------------------#
register_auth_routes(app)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /index               ------------------------------#
register_index_routes(app, db, app.config['UPLOAD_FOLDER'])
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /all                 ------------------------------#
register_all_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /documents           ------------------------------#
register_documents_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /add                 ------------------------------#
register_add_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /storage             ------------------------------#
register_storage_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /images_list         ------------------------------#
register_image_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /reservation         ------------------------------#
register_reservation_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /Feedback            ------------------------------#
register_feedback_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /parcel_delivery     ------------------------------#
register_parcel_delivery_routes(app, db)



@app.route('/reservation_big', methods=['POST', 'GET'])
@login_required
def reservation_big():
    access = ['admin', 'Tbilisi', 'Moscow']
    if current_user.role not in access:
        flash('თქვენ არ გაქვთ წვდომა ამ გვერდზე', 'error')
        return redirect(url_for('index'))
    selected_date = request.args.get('date')
    reis = request.args.get('route')
    reservation_data = get_reservation_data(selected_date, reis, 59)
    return render_template('reservation_big.html', **reservation_data)


@app.route('/generate-link', methods=['POST'])
@login_required
def generate_link():
    token = str(uuid.uuid4())
    link = Temporarylink(token=token)
    db.session.add(link)
    db.session.commit()

    full_url = request.host_url + 'form/' + token
    return jsonify({'link': full_url})



@app.route('/form/<token>', methods=['GET', 'POST'])
def form_page(token):
    link = Temporarylink.query.filter_by(token=token).first()

    if not link or link.is_expired():
        if link:
            db.session.delete(link)
            db.session.commit()
        return "Срок действия ссылки истёк", 403

    if request.method == 'POST':
        # Обработка данных и сохранение в БД
        link.is_active = False
        db.session.commit()
        return "Данные успешно отправлены"

    return render_template('form.html', token=token)


@app.route('/submit-parcel', methods=['POST'])
def submit_parcel():
    # Получаем токен из формы
    token = request.form.get('token')
    link = Temporarylink.query.filter_by(token=token).first()

    # Проверка на существование, срок действия и активность
    if not link or link.is_expired() or not link.is_active:
        return jsonify({'status': 'danger', 'message': 'Ссылка недействительна или уже использована.'})

    # Получаем данные из формы
    sender_first_name = request.form['sender_first_name']
    sender_last_name = request.form['sender_last_name']
    sender_phone = request.form['sender_phone']
    sender_passport = request.form['sender_passport']

    recipient_first_name = request.form['recipient_first_name']
    recipient_last_name = request.form['recipient_last_name']
    recipient_phone = request.form['recipient_phone']
    recipient_passport = request.form['recipient_passport']

    city = request.form['city']
    description = request.form['description']

    # Работа с PDF файлом
    invoice = request.files['invoice']
    invoice_path = "empty"

    if invoice and invoice.filename.endswith('.pdf'):
        now = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{sender_first_name}-{sender_last_name}-{now}.pdf"
        filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_INVOICE'], filename)
        invoice.save(file_path)
        invoice_path = f"documents/invoice/{filename}"

    # Сохраняем данные в БД
    parcel = Temporaryparcel(
        sender_first_name=sender_first_name,
        sender_last_name=sender_last_name,
        sender_phone=sender_phone,
        sender_passport=sender_passport,
        recipient_first_name=recipient_first_name,
        recipient_last_name=recipient_last_name,
        recipient_phone=recipient_phone,
        recipient_passport=recipient_passport,
        city=city,
        description=description,
        invoice_path=invoice_path,
    )
    db.session.add(parcel)
    db.session.commit()  # Сохраняем данные в базе данных

    # Получаем tracking_number из только что сохраненной записи
    tracking_number = parcel.tracking_number  # Предполагаем, что tracking_number уже сгенерирован и сохранен в базе данных

    # Деактивируем ссылку
    link.is_active = False
    db.session.commit()

    # Отправляем ответ с tracking_number
    return jsonify({'status': 'success', 'message': f'Заявка успешно отправлена! Вот ваш номер отслеживания: {tracking_number}'})


@app.route('/get-tracking-data')
@login_required
def get_tracking_data():
    tracking_number = request.args.get('tracking_number')

    if not tracking_number:
        return jsonify({'success': False, 'error': 'Tracking number not provided'})

    record = Temporaryparcel.query.filter_by(tracking_number=tracking_number).first()

    if not record:
        return jsonify({'success': False, 'error': 'Record not found'})

    return jsonify({
        'success': True,
        'sender_first_name': record.sender_first_name,
        'sender_last_name': record.sender_last_name,
        'sender_phone': record.sender_phone,
        'sender_passport': record.sender_passport,
        'recipient_first_name': record.recipient_first_name,
        'recipient_last_name': record.recipient_last_name,
        'recipient_phone': record.recipient_phone,
        'recipient_passport': record.recipient_passport,
        'city': record.city,
        'description': record.description
    })


#-------------------------------------------------------------------------------------------------#
# ------------------------------               /list                ------------------------------#
register_list_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /list_edit           ------------------------------#
register_list_edit_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               /expertise           ------------------------------#
register_expertise_routes(app, db)
#-------------------------------------------------------------------------------------------------#
# ------------------------------               other                ------------------------------#
register_analysis_routes(app, db)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# @app.teardown_request
# def teardown_request(exception=None):
#     db.session.close()


@app.teardown_request
def teardown_request(exception=None):
    db.session.remove()

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', message='Страница не найдена'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message='Внутренняя ошибка сервера'), 500



    


@app.route("/generate_qr/<int:form_id>")
@login_required
def generate_qr(form_id):
    form = Forms.query.get_or_404(form_id)

    # Получаем список весов
    weights = form.weights.split()  # Предположим, что веса разделены пробелами

    # Преобразуем строки в числа и суммируем
    total_weight = 0
    for weight in weights:
        try:
            total_weight += float(weight)
        except ValueError:
            continue  # Пропускаем некорректные записи

    # Получаем количество посылок
    total_parcels = len(weights)

    qr_text = f"""
    Отправитель: {form.sender_fio}
    Телефон отправителя: {form.sender_phone}
    Паспорт отправителя: {form.sender_passport}

    Получатель: {form.recipient_fio}
    Телефон получателя: {form.recipient_phone}
    Паспорт получателя: {form.passport}

    Город: {form.city}
    Описание: {form.comment}

    Количество посылок: {total_parcels}
    Общий вес: {total_weight:.2f} кг
    """.strip()

    # Генерируем QR-код
    qr_img = qrcode.make(qr_text)

    # Сохраняем во временный файл
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        qr_img.save(tmp)
        tmp_path = tmp.name

    # Используем fpdf2 для создания PDF
    pdf = FPDF()
    pdf.add_page()

    # Добавляем изображение QR-кода
    pdf.image(tmp_path, x=60, y=pdf.get_y() + 10, w=90)

    # Сохраняем PDF в память
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(
        pdf_output,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"QR_Form_{form_id}.pdf"
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


