from flask import (
    Blueprint,
    jsonify,
    request,
)
from flask.views import MethodView

from auth import auth_required
from database import db
from services.colors import (
    ColorsService,
)

bp = Blueprint('colors', __name__)



class ColorsView(MethodView):
    
    @auth_required
    def get(self, account):
        if not account['is_seller']:
            return '', 403
        with db.connection as con:
            service = ColorsService(con)
            colors = service.get_colors()
            return jsonify(colors)

    @auth_required
    def post(self, account):
        if not account['is_seller']:
            return '', 403
        with db.connection as con:
            request_json = request.json
            service = ColorsService(con)
            color = service.post_color(request_json)
            return jsonify(color)

bp.add_url_rule('', view_func=ColorsView.as_view('colors'))