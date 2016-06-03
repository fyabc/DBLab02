# -*- coding: utf-8 -*-

__author__ = 'fyabc'

# These 2 statements are important.
import pymysql

pymysql.install_as_MySQLdb()

from flask import request, session
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, InvalidRequestError

# Local modules.
from createApp import app
import config

db = SQLAlchemy(app)


class DBErrorMessage:
    def __init__(self, code, *message):
        self.code = code
        self.message = message


class Flights(db.Model):
    __tablename__ = 'Flights'

    flightNum = db.Column(name='flightNum', type_=db.String(20), primary_key=True, nullable=False)
    price = db.Column(name='price', type_=db.BigInteger)
    numSeats = db.Column(name='numSeats', type_=db.Integer)
    numAvail = db.Column(name='numAvail', type_=db.Integer)
    fromCity = db.Column(name='fromCity', type_=db.String(20))
    toCity = db.Column(name='toCity', type_=db.String(20))

    constraint = db.CheckConstraint('numAvail >= 0')

    columns = [('flightNum', '航班号'), ('price', '价格'), ('numSeats', '座位数量'), ('numAvail', '可用数量'),
               ('fromCity', '出发城市'), ('toCity', '目的城市')]

    def __init__(self, flightNum, price, numSeats, fromCity, toCity):
        self.flightNum = flightNum
        self.price = price
        self.numSeats = numSeats
        self.numAvail = numSeats
        self.fromCity = fromCity
        self.toCity = toCity

    def __repr__(self):
        return 'Flights(flightNum=%s, price=%d, numSeats=%d, numAvail=%d, fromCity=%s, toCity=%s)' % \
               (self.flightNum, self.price, self.numSeats, self.numAvail, self.fromCity, self.toCity)


class Hotels(db.Model):
    __tablename__ = 'Hotels'

    location = db.Column(name='location', type_=db.String(20), primary_key=True, nullable=False)
    price = db.Column(name='price', type_=db.BigInteger)
    numRooms = db.Column(name='numRooms', type_=db.Integer)
    numAvail = db.Column(name='numAvail', type_=db.Integer)

    constraint = db.CheckConstraint('numAvail >= 0')

    columns = [('location', '地点'), ('price', '价格'), ('numRooms', '房间数量'), ('numAvail', '可用数量')]

    def __init__(self, location, price, numRooms):
        self.location = location
        self.price = price
        self.numRooms = numRooms
        self.numAvail = numRooms

    def __repr__(self):
        return 'Hotels(location=%s, price=%d, numRooms=%d, numAvail=%d)' % \
               (self.location, self.price, self.numRooms, self.numAvail)


class Cars(db.Model):
    __tablename__ = 'Cars'

    location = db.Column(name='location', type_=db.String(20), primary_key=True, nullable=False)
    price = db.Column(name='price', type_=db.BigInteger)
    numCars = db.Column(name='numCars', type_=db.Integer)
    numAvail = db.Column(name='numAvail', type_=db.Integer)

    constraint = db.CheckConstraint('numAvail >= 0')

    columns = [('location', '地点'), ('price', '价格'), ('numCars', '车辆数量'), ('numAvail', '可用数量')]

    def __init__(self, location, price, numCars):
        self.location = location
        self.price = price
        self.numCars = numCars
        self.numAvail = numCars

    def __repr__(self):
        return 'Cars(location=%s, price=%d, numCars=%d, numAvail=%d)' % \
               (self.location, self.price, self.numCars, self.numAvail)


class Customers(db.Model):
    __tablename__ = 'Customers'

    IDNumber = db.Column(name='IDNumber', type_=db.String(20), primary_key=True, nullable=False)
    customerName = db.Column(name='customerName', type_=db.String(20))
    password = db.Column(name='password', type_=db.String(20))

    columns = [('IDNumber', '用户ID'), ('customerName', '用户名'), ('password', '密码')]

    def __init__(self, IDNumber, customerName, password):
        self.IDNumber = IDNumber
        self.customerName = customerName
        self.password = password

    # Used by flask_login.
    def is_authenticated(self):
        # return Customers.query.get(self.IDNumber).password == self.password
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.IDNumber)

    def __repr__(self):
        return 'Customers(IDNumber=%s, customerName=%s, password=%s)' %\
               (self.IDNumber, self.customerName, self.password)


class Reservations(db.Model):
    __tablename__ = 'Reservations'

    reservationID = db.Column(name='reservationID', type_=db.Integer, primary_key=True, nullable=False,
                              autoincrement=True)
    customerID = db.Column(db.ForeignKey('Customers.IDNumber'), name='customerID', type_=db.String(20), nullable=False)
    reserveType = db.Column(name='reserveType', type_=db.SmallInteger)
    reserveKey = db.Column(name='reserveKey', type_=db.String(20), nullable=False)

    columns = [('reservationID', '预订ID'), ('customerID', '顾客ID'),
               ('reserveType', '预订类型'), ('reserveKey', '预订名称')]

    def __init__(self, customerID, reserveType, reserveKey):
        self.customerID = customerID
        self.reserveType = reserveType
        self.reserveKey = reserveKey

    def __repr__(self):
        return 'Reservations(customerID=%s, reserveType=%d, reserveKey=%s) # reservationID=%d' % \
               (self.customerID, self.reserveType, self.reserveKey, self.reservationID)


Tables = {
    table.__tablename__: table
    for table in [Flights, Cars, Hotels, Customers, Reservations]
}


def queryOneColumn(result, nameCol=0):
    return [row[nameCol] for row in result.fetchall()]


def createTriggers():
    allProcedures = queryOneColumn(db.session.execute("""Show Procedure Status Where Db = 'DBLab02';"""), 1)

    if 'changeReserve' not in allProcedures:
        # You needn't to change delimiter in mysql APIs, because ';' will not split the query in API.
        db.session.execute(
            """\
            CREATE PROCEDURE DBLab02.changeReserve(resType INT(11), resKey CHAR(20), ins_or_del BOOLEAN)
            BEGIN

            IF resType = 1 THEN
                UPDATE Flights
                SET numAvail = numAvail + If(ins_or_del, -1, 1)
                WHERE flightNum = resKey
                ;
            ELSEIF resType = 2 THEN
                UPDATE Hotels
                SET numAvail = numAvail + If(ins_or_del, -1, 1)
                WHERE location = resKey
                ;
            ELSEIF resType = 3 THEN
                UPDATE Cars
                SET numAvail = numAvail + If(ins_or_del, -1, 1)
                WHERE location = resKey
                ;
            END IF;

            END;
            """
        )

    # 在表 FLIGHTS 中,numAvail 表示指定航班上的还可以被预订的座位数。对
    #   于 一 个 给 定 的 航 班 ( flightNum ) , 数 据 库 一 致 性 的 条 件 之 一 是 , 表
    #   RESERVATIONS 中所有预订该航班的条目数加上该航班的剩余座位数必须
    #   等于该航班上总的座位数。这个条件对于表 CARS 和表 HOTELS 同样适用。

    allTriggers = queryOneColumn(db.session.execute("""Show Triggers;"""))

    if 'T_AvailableNum_Ins' not in allTriggers:
        db.session.execute(
            """
            CREATE TRIGGER T_AvailableNum_Ins
            AFTER INSERT ON Reservations
            FOR EACH ROW
            CALL changeReserve(new.reserveType, new.reserveKey, TRUE)
            ;
            """
        )

    if 'T_AvailableNum_Del' not in allTriggers:
        db.session.execute(
            """
            CREATE TRIGGER T_AvailableNum_Del
            AFTER DELETE ON Reservations
            FOR EACH ROW
            CALL changeReserve(old.reserveType, old.reserveKey, FALSE)
            ;
            """
        )

    if 'T_AvailableNum_Update' not in allTriggers:
        db.session.execute(
            """
            CREATE TRIGGER T_AvailableNum_Update
            AFTER UPDATE ON Reservations
            FOR EACH ROW
            BEGIN
            CALL changeReserve(old.reserveType, old.reserveKey, FALSE);
            CALL changeReserve(new.reserveType, new.reserveKey, TRUE);
            END
            ;
            """
        )

    db.session.commit()


def query():
    table = Tables.get(request.form['type'])
    queryName = request.form['queryName']
    if config.adminLoggedIn or table in (Flights, Hotels, Cars):
        if queryName == '':
            return table, table.query.all()
        else:
            return table, [table.query.get(queryName)]
    else:
        if table == Reservations:
            return table, table.query.filter(Reservations.customerID == session.get('user_id')).all()
        else:
            return table, [table.query.get(session.get('user_id'))]


def addReserve():
    if config.adminLoggedIn:
        customerID = request.form['customerID']
    else:
        customerID = session.get('user_id')

    reserveType = int(request.form['reserveType'])
    reserveKey = request.form['reserveKey']

    table = None
    if reserveType == 1:
        table = Flights
    elif reserveType == 2:
        table = Hotels
    elif reserveType == 3:
        table = Cars

    # test if the reserveKey in the Table.
    reserveEntity = table.query.get(reserveKey)
    if reserveEntity is None:
        return DBErrorMessage(1, '没有在数据库中找到预订的名称。')
    elif reserveEntity.numAvail <= 0:
        return DBErrorMessage(5, '没有多余的空位了！')

    reservation = Reservations(customerID, reserveType, reserveKey)
    try:
        db.session.add(reservation)
        db.session.commit()
    except IntegrityError as e:
        print(e)
        db.session.rollback()
        return DBErrorMessage(2, '完整性错误：数据库中不存在该用户编号。', '详细信息：%s' % e)
    except Exception as e:
        print(e)
        db.session.rollback()
        return DBErrorMessage(3, '其他错误：%s' % e)

    return DBErrorMessage(0, '预订成功！预订编号为%d，请记得保存。' % reservation.reservationID)


def removeReserve():
    try:
        reservationID = int(request.form['reservationID'])
        assert 1 <= reservationID
    except ValueError as e:
        print(e)
        return DBErrorMessage(4, '预订编号必须为正整数')

    if config.adminLoggedIn:
        deleteNum = Reservations.query.filter(Reservations.reservationID == reservationID).delete(False)
    else:
        deleteNum = Reservations.query.filter(Reservations.reservationID == reservationID,
                                              Reservations.customerID == session.get('user_id')).delete(False)
    db.session.commit()

    if deleteNum == 0:
        return DBErrorMessage(1, '没有在数据库中找到预订的编号，或这不是您的预订。')
    else:
        return DBErrorMessage(0, '退订成功！')


def insertRecord():
    table = Tables[request.form['type']]

    if table == Customers:
        IDNumber = request.form['primaryKey']
        customerName = request.form['customerName']
        password = request.form['password']
        try:
            db.session.add(Customers(IDNumber, customerName, password))
            db.session.commit()
        except IntegrityError as e:
            print(e)
            db.session.rollback()
            return DBErrorMessage(2, '完整性错误：数据库中已存在该用户。', '详细信息：%s' % e)
        except Exception as e:
            print(e)
            db.session.rollback()
            return DBErrorMessage(3, '其他错误：%s' % e)
        return DBErrorMessage(0, '添加用户成功！')
    else:
        # validate the price and numTotal.
        try:
            price = int(request.form['price'])
            numTotal = int(request.form['numTotal'])
            assert 1 <= price <= 1048576
            assert 1 <= numTotal <= 1024
        except (ValueError, AssertionError) as e:
            print(e)
            return DBErrorMessage(4, '价格必须为1~1048576的整数，可用数量必须为1~1024的整数')

        try:
            if table == Flights:
                db.session.add(table(request.form['primaryKey'], price, numTotal, request.form['fromCity'],
                                     request.form['toCity']))
            else:
                db.session.add(table(request.form['primaryKey'], price, numTotal))
            db.session.commit()
        except IntegrityError as e:
            print(e)
            db.session.rollback()
            return DBErrorMessage(2, '完整性错误：数据库中已存在主键相同的记录。', '详细信息：%s' % e)
        except Exception as e:
            print(e)
            db.session.rollback()
            return DBErrorMessage(3, '其他错误：%s' % e)
        return DBErrorMessage(0, '添加记录成功！')


def deleteRecord():
    print(request.form)

    table = Tables[request.form['type']]
    primaryKey = request.form['primaryKey']

    if table == Reservations:
        deleteNum = Reservations.query.filter(Reservations.reservationID == primaryKey).delete(False)
        db.session.commit()

        if deleteNum == 0:
            return DBErrorMessage(1, '没有在数据库中找到预订的编号。')
        else:
            return DBErrorMessage(0, '删除预订成功！')

    elif table == Customers:
        # Before deleting a customer, you should remove all reservations it reserved.
        Reservations.query.filter(Reservations.customerID == primaryKey).delete(False)
        deleteNum = Customers.query.filter(Customers.IDNumber == primaryKey).delete(False)
        db.session.commit()

        if deleteNum == 0:
            return DBErrorMessage(1, '没有在数据库中找到用户的ID。')
        else:
            return DBErrorMessage(0, '删除用户成功！')
    else:
        try:
            # Before deleting a flight, you should remove all reservations that reserve it.
            Reservations.query.filter(Reservations.reserveKey == primaryKey).delete(False)

            db.session.delete(table.query.get(primaryKey))
            db.session.commit()
        except InvalidRequestError as e:
            print(e)
            db.session.rollback()
            return DBErrorMessage(1, '没有在数据库中找到对应的记录。')
        except Exception as e:
            print(e)
            db.session.rollback()
            return DBErrorMessage(3, '其他错误：%s' % e)
        return DBErrorMessage(0, '删除记录成功！')


def insertCustomer():
    userID = request.form['userID']
    userName = request.form['userName']
    password = request.form['password']

    try:
        db.session.add(Customers(userID, userName, password))
        db.session.commit()
    except IntegrityError as e:
        print(e)
        db.session.rollback()
        return DBErrorMessage(2, '完整性错误：该用户ID已被注册！')
    except Exception as e:
        print(e)
        db.session.rollback()
        return DBErrorMessage(3, '其他错误：%s' % e)
    return DBErrorMessage(0, '注册成功！')


def routeQuery():
    fromCity = request.form['fromCity']
    toCity = request.form['toCity']

    flightsResult = Flights.query.filter(Flights.fromCity == fromCity, Flights.toCity == toCity).all()
    hotelsResult = Hotels.query.filter(Hotels.location == toCity).all()
    carsResult = Cars.query.filter(Cars.location == toCity).all()

    return flightsResult, hotelsResult, carsResult


def customerQuery():
    if config.adminLoggedIn:
        IDNumber = request.form['IDNumber']
        customerName = request.form['customerName']
    else:
        IDNumber = session.get('user_id')
        customerName = ''

    if IDNumber != '':
        return Reservations.query.filter(Reservations.customerID == IDNumber).all()
    elif customerName != '':
        return db.session.query(Reservations) \
            .join(Customers) \
            .filter(Reservations.customerID == Customers.IDNumber, Customers.customerName == customerName) \
            .all()
    else:
        return Reservations.query.all()


def dropTable():
    db.drop_all()


def createTable():
    # dropTable()
    db.create_all()
    createTriggers()
    # result = db.engine.execute("Show databases")
    # print(result.fetchall())


createTable()
