from flask.views import MethodView
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, send_file


class ListView(MethodView):
    def __init__(self):
        pass
    
    decorators = [login_required]

    def get(self):
        return render_template('shipments.html')
    


def register_shipments_routes(app, db):
    app.add_url_rule('/shipments', view_func=ListView.as_view('shipments'))