# import some libraries 
import datetime
import json
import os
import sqlite3
from decimal import Decimal, getcontext
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text

from commons import R, randomcolor


# get the project path
basedir = os.path.abspath(os.path.dirname(__file__))
# init Flask framework
app = Flask(__name__)
app.secret_key = 'any random string'

### sqlalchemy config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dino.db') + '?check_same_thread=False'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# show raw sql when set true
app.config['SQLALCHEMY_ECHO'] = True
### define type
db = SQLAlchemy(app)
# init database session
Session = db.sessionmaker(bind=db.engine)
session = Session()

# init return object 
r = R()

# data model
class Dino_Data(db.Model):
    __tablename__ = "dino_Table"
    index = db.Column(db.Integer, primary_key=True)
    idn = db.Column(db.TEXT)
    eag = db.Column(db.FLOAT)
    lag = db.Column(db.FLOAT)
    phl = db.Column(db.String(32))
    cll = db.Column(db.String(32))
    odl = db.Column(db.String(32))
    fml = db.Column(db.String(32))
    gnl = db.Column(db.String(32))
    lng = db.Column(db.String(32))
    lat = db.Column(db.String(32))

    # define return data structure
    def serialize(self):
        return {
            "index": self.index,
            "idn": self.idn,
            "eag": self.eag,
            "lag": self.lag,
            "phl": self.phl,
            "cll": self.cll,
            "odl": self.odl,
            "fml": self.fml,
            "gnl": self.gnl,
            "lng": self.lng,
            "lat": self.lat,
        }


# go to index.html web page
@app.route('/')
def index():  # put application's code here
    return render_template("index.html")


# go to dashboard.html web page
@app.route('/dashboard')
def dashboard():  # put application's code here
    return render_template("dashboard.html")


# go to data.html web page
@app.route('/data')
def data():  # put application's code here
    return render_template("data.html")


# return search request data
@app.route('/data/search', methods=['GET'])
def dataSearch():  # put application's code here
    # get request parameters
    keyword = request.values.get("keyword")
    # fetch data from database
    obj_list = selectData(Dino_Data, keyword)
    # put data into array and return to frontend
    obj_list1 = []
    for obj in obj_list:
        obj_list1.append(Dino_Data.serialize(obj))
    return r.success(obj_list1)


# return charts data 
@app.route('/data/charts', methods=['GET'])
def dataCharts():  # put application's code here
    # find all data
    keyword = request.values.get("keyword")
    phl_list = selectPhlData(Dino_Data)

    # get all cll data without specific phl
    cll_list = selectCllData(Dino_Data, None)
    bar_xAxis = []
    bar_series = []
    for obj in cll_list:
        bar_xAxis.append(obj.name)
        bar_series.append(obj.name_count)
    barData = {
        'xAxis': bar_xAxis,
        'series': bar_series,
    }
    # calculate the number for each layer, value 1 if not equal to 0, else: do not set and keep looping
    # calculate pie data
    pieData = []
    # get all phl data
    for obj1 in phl_list:
        phl_children = []

        # get all cll data of this phl
        cll_list = selectCllData(Dino_Data, obj1.name)
        for obj2 in cll_list:
            cll_children = []
            # get all gnl data of this cll
            gnl_list = selectGnlData(Dino_Data, obj2.name)

            for obj3 in gnl_list:
                # set echarts format object
                gnl_obj = {
                    'name': obj3.name,
                    'itemStyle': {
                        'color': randomcolor()
                    },
                    'value': obj3.name_count
                }
                cll_children.append(gnl_obj)

            # set echarts format object
            cll_obj = {
                'name': obj2.name,
                'itemStyle': {
                    'color': randomcolor()
                },
                'children': cll_children
            }
            if gnl_list.count() <= 0:
                cll_obj['value'] = 1
            phl_children.append(cll_obj)

        # set echarts format object
        phl_obj = {
            'name': obj1.name,
            'itemStyle': {
                'color': randomcolor()
            },
            'children': phl_children
        }
        pieData.append(phl_obj)

   
    return_data = {
        'barData': barData,
        'pieData': pieData,
    }
    return r.success(return_data)


### sqlite database operations

# find data list
def selectData(obj, keyword):
    try:
        if keyword is not None and keyword != '':
            obj_list = obj.query.filter(obj.idn.like('%' + keyword + '%'))
        else:
            obj_list = obj.query.all()
        return obj_list
    except Exception as e:
        res = {'code': 0, 'message': 'find data list error'}
        return json.dumps(res, ensure_ascii=False, indent=4)



# find all phl data and its count value 
def selectPhlData(Dino_Data):
    try:
        results = session.query(Dino_Data.phl.label('name'), func.count('*').label('name_count')).filter(
            Dino_Data.phl.isnot(None)
        ).group_by(Dino_Data.phl)
        return results
    except Exception as e:
        res = {'code': 0, 'message': 'find data list error'}
        return json.dumps(res, ensure_ascii=False, indent=4)


# find all cll data of specific phl and its count value 
def selectCllData(Dino_Data, phl):
    try:
        if phl is not None:
            results = session.query(Dino_Data.cll.label('name'), func.count('*').label('name_count'))\
                .filter(Dino_Data.cll.isnot(None))\
                .filter(Dino_Data.phl == phl)\
                .group_by(Dino_Data.cll)
        else:
            results = session.query(Dino_Data.cll.label('name'), func.count('*').label('name_count')) \
                .filter(Dino_Data.cll.isnot(None)) \
                .group_by(Dino_Data.cll)
        return results
    except Exception as e:
        res = {'code': 0, 'message': 'find data list error'}
        return json.dumps(res, ensure_ascii=False, indent=4)


# find all gnl data of specific cll and its count value 
def selectGnlData(Dino_Data, cll):
    try:
        results = session.query(Dino_Data.gnl.label('name'), func.count('*').label('name_count'))\
            .filter(Dino_Data.gnl.isnot(None))\
            .filter(Dino_Data.cll == cll)\
            .group_by(Dino_Data.gnl)
        return results
    except Exception as e:
        res = {'code': 0, 'message': 'find data list error'}
        return json.dumps(res, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    app.run()