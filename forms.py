# -*- coding: utf-8 -*-

__author__ = 'fyabc'

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField, PasswordField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length

# Local modules.
from config import TableNames


class SignInForm(Form):
    userID = StringField('用户ID', validators=[DataRequired()])
    userName = StringField('用户名', validators=[DataRequired()])
    password = PasswordField(
        '密码', validators=[DataRequired(), Length(min=6, message='密码长度不得少于6个字符。')])
    submit = SubmitField('注册')


class QueryForm(Form):
    type = SelectField('查询类型', coerce=str, choices=TableNames)
    queryName = StringField('查询主键名称', default='')
    submit = SubmitField('查询')


class LoginForm(Form):
    userName = StringField('账号', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

    myUserName = 'fyabc'
    myPassword = 'fy95102'


class ReserveForm(Form):
    customerID = StringField('用户编号', validators=[DataRequired()])
    reserveType = SelectField('预订类型', coerce=int,
                              choices=[
                                  (1, '航班'),
                                  (2, '宾馆'),
                                  (3, '出租车')
                              ])
    reserveKey = StringField('预订名称', validators=[DataRequired()])
    submit = SubmitField('预订')


class UnsubscribeForm(Form):
    reservationID = IntegerField('预订编号', validators=[DataRequired()])
    submit = SubmitField('退订')


class InsertForm(Form):
    type = SelectField('插入类型', coerce=str, choices=[name for name in TableNames if name[0] != 'Reservations'])
    primaryKey = StringField('主键名称', validators=[DataRequired()])
    price = IntegerField('价格', validators=[NumberRange(min=1, max=524287)])
    numTotal = IntegerField('数量', validators=[NumberRange(min=1, max=1023)])
    password = StringField('密码')
    fromCity = StringField('出发城市')
    toCity = StringField('目的城市')
    customerName = StringField('用户名称')
    submit = SubmitField('插入记录')


class DeleteForm(Form):
    type = SelectField('删除类型', coerce=str, choices=[name for name in TableNames])
    primaryKey = StringField('主键名称', validators=[DataRequired()])
    submit = SubmitField('删除记录')


class RouteQueryForm(Form):
    fromCity = StringField('出发城市', validators=[DataRequired()])
    toCity = StringField('目的城市', validators=[DataRequired()])
    submit = SubmitField('查询线路')


class CustomerQueryForm(Form):
    IDNumber = StringField('用户ID')
    customerName = StringField('用户名称')
    submit = SubmitField('查询用户')
