import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
# from geopy.geocoders import Nominatim

url = 'https://api.myhome.ie/search'
res = []

for x in range(1,20):
#
  data = {"ApiKey":"4284149e-13da-4f12-aed7-0d644a0b7adb","CorrelationId":"6a38fb7d-ff5b-4132-bcc9-7224238f7c93","RequestTypeId":2,"RequestVerb":"POST","Endpoint":"https://api.myhome.ie/search","Page":f"{x}","PageSize":20,"SortColumn":2,"SortDirection":2,"SearchRequest":{"PropertyClassIds":[3],"PropertyStatusIds":[11],"PropertyTypeIds":[],"RegionId":1265,"LocalityIds":[],"ChannelIds":[1],"Polygons":[]}}

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

print(f"Total results collected: {len(res)}")

df = pd.DataFrame(res)
df

print(df['CustomData'].iloc[0].keys())

print(df['CustomData'])

df['CustomData'].apply(lambda x: x.get('IsMyHomePassport') if isinstance(x, dict) else None)

len(df)

# Extracting Dublin Area from Address

df = pd.DataFrame(res)
df.columns.tolist()
df.dtypes

# Function to extract Dublin area from the address
def extract_dublin_info(address):
    if not address:  # Check if address is empty or None
        return None

    address_lower = address.lower()  # Convert to lowercase for case-insensitive comparison

    # Define the mapping for known Dublin areas
    area_mapping = {
        'templeogue': 'Dublin 6',
        'ridgewood': 'Dublin 9',
        'strawberry beds': 'Dublin 15',
        'blackrock': 'Dublin 4',
        'merrion park': 'Dublin 4',
        'swords': 'Dublin 9',
        'malahide': 'Dublin 13',
        'lusk': 'Dublin 17',
        'blanchardstown': 'Dublin 15',
        'donabate': 'Dublin 13',
        'clontarf': 'Dublin 3',
        'ranelagh': 'Dublin 6',
        'ballyfermot': 'Dublin 10',
        'dun laoghaire': 'Dublin 18',
        'tallaght': 'Dublin 24',
        'drimnagh': 'Dublin 12',
        'ballinteer': 'Dublin 16',
        'artane': 'Dublin 5',
        'crumlin': 'Dublin 12',
        'lucan': 'Dublin 20',
        'adamstown': 'Dublin 22',
        'santry': 'Dublin 19'
    }

    # Check for specific cases like Adamstown and Lucan
    if 'adamstown' in address_lower:
        return 'Dublin 22'
    elif 'lucan' in address_lower:
        return 'Dublin 20'

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
len(df)

len(df)

# Checking for Blank entries in Apartment Size in Meters

df['SizeStringMeters']
blank_entries_meters = df['SizeStringMeters'].isnull().sum()
blank_entries_meters

# Checking for Blank entries in Apartment Size in Feet

df['SizeStringFeet']
blank_entries_feet = df['SizeStringFeet'].isnull().sum()
blank_entries_feet

# Checking for number of records in dataset

len(df)

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

# Replacing Blank sizes by mean apartment size based on Dublin area

for info in df['Dublin_Info'].unique():
    mean_value = df.loc[df['Dublin_Info'] == info, 'SizeStringMeters'].mean()
    df.loc[(df['Dublin_Info'] == info) & (df['SizeStringMeters'].isnull()), 'SizeStringMeters'] = mean_value

# Checking for blank data after treating the blank entries

df['SizeStringMeters']
blank_entries_meters = df['SizeStringMeters'].isnull().sum()
blank_entries_meters

# Checking Dublin area for blank apartment size

# Filter rows where 'SizeStringMeters' is blank
blank_entries = df[df['SizeStringMeters'].isnull()]

# Display the 'Dublin_Info' values for these rows
dublin_info_for_blank = blank_entries['Dublin_Info']

# Output the result
print("Dublin_Info values for blank entries in 'SizeStringMeters':")
print(dublin_info_for_blank.value_counts())  # Count of occurrences per Dublin_Info

# CHecking data for one of the Dublin area
dublin_11 = df[df['Dublin_Info'] == 'Dublin 11']['SizeStringMeters']

# Display the values
print("SizeStringMeters values for Dublin 11:")
print(dublin_11)

# First, group by 'NumberOfBeds' and calculate the mean of 'SizeStringMeters' for each group
mean_size_by_beds = df.groupby('NumberOfBeds')['SizeStringMeters'].mean()

# Then, assign the mean size based on the number of bedrooms
for beds, mean_size in mean_size_by_beds.items():
    df.loc[(df['SizeStringMeters'].isna()) & (df['NumberOfBeds'] == beds), 'SizeStringMeters'] = mean_size

# Checking if any more null or blank data exixting for apartment size

blank_entries = df[df['SizeStringMeters'].isnull()]
len(blank_entries)

# Extracting rows where 'PriceAsString' contains 'week'
weekly_entries = df[df['PriceAsString'].str.contains('week', case=False, na=False)]

len(weekly_entries['PriceAsString'])

# Converting weekly rent to monthly

for index, row in weekly_entries.iterrows():
    price_string = row['PriceAsString']

    # Extract the numeric value from the string
    cleaned_price = price_string.replace('€', '').replace(',', '').split()[0]
    weekly_price = float(cleaned_price)

    # Convert weekly to monthly by multiplying by 13/3
    monthly_price = weekly_price * (13 / 3)

    # Update the 'PriceAsString' column with the new monthly price
    df.at[index, 'PriceAsString'] = f'€{monthly_price:,.2f} / month'

# Checking if 'PriceAsString' contains any weekly rent availaible in the data
weekly_entries = df[df['PriceAsString'].str.contains('week', case=False, na=False)]
len(weekly_entries['PriceAsString'])

df['PriceAsString']

blank_entries = df[df['PriceAsString'].isnull()]
blank_entries['PriceAsString']

df = df[df['PriceAsString'].notna() & (df['PriceAsString'] != '')]

blank_entries = df[df['PriceAsString'].isnull()]
blank_entries['PriceAsString']

blank_entries = df[df['PropertyType'].isnull()]
blank_entries['PropertyType']

len(blank_entries)

unique_values = df['PropertyType'].unique()
print(unique_values)

# Group by 'NumberOfBeds' and get the most frequent 'PropertyType' for each group
property_type_by_beds = df.groupby('NumberOfBeds')['PropertyType'].agg(lambda x: pd.Series.mode(x).iloc[0] if not x.empty else 'Unknown')

# Ensure we are modifying the DataFrame in a safe manner
df.loc[:, 'PropertyType'] = df['PropertyType'].fillna(df['NumberOfBeds'].map(property_type_by_beds))

blank_entries = df[df['PropertyType'].isnull()]
blank_entries['PropertyType']

len(df)

df.isnull().sum()

# Checking number Of unique Dublin areas

unique_count = df['Dublin_Info'].nunique()
print(f"Number of unique values in 'Dublin_Info': {unique_count}")

# As we know Dublin areas exists only from 1 to 24, so removing rest of the data
# Converting PriceAsString to numeric

df = df.copy()
df = df[df['Dublin_Info'].str.startswith('Dublin ') & df['Dublin_Info'].str.split().str[1].astype(int).between(1, 24)]
df.loc[:, 'Price'] = pd.to_numeric(df['PriceAsString'].str.extract(r'([\d,\.]+)')[0].str.replace(',', '', regex=True), errors='coerce')

# Drop rows where Price could not be converted or is not a 4-digit number
df = df.dropna(subset=['Price'])
df = df[df['Price'].astype(int).between(1000, 9999)]

# Group and calculate average prices
price_summary = df.groupby('Dublin_Info')['Price'].agg(['mean', 'min', 'max', 'count'])

# Print the price summary
print(price_summary)

# Define the threshold for missing values
threshold = 0.1

# Get the proportion of missing values for each column
missing_values = df.isnull().mean()

# Identify columns to drop
columns_to_drop = missing_values[(missing_values > threshold)].index.tolist()

# Remove those columns from the DataFrame
df = df.loc[:, (missing_values <= threshold)]

# Output the cleaned DataFrame and the removed column names
print("Removed Columns:", columns_to_drop)

# Calculate the unique count of values in the 'Dublin_Info' column
unique_count = df['Dublin_Info'].nunique()

df.isnull().sum()

len(df.columns.tolist())

len(df)

# Sort the 'mean' prices in ascending order
price_summary_sorted = price_summary.sort_values(by='mean', ascending=True)
# Plot the bar chart
plt.figure(figsize=(14, 8))
price_summary_sorted['mean'].plot(kind='bar', color='skyblue', edgecolor='k')
plt.title("Average Price by Dublin Info", fontsize=16)
plt.xlabel("Dublin Info", fontsize=14)
plt.ylabel("Average Price", fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# List of columns to keep
columns_to_keep = [
    'DisplayAddress', 'GroupPhoneNumber', 'SizeStringMeters', 'GroupEmail', 'CreatedOnDate',
    'NumberOfBeds', 'PriceChangeIsIncrease', 'PropertyType', 'NumberOfBathrooms',
    'PhotoCount', 'Dublin_Info', 'PriceAsString'
]

# Filter the DataFrame to retain only these columns
df_final = df.loc[:, columns_to_keep]
df_final

print(df['CreatedOnDate'].dtype)

# Ensure that 'CreatedOnDate' is a string for proper handling
df['CreatedOnDate'] = df['CreatedOnDate'].astype(str)

# Use a function to handle splitting and checking if 'T' exists
df['CreatedOnDate'] = df['CreatedOnDate'].apply(lambda x: x.split('T')[0] if 'T' in x else x)

print(df['CreatedOnDate'])

for col in df.columns:
    if df[col].apply(type).eq(dict).any():  # Check for dictionaries
        df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
    elif df[col].apply(type).eq(list).any():  # Check for lists
        df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)

from flask import Flask
from flask import render_template
from flask import request
from flask_cors import CORS

import sqlite3
import json
from flask import Flask, jsonify
conn = mysql.connector.connect(user='web', password='webPass',
  host='127.0.0.1',
  database='student')

from logging.config import dictConfig

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

@app.route("/get", methods=['GET'])  # Get Property Data
def get_property_data():
    cursor.execute("SELECT * FROM property_price_normal")
    rows = cursor.fetchall()
    rows
    # Prepare results to return as JSON
    Results = []
    for row in rows:
        Result = {}
        Result['DisplayAddress'] = row[0]
        Result['GroupPhoneNumber'] = row[1]
        Result['SizeStringMeters'] = row[2]
        Result['GroupEmail'] = row[3]
        Result['CreatedOnDate'] = row[4]
        Result['NumberOfBeds'] = row[5]
        Result['PriceChangeIsIncrease'] = row[6]
        Result['PropertyType'] = row[7]
        Result['NumberOfBathrooms'] = row[8]
        Result['PhotoCount'] = row[9]
        Result['Dublin_Info'] = row[10]
        Result['PriceAsString'] = row[11]
        Results.append(Result)

    # Insert the fetched data into a new table (example: property_price_inserted)
    cursor.executemany('''
        INSERT INTO property_price_inserted (
            DisplayAddress, GroupPhoneNumber, SizeStringMeters, GroupEmail, CreatedOnDate,
            NumberOfBeds, PriceChangeIsIncrease, PropertyType, NumberOfBathrooms,
            PhotoCount, Dublin_Info, PriceAsString
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [(row['DisplayAddress'], row['GroupPhoneNumber'], row['SizeStringMeters'], row['GroupEmail'], row['CreatedOnDate'],
           row['NumberOfBeds'], row['PriceChangeIsIncrease'], row['PropertyType'], row['NumberOfBathrooms'],
           row['PhotoCount'], row['Dublin_Info'], row['PriceAsString']) for row in Results])

    # Return the results as JSON
    response = {'Results': Results, 'count': len(Results)}
    return jsonify(response)
if __name__ == "__main__":
  app.run(host='0.0.0.0',port='8080', ssl_context=('cert.pem', 'privkey.pem')) #Run the flask app at port 8080