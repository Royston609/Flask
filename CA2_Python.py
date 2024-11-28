from flask import Flask, render_template, request, jsonify
import mysql.connector
from flask_cors import CORS
import json
from logging.config import dictConfig

# MySQL connection setup
mysql = mysql.connector.connect(
    user='web',
    password='webPass',
    host='127.0.0.1',
    database='property_price'
)

# Logging configuration
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
CORS(app)

# Test Route
@app.route("/test")
def test():
    return "Hello World!<BR/>THIS IS ANOTHER TEST!"

# Add Property Data to Database
@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.get_json()
        cursor = mysql.cursor()
        insert_query = '''INSERT INTO property_price_normal (
            DisplayAddress, GroupPhoneNumber, SizeStringMeters, GroupEmail, CreatedOnDate,
            NumberOfBeds, PriceChangeIsIncrease, PropertyType, NumberOfBathrooms,
            PhotoCount, Dublin_Info, PriceAsString
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

        cursor.execute(insert_query, (
            data['DisplayAddress'], data['GroupPhoneNumber'], data['SizeStringMeters'], 
            data['GroupEmail'], data['CreatedOnDate'], data['NumberOfBeds'], 
            data['PriceChangeIsIncrease'], data['PropertyType'], 
            data['NumberOfBathrooms'], data['PhotoCount'], 
            data['Dublin_Info'], data['PriceAsString']
        ))
        mysql.commit()
        return jsonify({"Result": "Success"})
    else:
        return render_template('add.html')

# Get Property Data from Database
@app.route("/get", methods=['GET'])
def get_property_data():
    cursor = mysql.cursor()
    cursor.execute("SELECT * FROM property_price_normal")
    rows = cursor.fetchall()

    results = []
    for row in rows:
        result = {
            'DisplayAddress': row[0],
            'GroupPhoneNumber': row[1],
            'SizeStringMeters': row[2],
            'GroupEmail': row[3],
            'CreatedOnDate': row[4],
            'NumberOfBeds': row[5],
            'PriceChangeIsIncrease': row[6],
            'PropertyType': row[7],
            'NumberOfBathrooms': row[8],
            'PhotoCount': row[9],
            'Dublin_Info': row[10],
            'PriceAsString': row[11]
        }
        results.append(result)

    return jsonify({"Results": results, "count": len(results)})

# Show Data - Default Route
@app.route("/index.html")
def index():
    return render_template('index.html')

# Default Route - Show Data
@app.route("/")
def hello():
    cursor = mysql.cursor()
    cursor.execute('''SELECT * FROM property_price_normal''')
    rv = cursor.fetchall()

    results = []
    for row in rv:
        result = {
            'DisplayAddress': row[0],
            'GroupPhoneNumber': row[1],
            'SizeStringMeters': row[2],
            'GroupEmail': row[3],
            'CreatedOnDate': row[4],
            'NumberOfBeds': row[5],
            'PriceChangeIsIncrease': row[6],
            'PropertyType': row[7],
            'NumberOfBathrooms': row[8],
            'PhotoCount': row[9],
            'Dublin_Info': row[10],
            'PriceAsString': row[11]
        }
        results.append(result)

    return jsonify({"Results": results, "count": len(results)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)  # Run the Flask app with SSL
