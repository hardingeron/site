from flask.views import MethodView
from flask import request, redirect, url_for, render_template
from flask_login import login_required
from models import Forms  # Замените на ваш файл с моделями



class EditParcelView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def get(self):
        item_id = request.args.get('id')  # Получаем id из параметра запроса
        data = Forms.query.get(item_id)
        if data is None:
            # Вы можете вернуть страницу с ошибкой, если данных нет
            return "Error: Parcel not found", 404

        # Если данные найдены, рендерим страницу редактирования
        return render_template('list_edit.html', data=data)

    def post(self):
        item_id = request.form.get('id')
        parcel = Forms.query.get(item_id)

        if parcel is None:
            return "Error: Parcel not found", 404

        # Обновляем данные посылки
        parcel.sender_fio = request.form.get('sender_fl').upper()
        parcel.sender_phone = request.form.get('sender_phone')
        parcel.recipient_fio = request.form.get('recipient_fl').upper()
        parcel.recipient_phone = request.form.get('recipient_phone')
        parcel.passport = request.form.get('passport')
        parcel.city = request.form.get('city')
        parcel.comment = request.form.get('comment')
        parcel.price = int(request.form.get('cost'))
        parcel.weights = request.form.get('weights')
        parcel.cost = int(request.form.get('payment'))
        parcel.payment_status = request.form.get('payment_status')
        parcel.currency = request.form.get('payment_currency')
        parcel.address = request.form.get('address')

        self.db.session.commit()  # Сохраняем изменения в базе данных

        # Перенаправляем обратно на нужную страницу
        return redirect(url_for('list', date=request.form.get('date'), where_from=request.form.get('where_from')))


class DeleteParcelView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def post(self):
        item_id = request.form.get('item_id')  # Получаем id из формы
        parcel = Forms.query.get(item_id)  # Находим посылку по ID

        if parcel:  # Если посылка существует, удаляем её
            self.db.session.delete(parcel)
            self.db.session.commit()  # Применяем изменения в базе данных

        # Перенаправляем обратно на нужную страницу после удаления
        return redirect(url_for('list', date=request.form.get('date'), where_from=request.form.get('where_from')))



def register_list_edit_routes(app, db):
    app.add_url_rule('/list_edit_id', view_func=EditParcelView.as_view('list_edit', db=db))
    app.add_url_rule('/list_delete', view_func=DeleteParcelView.as_view('list_delete', db=db))