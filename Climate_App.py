import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from dateutil.relativedelta import relativedelta as rd

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'enter starting date'<br/>"
        f"/api/v1.0/'enter starting date'/'enter end date'<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation"""
    # Query all records of prcp
    results = session.execute("SELECT date, prcp FROM measurement").all()

    session.close()

    # Convert list of tuples into normal list
    prcp_date_info = []
    
    for row in results:
        
        prcp_dict = {
            'prcp' : row[1],
            'date' : row[0]
        }

        prcp_date_info.append(prcp_dict)


    return jsonify(prcp_date_info)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    results = session.execute("SELECT station FROM station").all()

    session.close()

    # Convert list of tuples into normal list
    station_info = []
    
    for row in results:
        
        stat_info = {
            'station' : row[0]
        }

        station_info.append(stat_info)

    return jsonify(station_info)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature"""
    # Query all records of temp
    result = session.execute('select MAX(date) from measurement').all()
    most_recent_date = None
    # Put result through a for loop to return it as a string
    for row in result:
        most_recent_date = row[0]
        
    date = str(most_recent_date).split('-')

    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    
    most_recent_date = dt.datetime(year, month, day)

    twelve_months = most_recent_date + rd(months=-12)
    
    active_station = session.execute("SELECT station, COUNT(station) as total_stations FROM measurement GROUP BY station ORDER BY total_stations DESC").all()
    most_active_station = active_station[0][0]

    results = session.query(measurement.station, measurement.date, measurement.tobs).\
    filter(measurement.station == most_active_station).\
        filter(measurement.date > twelve_months).all()

    # Convert list of tuples into normal list
    date_tobs_list = []


    for row in results:
        station = row[0]
        date = row[1]
        tobs = row[2]

        info = {
        "station":station,
        "date":date,
        "tobs":tobs
        }

        date_tobs_list.append(info)

    return jsonify(date_tobs_list)

@app.route("/api/v1.0/<start>")
def min_describe(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all info
    result1=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()[0]

    session.close()

    # Convert list of tuples into normal list
    
    stat_info = {
       'min_temp':result1[0],
       'max_temp':result1[2],
       'avg_temp':result1[1]
        }

    return jsonify(stat_info)

@app.route("/api/v1.0/<start>/<end>")
def start_end_describe(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all info
    result1=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
            filter(measurement.date <= end).all()[0]

    session.close()

    # Convert list of tuples into normal list
    
    stat_info = {
       'min_temp':result1[0],
       'max_temp':result1[2],
       'avg_temp':result1[1]
        }

    return jsonify(stat_info)
