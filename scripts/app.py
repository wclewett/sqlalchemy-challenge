import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# SQLAlchemy Startup
engine = create_engine("sqlite:///../resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Date Calculator
def date_calc():
    Latest_date = session.query(func.max(Measurement.date)).all()
    today = dt.date.today()
    Lastest_date_datefmt = today.replace(year=int(Latest_date[0][0][:4]), month=int(Latest_date[0][0][5:7]), day=int(Latest_date[0][0][8:]))
    One_Year_backdate = Lastest_date_datefmt-dt.timedelta(days=365)
    This_Year_End_Date = Lastest_date_datefmt.strftime("%Y-%m-%d")
    Previous_Year_Start_Date = One_Year_backdate.strftime("%Y-%m-%d")
    Year_list = [Previous_Year_Start_Date,This_Year_End_Date]
    return(tuple(Year_list))

# Flask Routes
app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"API Branches:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"Place Date After API path<br/>"
        f"Input Format: 'YYYY-MM-DD'<br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Place Date After API path<br/>"   
        f"Input Format: 'YYYY-MM-DD/YYYY-MM-DD'<br/>"
        )  

@app.route("/api/v1.0/precipitation")
def precipitation():
    Range = date_calc()
    End_date = Range[1]
    Start_date = Range[0]
    results = session.query(Measurement.date, Measurement.station,Measurement.prcp).filter(Measurement.date <= End_date).filter(Measurement.date >= Start_date).all()                                                                  
    list = []
    for result in results:
        dict = {"Date":result[0],"Station":result[1],"Precipitation":result[2]}
        list.append(dict)
    return jsonify(list)

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station,Station.name).all()
    list=[]
    for station in stations:
        dict = {"Station ID:":stations[0],"Station Name":stations[1]}
        list.append(dict)
    return jsonify(list)

@app.route("/api/v1.0/tobs")
def tobs():
    Range = date_calc()
    End_date = Range[1]
    Start_date = Range[0]
    tobs = session.query(Measurement.date,Measurement.tobs).\
                            filter(Measurement.date <= End_date).\
                            filter(Measurement.date >= Start_date).all()
    list = []
    for temp in tobs:
        dict = {"date": temp[0], "tobs": temp[1]}
        list.append(dict)
    return jsonify(list)  

@app.route("/api/v1.0/<start>")
def tstart(start):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).order_by(Measurement.date.desc()).all()
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(dict) 

@app.route("/api/v1.0/<start>/<end>")
def tstartend(start,end):         
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.date.desc()).all()
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(dict)   

if __name__ == '__main__':
    app.run(debug=True)