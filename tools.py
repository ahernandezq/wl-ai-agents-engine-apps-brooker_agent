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
def get_real_estate_listings():
    return _run_query("SELECT * FROM ai_tools order by name")

# function to insert a new tool into te DB
def insert_real_estate_info(name, link, ecosystem, category, enterprise_categories, license, description):
    sql = '''INSERT INTO ai_tools (name, link, ecosystem, category, enterprise_categories, license, description, last_search) VALUES (? , ? , ? , ? , ? , ? , ? , datetime() )'''
    
    fields = (name, link, ecosystem, category, enterprise_categories, license, description)
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute(sql, fields)
    con.commit() 
    con.close() 
    return True

# Function for update airtable records
def update_real_estate_info(id, name, link, ecosystem, category, enterprise_categories, license, description):
    sql = '''UPDATE ai_tools 
              SET name = ? ,
                  link = ? ,
                  ecosystem = ? ,
                  category = ? ,
                  enterprise_categories = ? 
                  license = ? ,
                  description = ? ,
                  last_search = datetime()  
              WHERE id = ?'''
    
    fields = (name, link, ecosystem, category, enterprise_categories, license, description, id)
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute(sql, fields)
    con.commit() 
    con.close() 
    return True