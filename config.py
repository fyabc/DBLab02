# -*- coding: utf-8 -*-

__author__ = 'fyabc'

import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'hard-string'
SQLALCHEMY_DATABASE_URI = 'mysql://root:fy95102@localhost/DBLab02'
SQLALCHEMY_TRACK_MODIFICATIONS = True

TableNames = [
    ('Flights', '航班'),
    ('Hotels', '宾馆'),
    ('Cars', '出租车'),
    ('Customers', '用户'),
    ('Reservations', '预订情况'),
]

# The administrator has logged in or not.
adminLoggedIn = False
