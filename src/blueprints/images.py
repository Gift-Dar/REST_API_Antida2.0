import os
import uuid

import flask
from flask import (
    Blueprint,
    current_app,
    request,
    send_from_directory,
    url_for,
)
from flask.views import MethodView

from auth import auth_required


class ImagesView(MethodView):
    @auth_required
    def post(self, account):
        if not account['is_seller']:
            return '', 403
        file = request.files['image']
        upload_dir = current_app.config['UPLOAD_DIR']
        filename = f'{uuid.uuid4()}{os.path.splitext(file.filename)[1]}'
        file.save(os.path.join(upload_dir, filename))
        file_url = flask.url_for('images.download_image', image_name=filename, _external=True)
        return flask.jsonify({"url": file_url})


class ImageView(MethodView):
    def get(self, image_name):
        upload_dir = current_app.config['UPLOAD_DIR']
        return send_from_directory(upload_dir, image_name)


bp = Blueprint('images', __name__)
bp.add_url_rule('', view_func=ImagesView.as_view('upload_image'))
bp.add_url_rule('/<image_name>', view_func=ImageView.as_view('download_image'))
