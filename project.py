from flask import Flask, request, jsonify
import mysql.connector
import pandas as pd

app = Flask(__name__)

# Function to establish MySQL connection
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",  # MySQL server host
        user="root",  # MySQL username
        password="Royston@2000",  # MySQL password
        database="property_price"  # Database name
    )
    return connection

# API endpoint to insert data from DataFrame into MySQL
@app.route('/insert_data', methods=['POST'])
def insert_data():
    # Receive the DataFrame data in JSON format
    data = request.json
    df = pd.DataFrame(data)  # Convert the JSON data into a DataFrame

    conn = get_db_connection()
    cursor = conn.cursor()
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Data inserted successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)