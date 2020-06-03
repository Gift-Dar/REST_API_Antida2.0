from flask import (
    Blueprint,
    jsonify,
    request,
)
from flask.views import MethodView

from database import db

bp = Blueprint('cities', __name__)

from services.cities import (
    CitiesService,
)


class CitiesView(MethodView):
    
    def get(self):
        with db.connection as con:
            service = CitiesService(con)
            cities = service.get_cities()
            return jsonify(cities)
    
    def post(self):
        with db.connection as con:
            request_json = request.json
            service = CitiesService(con)
            city = service.post_city(request_json)
            return jsonify(city)


bp.add_url_rule('', view_func=CitiesView.as_view('cities'))