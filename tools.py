import sqlite3
import os
import json
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

db_name = os.getenv("DB_NAME", "ai-tools.db")
db_name = join(dirname(__file__), db_name)

# Function run query
def _run_query(query):
    con = sqlite3.connect(db_name)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query)    
    results = []
    for r in cur.fetchall():
        results.append(dict(r))

    con.close()
    return json.dumps(results)

# Function get Gen AI tool by name
def get_real_estate_info_by_name(name):
    return _run_query(f"SELECT * FROM ai_tools WHERE name='{name}' COLLATE NOCASE")

# Function to Get the list of AI tools from the SQLite database
def get_real_estate_listings(location = None, bedrooms = None, bathrooms = None, basement = None, yard = None, laundry_room = None, garage = None, min_price = None, max_price = None, other_features = None):
    file = open("./applications/broker_agent/datasets/listings.json")
    data = json.load(file)
    file.close()
    return data

# Function to generate a new JSON file with the search results
def dump_results_to_file(items = None):
    f = open("./applications/broker_agent/datasets/results.json", "w")
    f.write(items)
    f.close()
    return True