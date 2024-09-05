from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################

# Set up database engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def homepage():
    return (
        "Welcome to the Climate API!<br>"
        "Available routes:<br>"
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/<start><br>"
        "/api/v1.0/<start>/<end><br>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year before the most recent data point
    start_date = dt.datetime(2016, 8, 23)
    end_date = dt.datetime(2017, 8, 23)
    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        order_by(Measurement.date).all()
    
    # Convert to dictionary
    precipitation_dict = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Query all stations
    results = session.query(Station.station).all()
    stations_list = [station[0] for station in results]
    
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Calculate the date one year before the most recent data point
    start_date = dt.datetime(2016, 8, 23)
    end_date = dt.datetime(2017, 8, 23)
    
    # Query temperature observations for the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()[0]
    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        order_by(Measurement.date).all()
    
    tobs_list = [{"date": date, "temperature": tobs} for date, tobs in results]
    
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def start(start):
    # Query the minimum, average, and maximum temperature for dates greater than or equal to start date
    results = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp')
    ).filter(Measurement.date >= start).all()
    
    return jsonify(results[0]._asdict())

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    # Query the minimum, average, and maximum temperature for dates from start date to end date, inclusive
    results = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp')
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    return jsonify(results[0]._asdict())

if __name__ == '__main__':
    app.run(debug=True)
