import json
import urllib

from urllib.parse import urlparse

from flask import (
    Blueprint,
    jsonify,
    request,
)
from flask.views import MethodView

from auth import auth_required
from database import db
from services.ads import (
    AdsService,
)
from services.users import (
    UserDoesNotExistError,
    UsersService,
)

bp = Blueprint('users', __name__)



class UserView(MethodView):
    
    @bp.route('<int:account_id>/ads')
    def get(account_id):
        with db.connection as con:
            service = AdsService(con)
            dict_query = dict(request.args)
            ads = service.get_ads(dict_query=dict_query, account_id=account_id)
            return jsonify(ads)
    
    def post(self):
        with db.connection as con:
            service = UsersService(con)
            request_json = request.json
            is_seller = request_json.get('is_seller')
            if not is_seller:
                user = dict(service.reqistration_account(request_json))
            else:
                user = service.reqistration_account(request_json)
                account_id = user['id']
                user = service.registration_seller(request_json, account_id)
            return jsonify(user)
   

class UsersView(MethodView):
   
    @auth_required
    def get(self, account_id, account):
        with db.connection as con:
            service = UsersService(con)
            try:
                user = service.get_account(account_id)
            except UserDoesNotExistError:
                return '', 404
            else:
                return jsonify(user)

    @bp.route('<int:account_id>/ads', methods=['POST'])
    @auth_required
    def post(account_id, account):
        if account_id != account['id'] or not account['is_seller']:
            return '', 403
    
        with db.connection as con:
            request_json = request.json
            service = AdsService(con)
            ad = service.post_ad(request_json, account_id)
            return jsonify(ad), 201
   
    @auth_required
    def patch(self, account_id, account):
        if account_id != account['id']:
            return '', 403
        
        with db.connection as con:
            service = UsersService(con)
            request_json = request.json
            user = service.patch_account(request_json, account['id'])
            return jsonify(user)


bp.add_url_rule('<int:account_id>', view_func=UsersView.as_view('users/'))
bp.add_url_rule('', view_func=UserView.as_view('users'))


