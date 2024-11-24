from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Royston@2000\@localhost:3306/property_price'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define a Table Model
class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    column1 = db.Column(db.String(255), nullable=False)
    column2 = db.Column(db.Float, nullable=False)

# Create table in the database
@app.before_request
def create_tables():
    db.create_all()

# Route to insert data into MySQL from JSON
@app.route('/insert_data', methods=['POST'])
def insert_data():
    try:
        data = request.get_json()
        df = pd.DataFrame(data)
        for _, row in df.iterrows():
            entry = Data(column1=row['column1'], column2=row['column2'])
            db.session.add(entry)
        db.session.commit()
        return jsonify({"message": "Data inserted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Route to retrieve data
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        result = Data.query.all()
        output = [{"id": row.id, "column1": row.column1, "column2": row.column2} for row in result]
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)