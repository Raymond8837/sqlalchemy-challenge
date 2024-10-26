# Import the dependencies.

from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`

# Use the Base class to reflect the database tables
Base = automap_base()
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Flask Routes
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a dictionary of all dates and precipitation values"""
    results = session.query(Measurement.date, Measurement.prcp).all()
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    results = session.query(Station.station).all()
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year"""
    # Get the most active station id from the dataset
    most_active_station = session.query(Measurement.station).group_by(Measurement.station)\
                               .order_by(func.count(Measurement.station).desc()).first()[0]
    # Find the most recent date and calculate one year back
    latest_date = session.query(func.max(Measurement.date)).scalar()
    previous_year = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query the temperature observations for the most active station for the last year
    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= previous_year
    ).all()

    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of TMIN, TAVG, and TMAX for all dates greater than or equal to the start date"""
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    temperature_stats = list(np.ravel(results))
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of TMIN, TAVG, and TMAX for all dates between the start and end date inclusive"""
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temperature_stats = list(np.ravel(results))
    return jsonify(temperature_stats)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)