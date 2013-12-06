# -*- coding: UTF-8 -*-
import os
from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("genuine_ap.default_settings")
app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"), silent=True)

from genuine_ap import utils
utils.assert_dir('static/spu_pics')


def register_views():
    # register web services
    from genuine_ap.tag import tag_page
    app.register_blueprint(tag_page, url_prefix='/tag')
