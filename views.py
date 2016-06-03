# -*- coding: utf-8 -*-

__author__ = 'fyabc'

from flask import render_template, request, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required

# Local modules.
from createApp import app, lm
import config
from forms import QueryForm, LoginForm, ReserveForm, UnsubscribeForm, \
    InsertForm, RouteQueryForm, CustomerQueryForm, SignInForm, DeleteForm

# Use this import to initialize the database connection.
from dbOperations import db, Customers, \
    query, addReserve, removeReserve, insertRecord, deleteRecord, routeQuery, customerQuery, insertCustomer,\
    Flights, Hotels, Cars, Reservations


@app.route('/')
@app.route('/index')
def mainPage():
    return render_template('index.html')


@app.route('/query', methods=['GET', 'POST'])
@login_required
def queryPage():
    results = None
    table = None
    form = QueryForm()

    if form.validate_on_submit():
        table, results = query()

    return render_template('query.html', query=form, queryResult=results, table=table,
                           isAdmin=config.adminLoggedIn)


@app.route('/reserve', methods=['GET', 'POST'])
@login_required
def reservePage():
    errorCode = None
    if request.method == 'POST':
        if 'customerID' in request.form:
            errorCode = addReserve()
        else:
            errorCode = removeReserve()

    return render_template('reserve.html', reserveForm=ReserveForm(), unsubscribeForm=UnsubscribeForm(),
                           errorCode=errorCode, isAdmin=config.adminLoggedIn)


@app.route('/routeQuery', methods=['GET', 'POST'])
def routeQueryPage():
    flightsResults, hotelsResults, carsResults = None, None, None
    form = RouteQueryForm()

    if form.validate_on_submit():
        flightsResults, hotelsResults, carsResults = routeQuery()

    return render_template('routeQuery.html', routeQueryForm=form,
                           flightsResults=flightsResults, hotelsResults=hotelsResults, carsResults=carsResults,
                           Flights=Flights, Hotels=Hotels, Cars=Cars)


@app.route('/customerQuery', methods=['GET', 'POST'])
@login_required
def customerQueryPage():
    results = None
    form = CustomerQueryForm()

    if form.validate_on_submit():
        results = customerQuery()

    return render_template('customerQuery.html', customerQueryForm=form,
                           results=results, Reservations=Reservations, isAdmin=config.adminLoggedIn)


@app.route('/signIn', methods=['GET', 'POST'])
def signInPage():
    form = SignInForm()
    errorCode = None

    if form.validate_on_submit():
        errorCode = insertCustomer()

    return render_template('signIn.html', signInForm=form, errorCode=errorCode,
                           isAdmin=config.adminLoggedIn)


@lm.user_loader
def load_user(idNumber):
    return Customers.query.get(idNumber)


@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    loginFailed = False

    form = LoginForm()

    if form.validate_on_submit():
        user = Customers.query.get(form.userName.data)
        if user and user.password == form.password.data:
            login_user(user, remember=False)
            if user.IDNumber == form.myUserName:
                config.adminLoggedIn = True
        else:
            loginFailed = True

    return render_template('login.html', loginForm=form, loginFailed=loginFailed,
                           isAdmin=config.adminLoggedIn)

# if login_required but not authorized, redirect to login page.
lm.unauthorized_callback = loginPage


@app.route('/logout')
@login_required
def logoutPage():
    logout_user()
    config.adminLoggedIn = False

    return render_template('logout.html')


@app.route('/insert', methods=['GET', 'POST'])
@login_required
def insertPage():
    if not config.adminLoggedIn:
        return redirect(url_for('.loginPage'))

    errorCode = None
    if request.method == 'POST':
        errorCode = insertRecord()

    return render_template('insert.html', insertForm=InsertForm(), errorCode=errorCode)


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def deletePage():
    if not config.adminLoggedIn:
        return redirect(url_for('.loginPage'))

    form = DeleteForm()

    errorCode = None
    if form.validate_on_submit():
        errorCode = deleteRecord()

    return render_template('delete.html', deleteForm=form, errorCode=errorCode)
