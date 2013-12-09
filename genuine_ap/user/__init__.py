# -*- coding: UTF-8 -*-
from flask import Blueprint

user_ws = Blueprint("user-ws", __name__, static_folder="static",
                    template_folder="templates")

import genuine_ap.user.views
