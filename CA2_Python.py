import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from logging.config import dictConfig

# Data extraction from MyHome API
url = 'https://api.myhome.ie/search'
res = []

for x in range(1, 20):
    data = {"ApiKey": "4284149e-13da-4f12-aed7-0d644a0b7adb",
            "CorrelationId": "6a38fb7d-ff5b-4132-bcc9-7224238f7c93",
            "RequestTypeId": 2,
            "RequestVerb": "POST",
            "Endpoint": "https://api.myhome.ie/search",
            "Page": f"{x}",
            "PageSize": 20,
            "SortColumn": 2,
            "SortDirection": 2,
            "SearchRequest": {"PropertyClassIds": [3], "PropertyStatusIds": [11], "PropertyTypeIds": [], "RegionId": 1265, "LocalityIds": [], "ChannelIds": [1], "Polygons": []}
           }

    headers = {'accept': 'application/json, text/plain, */*',
               'content-type': 'application/json',
               'referer': 'https://www.myhome.ie/',
               'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
               'sec-ch-ua-mobile': '?0',
               'sec-ch-ua-platform': '"Windows"',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
              }

    response = requests.post(url, json=data, headers=headers)
    response_json = response.json()
    # Extract 'SearchResults' and append to results
    search_results = response_json.get('SearchResults', [])
    if search_results:
        res.extend(search_results)

# Dataframe creation
df = pd.DataFrame(res)

# Function to extract Dublin area from the address
def extract_dublin_info(address):
    if not address:  # Check if address is empty or None
        return None

    address_lower = address.lower()  # Convert to lowercase for case-insensitive comparison

    # Define the mapping for known Dublin areas
    area_mapping = {
        'templeogue': 'Dublin 6', 'ridgewood': 'Dublin 9', 'strawberry beds': 'Dublin 15', 'blackrock': 'Dublin 4',
        'merrion park': 'Dublin 4', 'swords': 'Dublin 9', 'malahide': 'Dublin 13', 'lusk': 'Dublin 17', 'blanchardstown': 'Dublin 15',
        'donabate': 'Dublin 13', 'clontarf': 'Dublin 3', 'ranelagh': 'Dublin 6', 'ballyfermot': 'Dublin 10', 'dun laoghaire': 'Dublin 18',
        'tallaght': 'Dublin 24', 'drimnagh': 'Dublin 12', 'ballinteer': 'Dublin 16', 'artane': 'Dublin 5', 'crumlin': 'Dublin 12',
        'lucan': 'Dublin 20', 'adamstown': 'Dublin 22', 'santry': 'Dublin 19'
    }

    # Check the address for any known Dublin areas from the mapping
    for key, value in area_mapping.items():
        if key in address_lower:
            return value

    # Check if 'dublin' is in the address and extract the area number if possible
    if 'dublin' in address_lower:  # Check if 'dublin' is in the address
        start_index = address_lower.find('dublin') + len('dublin')
        additional_info = address[start_index:].strip()

        # Handle non-numeric characters and extract the numeric info
        numeric_info = ''
        for char in additional_info:
            if char.isdigit():  # If the character is a digit, add it to numeric_info
                numeric_info += char
            elif numeric_info:  # Stop once we have the numeric part
                break

        if numeric_info:
            return f'Dublin {numeric_info}'  # Return 'Dublin' and the number

    return None  # Return None if no area is found

# Extract Dublin info from the 'DisplayAddress' column
df['Dublin_Info'] = df['DisplayAddress'].apply(extract_dublin_info)

# Store rows where Dublin_Info is None (discarded rows)
discarded_rows = df[df['Dublin_Info'].isna()]

# Remove rows where Dublin_Info is None (keep only valid rows)
df = df[df['Dublin_Info'].notna()]

# Cleaning and handling missing data for 'SizeStringMeters' and 'SizeStringFeet'
for info in df['Dublin_Info'].unique():
    for bedrooms in df['NumberOfBeds'].unique():
        # Calculate mean size based on Dublin area and number of bedrooms
        mean_size = df.loc[(df['Dublin_Info'] == info) & (df['NumberOfBeds'] == bedrooms), 'SizeStringMeters'].mean()

        # Iterate over rows where SizeStringMeters is null
        for idx, row in df[(df['Dublin_Info'] == info) & (df['SizeStringMeters'].isnull())].iterrows():
            if not pd.isnull(row['SizeStringFeet']):
                # If SizeStringFeet is not null, convert it to meters and fill SizeStringMeters
                df.at[idx, 'SizeStringMeters'] = row['SizeStringFeet'] * 0.092903
            else:
                # If SizeStringFeet is also null, use the mean size based on bedrooms and area
                if not pd.isnull(mean_size):
                    df.at[idx, 'SizeStringMeters'] = mean_size

# Replace blank sizes with mean apartment size based on Dublin area
for info in df['Dublin_Info'].unique():
    mean_value = df.loc[df['Dublin_Info'] == info, 'SizeStringMeters'].mean()
    df.loc[(df['Dublin_Info'] == info) & (df['SizeStringMeters'].isnull()), 'SizeStringMeters'] = mean_value

# Handling 'PriceAsString' for weekly rent and conversion to monthly
weekly_entries = df[df['PriceAsString'].str.contains('week', case=False, na=False)]
for index, row in weekly_entries.iterrows():
    price_string = row['PriceAsString']

    # Extract the numeric value from the string
    cleaned_price = price_string.replace('€', '').replace(',', '').split()[0]
    weekly_price = float(cleaned_price)

    # Convert weekly to monthly by multiplying by 13/3
    monthly_price = weekly_price * (13 / 3)

    # Update the 'PriceAsString' column with the new monthly price
    df.at[index, 'PriceAsString'] = f'€{monthly_price:,.2f} / month'

# Filter Dublin data (only areas 1 to 24)
df = df[df['Dublin_Info'].str.startswith('Dublin ') & df['Dublin_Info'].str.split().str[1].astype(int).between(1, 24)]
df['Price'] = pd.to_numeric(df['PriceAsString'].str.extract(r'([\d,\.]+)')[0].str.replace(',', '', regex=True), errors='coerce')

# Drop rows where Price could not be converted or is not a 4-digit number
df = df.dropna(subset=['Price'])
df = df[df['Price'].astype(int).between(1000, 9999)]

# Group and calculate average prices
price_summary = df.groupby('Dublin_Info')['Price'].agg(['mean', 'min', 'max', 'count'])

# Removing columns with too many missing values
missing_values = df.isnull().mean()
columns_to_drop = missing_values[(missing_values > 0.1)].index.tolist()
df = df.loc[:, (missing_values <= 0.1)]

# Select relevant columns
columns_to_keep = [
    'DisplayAddress', 'GroupPhoneNumber', 'SizeStringMeters', 'GroupEmail', 'CreatedOnDate',
    'NumberOfBeds', 'PriceChangeIsIncrease', 'PropertyType', 'NumberOfBathrooms',
    'PhotoCount', 'Dublin_Info', 'PriceAsString'
]
df_final = df[columns_to_keep]

# Convert 'CreatedOnDate' to string and clean it
df_final['CreatedOnDate'] = df_final['CreatedOnDate'].astype(str)
df_final['CreatedOnDate'] = df_final['CreatedOnDate'].apply(lambda x: x.split('T')[0] if 'T' in x else x)

# Flask app to serve data
dictConfig({
    'version': 1,
    'formatters': {'default': {'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'}},
    'handlers': {'wsgi': {'class': 'logging.StreamHandler', 'stream': 'ext://flask.logging.wsgi_errors_stream', 'formatter': 'default'}},
    'root': {'level': 'INFO', 'handlers': ['wsgi']},
})

app = Flask(__name__)
CORS(app)

# Connect to MySQL
conn = mysql.connector.connect(user='web', password='webPass', host='localhost', database='property_price')
cursor = conn.cursor()

@app.route("/get", methods=['GET'])
def get_property_data():
    try:
        cursor.execute("SELECT * FROM property_price")
        rows = cursor.fetchall()
        if not rows:
            return jsonify({"message": "No data found in the database"}), 404
        
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
        
        # Insert the fetched data into a new table if required
        cursor.executemany('''INSERT INTO property_price_inserted (
            DisplayAddress, GroupPhoneNumber, SizeStringMeters, GroupEmail, CreatedOnDate,
            NumberOfBeds, PriceChangeIsIncrease, PropertyType, NumberOfBathrooms,
            PhotoCount, Dublin_Info, PriceAsString
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', [
            (result['DisplayAddress'], result['GroupPhoneNumber'], result['SizeStringMeters'], result['GroupEmail'], 
            result['CreatedOnDate'], result['NumberOfBeds'], result['PriceChangeIsIncrease'], result['PropertyType'], 
            result['NumberOfBathrooms'], result['PhotoCount'], result['Dublin_Info'], result['PriceAsString'])
            for result in results
        ])
        conn.commit()

        return jsonify({"Results": results, "count": len(results)}), 200

    except mysql.connector.Error as err:
        app.logger.error(f"MySQL Error: {err}")
        return jsonify({"message": "Database error", "error": str(err)}), 500

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"message": "Internal server error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, ssl_context=('cert.pem', 'privkey.pem'))  # Use SSL certificates for secure connections
