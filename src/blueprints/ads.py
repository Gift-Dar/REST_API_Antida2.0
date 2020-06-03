from flask import (
    Blueprint,
    jsonify,
    request,
)
from flask.views import MethodView

from auth import (
    auth_required,
    check_auth_and_sellerid,
)
from database import db
from services.ads import (
    AdDoesNotExistError,
    AdsService,
)


bp = Blueprint('ads', __name__)


class AdsView(MethodView):

    def get(self):
        with db.connection as con:
            service = AdsService(con)
            qwery = dict(request.args)
            ads = service.get_ads(dict_query=qwery)
            return jsonify(ads)

    @auth_required
    def post(self, account):
        account_id = account['id']
        if not account['is_seller']:
            return '', 403

        with db.connection as con:
            request_json = request.json
            service = AdsService(con)
            ad = service.post_ad(request_json, account_id)
            return jsonify(ad), 201


class AdView(MethodView):

    def get(self, ad_id):
        with db.connection as con:
            service = AdsService(con)
            try:
                ad = service.phorm_dict_ad(ad_id)
            except AdDoesNotExistError:
                return '', 404
            else:
                return jsonify(ad)


    @check_auth_and_sellerid
    def patch(self, ad_id, seller):
        seller_id = seller['id']
        request_json = request.json
        with db.connection as con:
            cur = con.execute(f"""
                SELECT ad.seller_id
                FROM ad
                WHERE ad.id={ad_id}
            """)
            result = cur.fetchone()
            if result is None:
                return "", 404
        seller_id_ad = result[0]
            
        if seller_id != seller_id_ad:
            return '', 403
        service = AdsService(con)
        service.patch_ad(request_json, ad_id)
        return "", 204
    # Нужно написать декоратор для проверки seller.account_id=account.id
    @check_auth_and_sellerid
    def delete(self, ad_id, seller):
        seller_id = seller['id']
        with db.connection as con:
            cur = con.execute(f"""
                SELECT ad.seller_id
                FROM ad
                WHERE ad.id={ad_id}
            """)
            result = cur.fetchone()
            if result is None:
                return "", 404
        seller_id_ad = result[0]
    
        if seller_id != seller_id_ad:
            return '', 403
        service = AdsService(con)
        service.delete_ad(ad_id)
        return "", 204
    
        
        


bp.add_url_rule('', view_func=AdsView.as_view('ads'))
bp.add_url_rule('<int:ad_id>', view_func=AdView.as_view('ads/'))
