# -*- coding: utf-8 -*-

__author__ = 'fyabc'

import os

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager

app = Flask(__name__)

app.config.from_object('config')

Bootstrap(app)

lm = LoginManager()
lm.init_app(app)
