# views.py
from flask import render_template, request, jsonify, send_file
from flask.views import MethodView
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os
import re
from PIL import Image, ImageFilter, ImageOps
from functions import handle_uploaded_image, edit_parcel_, log_error  # Ð˜Ð¼Ð¿Ð¾Ñ€Ñ‚Ð¸Ñ€ÑƒÐ¹Ñ‚Ðµ Ð½ÐµÐ¾Ð±Ñ…Ð¾Ð´Ð¸Ð¼Ñ‹Ðµ Ñ„ÑƒÐ½ÐºÑ†Ð¸Ð¸
from models import Purcell  # Ð˜Ð¼Ð¿Ð¾Ñ€Ñ‚Ð¸Ñ€ÑƒÐ¹Ñ‚Ðµ Ð¼Ð¾Ð´ÐµÐ»Ð¸

class AllView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def get(self):
        try:
            # ÐŸÐ¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ Ñ‚ÐµÐºÑƒÑ‰ÑƒÑŽ Ð´Ð°Ñ‚Ñƒ
            today = datetime.now().date()
            delta = timedelta(days=60)
            date_threshold = today - delta

            # ÐŸÐ¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ Ð´Ð°Ð½Ð½Ñ‹Ðµ Ð´Ð»Ñ Ð¾Ñ‚Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ñ, Ð¾Ñ‚ÑÐ¾Ñ€Ñ‚Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð½Ñ‹Ðµ Ð¿Ð¾ Ð´Ð°Ñ‚Ðµ Ð¸ Ð½Ð¾Ð¼ÐµÑ€Ñƒ
            all_data = list(reversed(self.db.session.query(Purcell).filter(Purcell.date >= date_threshold)
                             .order_by(Purcell.date.asc(), Purcell.number.asc())
                             .all()))

            # ÐŸÐ¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ Ð´Ð°Ñ‚Ñ‹ Ð¿Ð¾ÑÐ»ÐµÐ´Ð½Ð¸Ñ… 10 Ñ€ÐµÐ¹ÑÐ¾Ð² Ð´Ð»Ñ Ð¾Ñ‚Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ñ Ð¸Ð· ÑƒÐ¶Ðµ Ð¿Ð¾Ð»ÑƒÑ‡ÐµÐ½Ð½Ñ‹Ñ… Ð´Ð°Ð½Ð½Ñ‹Ñ…
            last_10_flights = list(set(row.flight for row in all_data))[:10]

            # ÐžÑ‚Ð¾Ð±Ñ€Ð°Ð¶Ð°ÐµÐ¼ ÑˆÐ°Ð±Ð»Ð¾Ð½ ÑÑ‚Ñ€Ð°Ð½Ð¸Ñ†Ñ‹ 'all.html' Ñ Ð´Ð°Ð½Ð½Ñ‹Ð¼Ð¸
            return render_template('all.html', all_data=all_data, last_10_flights=last_10_flights)
        except Exception as e:
            log_error(e)
            return jsonify({'success': False, 'message': 'ÐžÑˆÐ¸Ð±ÐºÐ° Ð¿Ñ€Ð¸ Ð¾Ð±Ñ€Ð°Ð±Ð¾Ñ‚ÐºÐµ Ð·Ð°Ð¿Ñ€Ð¾ÑÐ°'}), 500

def _normalize_city(value):
    aliases = {
        'moscow': 'Moscow',
        'Ð¼Ð¾ÑÐºÐ²Ð°': 'Moscow',
        'spb': 'S.P.B',
        's.p.b': 'S.P.B',
        's.p.b.': 'S.P.B',
        'ÑÐ°Ð½ÐºÑ‚-Ð¿ÐµÑ‚ÐµÑ€Ð±ÑƒÑ€Ð³': 'S.P.B',
        'saint-petersburg': 'S.P.B',
        'saint petersburg': 'S.P.B',
    }
    cleaned = (value or '').strip()
    return aliases.get(cleaned.lower(), cleaned)


def _parse_date(value, end_of_day=False):
    if not value:
        return None

    for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y'):
        try:
            parsed = datetime.strptime(value, fmt)
            if end_of_day and fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y'):
                parsed = parsed.replace(hour=23, minute=59, second=59, microsecond=999999)
            return parsed
        except ValueError:
            continue
    return None


def _money_parts(value):
    text = str(value or '').upper()
    match = re.search(r'([+-]?)\s*([0-9]+(?:[.,][0-9]+)?)\s*(GEL|RUB|USD|EUR)?', text)
    if not match:
        return None

    currency = match.group(3) or 'UNKNOWN'
    if currency == 'UNKNOWN':
        if 'LARI' in text or 'Ð›ÐÐ ' in text:
            currency = 'GEL'
        elif 'RUR' in text or 'Ð Ð£Ð‘' in text:
            currency = 'RUB'

    return {
        'sign': match.group(1) or '',
        'amount': float(match.group(2).replace(',', '.')),
        'currency': currency,
        'is_card': '\U0001f4b3' in str(value or ''),
        'is_due': (match.group(1) or '') == '-',
    }


def _parse_weight(value):
    match = re.search(r'([0-9]+(?:[.,][0-9]+)?)', str(value or ''))
    return float(match.group(1).replace(',', '.')) if match else 0


def _image_url(record):
    image = (record.image or '').replace('\\', '/').strip()
    if not image:
        return '/static/images/not_found.jpeg'
    if image.startswith('/'):
        return image
    return '/' + image


def _format_flight_date(value, fallback=''):
    text = str(value or '').strip()
    if not text:
        return fallback

    for fmt in ('%d.%m.%Y %H.%M.%S', '%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H.%M', '%d.%m.%Y %H:%M'):
        try:
            return datetime.strptime(text, fmt).strftime('%d.%m.%Y %H:%M')
        except ValueError:
            continue

    return text


def _serialize_parcel(record):
    parts = _money_parts(record.cost)
    date_label = record.date.strftime('%d.%m.%Y %H:%M') if record.date else ''
    order_label = _format_flight_date(record.flight, date_label)
    return {
        'id': record.id,
        'number': record.number or '',
        'sender': record.sender or '',
        'sender_phone': record.sender_phone or '',
        'recipient': record.recipient or '',
        'recipient_phone': record.recipient_phone or '',
        'inventory': record.inventory or '',
        'cost': record.cost or '',
        'passport': record.passport or '',
        'weight': record.weight or '',
        'responsibility': record.responsibility or '',
        'city': record.city or '',
        'where_from': record.where_from or '',
        'flight': record.flight or '',
        'date': record.date.isoformat() if record.date else '',
        'date_label': date_label,
        'order_label': order_label,
        'departure_status': record.departure_status or '',
        'delivery': record.delivery or 'no',
        'image': _image_url(record),
        'thumbnail': f'/all-new/image-thumb/{record.id}',
        'payment_kind': 'due' if parts and parts['is_due'] else 'paid',
        'payment_currency': parts['currency'] if parts else '',
        'payment_amount': parts['amount'] if parts else 0,
        'payment_is_card': bool(parts and parts['is_card']),
    }


def _apply_all_new_filters(query, params):
    destination_city = _normalize_city(params.get('destination_city') or params.get('city'))
    origin_city = _normalize_city(params.get('origin_city') or params.get('where_from') or params.get('sender_city'))
    quick_range = (params.get('range') or '').strip()
    search = (params.get('search') or '').strip()

    if destination_city and destination_city != 'all':
        query = query.filter(Purcell.city.ilike(f'%{destination_city}%'))

    if origin_city and origin_city != 'all':
        query = query.filter(Purcell.where_from.ilike(f'%{origin_city}%'))

    text_filters = {
        'sender': Purcell.sender,
        'sender_phone': Purcell.sender_phone,
        'recipient': Purcell.recipient,
        'recipient_phone': Purcell.recipient_phone,
        'number': Purcell.number,
        'cost': Purcell.cost,
        'weight': Purcell.weight,
        'passport': Purcell.passport,
    }
    for key, column in text_filters.items():
        value = (params.get(key) or '').strip()
        if value:
            query = query.filter(column.ilike(f'%{value}%'))

    if search:
        like = f'%{search}%'
        query = query.filter(
            Purcell.sender.ilike(like) |
            Purcell.sender_phone.ilike(like) |
            Purcell.recipient.ilike(like) |
            Purcell.recipient_phone.ilike(like) |
            Purcell.inventory.ilike(like) |
            Purcell.number.ilike(like) |
            Purcell.city.ilike(like) |
            Purcell.where_from.ilike(like)
        )

    now = datetime.now()
    start = _parse_date(params.get('date_from'))
    end = _parse_date(params.get('date_to'), end_of_day=True)

    if quick_range == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif quick_range == 'week':
        start = now - timedelta(days=7)
        end = now
    elif quick_range == 'month':
        start = now - timedelta(days=30)
        end = now

    if start:
        query = query.filter(Purcell.date >= start)
    if end:
        query = query.filter(Purcell.date <= end)

    payment = (params.get('payment') or '').strip()
    if payment == 'paid':
        query = query.filter(Purcell.cost.startswith('+'))
    elif payment == 'due':
        query = query.filter(Purcell.cost.startswith('-'))

    status = (params.get('status') or '').strip()
    if status == 'issued':
        query = query.filter(Purcell.delivery == 'yes')
    elif status == 'active':
        query = query.filter((Purcell.delivery != 'yes') | (Purcell.delivery.is_(None)))
    elif status == 'ready':
        query = query.filter(Purcell.departure_status == '+')

    return query


def _build_analytics(records):
    analytics = {
        'total': len(records),
        'issued': 0,
        'active': 0,
        'ready': 0,
        'weight': 0,
        'profit_gel': 0,
        'profit_rub': 0,
        'due_gel': 0,
        'due_rub': 0,
        'moscow': 0,
        'spb': 0,
        'tbilisi': 0,
        'batumi': 0,
    }

    for record in records:
        if record.delivery == 'yes':
            analytics['issued'] += 1
        else:
            analytics['active'] += 1

        if record.departure_status == '+':
            analytics['ready'] += 1

        analytics['weight'] += _parse_weight(record.weight)

        destination_city = (record.city or '').lower()
        origin_city = (record.where_from or '').lower()
        if 'moscow' in destination_city or 'москва' in destination_city:
            analytics['moscow'] += 1
        if 's.p.b' in destination_city or 'spb' in destination_city or 'петер' in destination_city:
            analytics['spb'] += 1
        if 'tbilisi' in origin_city or 'თბილისი' in origin_city:
            analytics['tbilisi'] += 1
        if 'batumi' in origin_city or 'ბათუმი' in origin_city:
            analytics['batumi'] += 1

        parts = _money_parts(record.cost)
        if not parts:
            continue

        key = None
        if parts['currency'] == 'GEL':
            key = 'due_gel' if parts['is_due'] else 'profit_gel'
        elif parts['currency'] == 'RUB':
            key = 'due_rub' if parts['is_due'] else 'profit_rub'

        if key:
            analytics[key] += parts['amount']

    analytics['weight'] = round(analytics['weight'], 2)
    for key in ('profit_gel', 'profit_rub', 'due_gel', 'due_rub'):
        analytics[key] = round(analytics[key], 2)

    return analytics


class AllNewView(MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('all_new.html')


class AllNewDataView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def get(self):
        try:
            page = max(int(request.args.get('page', 1)), 1)
            per_page = min(max(int(request.args.get('per_page', 15)), 1), 50)

            query = _apply_all_new_filters(self.db.session.query(Purcell), request.args)
            total = query.count()
            analytics_records = query.all()
            records = (
                query.order_by(Purcell.date.desc(), Purcell.number.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
                .all()
            )

            return jsonify({
                'success': True,
                'items': [_serialize_parcel(record) for record in records],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'has_more': page * per_page < total,
                },
                'analytics': _build_analytics(analytics_records),
            })
        except Exception as e:
            log_error(e)
            return jsonify({'success': False, 'message': 'Failed to load parcels'}), 500


class AllNewThumbView(MethodView):
    def __init__(self, db, app):
        self.db = db
        self.app = app

    decorators = [login_required]

    def get(self, parcel_id):
        record = self.db.session.query(Purcell).get(parcel_id)
        fallback = os.path.join(self.app.static_folder, 'images', 'not_found.jpeg')
        if not record or not record.image:
            return send_file(fallback)

        image_path = record.image.replace('\\', os.sep).lstrip('/\\')
        full_path = os.path.abspath(os.path.join(os.getcwd(), image_path))
        static_path = os.path.abspath(self.app.static_folder)

        if os.path.commonpath([full_path, static_path]) != static_path or not os.path.exists(full_path):
            return send_file(fallback)

        cache_dir = os.path.join(self.app.static_folder, 'purcells', 'thumbs')
        os.makedirs(cache_dir, exist_ok=True)
        stamp = int(os.path.getmtime(full_path))
        thumb_path = os.path.join(cache_dir, f'{record.id}-{stamp}.jpg')

        if not os.path.exists(thumb_path):
            with Image.open(full_path) as image:
                image = ImageOps.exif_transpose(image).convert('RGB')
                image.thumbnail((96, 96))
                image = image.filter(ImageFilter.GaussianBlur(radius=1.2))
                image.save(thumb_path, 'JPEG', quality=35, optimize=True)

        return send_file(thumb_path, mimetype='image/jpeg')


class RemoveFromListView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def post(self):
        access = ['admin', 'Tbilisi']
        # ÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ° Ð¿Ñ€Ð°Ð² Ð´Ð¾ÑÑ‚ÑƒÐ¿Ð°
        if current_user.role not in access:
            return jsonify({'success': False, 'message': 'áƒ—áƒ¥áƒ•áƒ”áƒœ áƒáƒ  áƒ’áƒáƒ¥áƒ•áƒ— áƒ¬áƒ•áƒ“áƒáƒ›áƒ'}), 404
        
        # ÐŸÐ¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ Ð·Ð½Ð°Ñ‡ÐµÐ½Ð¸Ðµ data.id Ð¸Ð· Ð·Ð°Ð¿Ñ€Ð¾ÑÐ°
        data_id = request.json.get('id')

        # Ð˜Ñ‰ÐµÐ¼ Ð·Ð°Ð¿Ð¸ÑÑŒ Ð² Ñ‚Ð°Ð±Ð»Ð¸Ñ†Ðµ Purcell Ð¿Ð¾ Ð¿ÐµÑ€ÐµÐ´Ð°Ð½Ð½Ð¾Ð¼Ñƒ id
        purcell_entry = self.db.session.query(Purcell).get(data_id)

        if purcell_entry:
            # Ð•ÑÐ»Ð¸ Ð·Ð°Ð¿Ð¸ÑÑŒ Ð½Ð°Ð¹Ð´ÐµÐ½Ð°, ÑƒÐ´Ð°Ð»ÑÐµÐ¼ ÐµÐµ
            self.db.session.delete(purcell_entry)
            self.db.session.commit()
            return jsonify({'success': True, 'message': 'áƒ©áƒáƒœáƒáƒ¬áƒ”áƒ áƒ˜ áƒ¬áƒáƒ¨áƒšáƒ˜áƒšáƒ˜áƒ'}), 200
        else:
            # Ð•ÑÐ»Ð¸ Ð·Ð°Ð¿Ð¸ÑÑŒ Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½Ð°, Ð²Ð¾Ð·Ð²Ñ€Ð°Ñ‰Ð°ÐµÐ¼ ÑÐ¾Ð¾Ð±Ñ‰ÐµÐ½Ð¸Ðµ Ð¾Ð± Ð¾ÑˆÐ¸Ð±ÐºÐµ
            return jsonify({'success': False, 'message': f'Ð—Ð°Ð¿Ð¸ÑÑŒ Ñ id {data_id} Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½Ð°'}), 404

class EditParcelView(MethodView):
    def __init__(self, db, app):
        self.db = db
        self.app = app

    decorators = [login_required]

    def post(self):
        try:
            # ÐŸÐ¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ Ð´Ð°Ð½Ð½Ñ‹Ðµ Ð¸Ð· Ñ„Ð¾Ñ€Ð¼Ñ‹
            data = request.form.to_dict()

            # ÐŸÐ¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ Ð¿ÐµÑ€ÐµÐ´Ð°Ð½Ð½ÑƒÑŽ Ñ„Ð¾Ñ‚Ð¾Ð³Ñ€Ð°Ñ„Ð¸ÑŽ, ÐµÑÐ»Ð¸ Ð¾Ð½Ð° ÐµÑÑ‚ÑŒ
            photo = request.files.get('photo')

            # ÐžÐ±Ñ€Ð°Ð±Ð¾Ñ‚ÐºÐ° Ñ„Ð¾Ñ‚Ð¾Ð³Ñ€Ð°Ñ„Ð¸Ð¸, ÐµÑÐ»Ð¸ Ð¾Ð½Ð° Ð±Ñ‹Ð»Ð° Ð¿ÐµÑ€ÐµÐ´Ð°Ð½Ð°
            if photo and photo.filename != '':
                handle_uploaded_image(request.files['photo'], data['id'], self.app)

            edit_parcel_(self.db, data)

            # Ð’Ð¾Ð·Ð²Ñ€Ð°Ñ‰Ð°ÐµÐ¼ ÑÐ¾Ð¾Ð±Ñ‰ÐµÐ½Ð¸Ðµ Ð¾Ð± ÑƒÑÐ¿ÐµÑˆÐ½Ð¾Ð¹ Ð¾Ð±Ñ€Ð°Ð±Ð¾Ñ‚ÐºÐµ
            return jsonify({'message': 'áƒ áƒ”áƒ“áƒáƒ¥áƒ¢áƒ˜áƒ áƒ”áƒ‘áƒáƒ› áƒ¬áƒáƒ áƒ›áƒáƒ¢áƒ”áƒ‘áƒ˜áƒ— áƒ©áƒáƒ˜áƒáƒ áƒ', 'success': True}), 200
        except Exception as e:
            return jsonify({'message': f'áƒ“áƒáƒ¤áƒ˜áƒ¥áƒ¡áƒ˜áƒ áƒ“áƒ áƒ¨áƒ”áƒªáƒ“áƒáƒ›áƒ : {e}', 'success': False}), 400

class EditDeliveryView(MethodView):
    def __init__(self, db):
        self.db = db

    decorators = [login_required]

    def post(self):
        access = ['admin', 'Moscow', 'SPB']
        # ÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ° Ð¿Ñ€Ð°Ð² Ð´Ð¾ÑÑ‚ÑƒÐ¿Ð°
        if current_user.role not in access:
            return jsonify({'message': 'áƒ—áƒ¥áƒ•áƒ”áƒœ áƒáƒ  áƒ’áƒáƒ¥áƒ•áƒ— áƒ¬áƒ•áƒ“áƒáƒ›áƒ!', 'success': False}), 404
        
        data_id = request.json.get('id')  # ÐŸÐ¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ ID Ð¸Ð· Ð·Ð°Ð¿Ñ€Ð¾ÑÐ°

        # ÐÐ°Ñ…Ð¾Ð´Ð¸Ð¼ Ð·Ð°Ð¿Ð¸ÑÑŒ Ð² Ñ‚Ð°Ð±Ð»Ð¸Ñ†Ðµ Purcell Ð¿Ð¾ Ð¿ÐµÑ€ÐµÐ´Ð°Ð½Ð½Ð¾Ð¼Ñƒ ID
        purcell_entry = self.db.session.query(Purcell).get(data_id)

        if purcell_entry:
            # ÐŸÑ€Ð¾Ð²ÐµÑ€ÑÐµÐ¼, Ñ‡Ñ‚Ð¾ ÑÑ‚Ð°Ñ‚ÑƒÑ Ð´Ð¾ÑÑ‚Ð°Ð²ÐºÐ¸ ÐµÑ‰Ðµ Ð½Ðµ 'yes'
            if purcell_entry.delivery != 'yes':
                # Ð˜Ð·Ð¼ÐµÐ½ÑÐµÐ¼ ÑÑ‚Ð°Ñ‚ÑƒÑ Ð´Ð¾ÑÑ‚Ð°Ð²ÐºÐ¸ Ð½Ð° 'yes'
                purcell_entry.delivery = 'yes'
                self.db.session.commit()
                return jsonify({'message': 'ÐŸÐ¾ÑÑ‹Ð»ÐºÐ° Ð²Ñ€ÑƒÑ‡ÐµÐ½Ð°', 'success': True}), 200
            else:
                # Ð•ÑÐ»Ð¸ ÑÑ‚Ð°Ñ‚ÑƒÑ Ð´Ð¾ÑÑ‚Ð°Ð²ÐºÐ¸ ÑƒÐ¶Ðµ 'yes', Ð²Ð¾Ð·Ð²Ñ€Ð°Ñ‰Ð°ÐµÐ¼ Ð¾ÑˆÐ¸Ð±ÐºÑƒ 404
                return jsonify({'message': 'Ð”Ð°Ð½Ð½Ð°Ñ Ð¿Ð¾ÑÑ‹Ð»ÐºÐ° ÑƒÐ¶Ðµ Ð²Ñ€ÑƒÑ‡ÐµÐ½Ð°!', 'success': False}), 404
        else:
            return jsonify({'message': 'Ð—Ð°Ð¿Ð¸ÑÑŒ Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½Ð°'}), 404

# Ð¤ÑƒÐ½ÐºÑ†Ð¸Ñ Ð´Ð»Ñ Ñ€ÐµÐ³Ð¸ÑÑ‚Ñ€Ð°Ñ†Ð¸Ð¸ Ð¼Ð°Ñ€ÑˆÑ€ÑƒÑ‚Ð¾Ð²
def register_all_routes(app, db):
    app.add_url_rule('/all', view_func=AllView.as_view('all', db=db))
    app.add_url_rule('/all-new', view_func=AllNewView.as_view('all_new'))
    app.add_url_rule('/api/all-new/parcels', view_func=AllNewDataView.as_view('all_new_parcels', db=db))
    app.add_url_rule('/all-new/image-thumb/<int:parcel_id>', view_func=AllNewThumbView.as_view('all_new_image_thumb', db=db, app=app))
    app.add_url_rule('/removing_from_the_list', view_func=RemoveFromListView.as_view('removing_from_the_list', db=db))
    app.add_url_rule('/edit_parcel', view_func=EditParcelView.as_view('edit_parcel', db=db, app=app))
    app.add_url_rule('/delivery_status', view_func=EditDeliveryView.as_view('delivery_status', db=db))
