import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#Database
#Create a Variable to Use Hawaii.sqlite to Create an Instance of a New Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# Reflect an Existing Database into a New Model
Base = automap_base()

#Reflect the Tables
Base.prepare(engine, reflect=True)

#Create Variables to Save References to Each Table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create a Session or Link from Python to the Database
session = Session(engine)


#Flask
app = Flask(__name__)


@app.route("/")
def welcome():
    return"""<html>
    <h1>List of All Available API Routes</h1>
    <ul>
    <br>
    <li>
    List of Precipitation for the Previous Year:
    <br>
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
    </li>
    <br>
    <li>
    List of Stations for Observations: 
    <br>
   <a href="/api/v1.0/stations">/api/v1.0/stations</a>
   </li>
    <br>
    <li>
    List of Observations of Temperature for the Previous Year:
    <br>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    </li>
    <br>
    <li>
    List of Minimum, Maximum, and Average for All Dates Greater than and Equal to the Start Date:
    <br>
    <a href="/api/v1.0/2017-08-01">/api/v1.0/2017-08-01</a>
    </li>
    <br>
    <li>
    List of Minimum, Maximum, and Average for the Dates in the Range of the Start End Dates Inclusive:
    <br>
    <a href="/api/v1.0/2017-08-01/2017-08-15">/api/v1.0/2017-08-01/2017-08-15</a>
    </li>
    <br>
    </ul>
    </html>
    """


@app.route("/api/v1.0/precipitation")
def precipitation():
    """List of Precipitation for the Previous Year"""
    #Design a Query to Retrieve the Last 12 Months of Data on Precipitation and Plot the Results
    previous_twelve_months_dates = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    most_recent_date = previous_twelve_months_dates[0]

    #Calculate the Date 1 year Ago from Today
    #Since 365 Days in Reverse Ends on the Date after the First Date, 366 Days Creates a Date for Start and End that are Equal
    date_previous_year = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    #Perform a Query to Retrieve the Data and Scores for Precipitation
    query_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_previous_year).all()

    # Convert Tuple into a Dictionary
    precipitation_dict = dict(query_precipitation)

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations(): 
    """List of Stations for Observations"""
    # Query for Stations
    results_stations =  session.query(Measurement.station).group_by(Measurement.station).all()

    # Convert Tuple into a List
    stations_list = list(np.ravel(results_stations))

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs(): 
    """List of Observations of Temperature for the Previous Year"""

    #Design a Query to Retrieve the Last 12 Months of Data on Precipitation and Plot the Results
    previous_twelve_months_dates = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    most_recent_date = previous_twelve_months_dates[0]

    #Calculate the Date 1 year Ago from Today
    #Since 365 Days in Reverse Ends on the Date after the First Date, 366 Days Creates a Date for Start and End that are Equal
    date_previous_year = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    #Perform a Query to Retrieve the Data for Observations of Temperature
    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= date_previous_year).all()

    # Convert Tuple into a List
    tobs_list = list(results_tobs)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start(start=None):
    """List of Minimum, Maximum, and Average for All Dates Greater than and Equal to the Start Date"""

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    from_start_list=list(from_start)
    return jsonify(from_start_list)

    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """List of Minimum, Maximum, and Average for the Dates in the Range of the Start End Dates Inclusive"""
    
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list=list(between_dates)
    return jsonify(between_dates_list)


if __name__ == '__main__':
    app.run(debug=True)