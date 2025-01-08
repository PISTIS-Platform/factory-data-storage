#tools.py
#TODO: Update to use batch insertion of rows 

import uuid, logging

from sql_scripts import *
from lineage_tracker import *
from flask import make_response,jsonify
from log import *
from identity_manager import *


log = setup_logging()

# Change datatypes from project specific datamodel to postgresql datatypes

datamodel = {
        "float" : "real",
        "integer" : "integer",
        "bigint" : "bigint",
        "string" : "text",
        "text" : "text",
        "real" : "real",
        "datetime": "timestamp without time zone",
        "date": "date",
        "timestamp": "timestamp with time zone",
        "double": "double precision",
        "double precision" : "double precision",
        "numeric" : "numeric"

    }

# Function to create the response of endpoints
def create_response(response_text, assetUUID,status_code):

    response = {
            "message": response_text,
            "asset_uuid": uuid.UUID(assetUUID),
            "status_code": status_code
        }

    return response

def create_table(db,tableName,columns):

    # Creating a table in the Tabular Assets Store
    create_table_query = "CREATE TABLE {} ({})".format(tableName, columns[0:-1])
    db.engine.execute(create_table_query)  # TODO: Check the return value of the response

def insert_intotable(db,tableName,column_names,tableEntries):

    # Inserting rows into a table in the Tabular Assets Store
    sql = ""
    for entry in tableEntries['rows']:
        if entry and "" not in entry and " " not in entry:
            insert_value_query = ""
            for row in entry:
                insert_value_query += "'{}' ,".format(str(row))
            insert_value_query=insert_value_query[0:-1]  
            # print(insert_value_query, flush=True)
            sql += insertIntoTableQuery.format(tableName,column_names[0:-2],insert_value_query) 
    # print(sql, flush=True)
    db.engine.execute(sql)


def new_table(db, table_name, columns, column_names, data_list, metadata, datamodel_list, pipe_id=None):

    # This section creates a new table in the Assets Store
    log.info("Table is being created")

    try:
        # Methods to create a new table and insert values to it
        create_table(db,table_name,columns)

        log.info("Inserting values into the table")
        insert_intotable(db,table_name,column_names,data_list)
    except Exception as e:
        log.exception(f"Table creation failed: {e}")
        return make_response(jsonify("Table creation failed"), 500)

    response = create_response("New dataset created in the data storage", table_name, 200)
    print(response, flush=True)
    return make_response(jsonify(response), 200)

def update_table(db, table_name, asset_type, access_token, registry_token, names, domain_datatypes, column_names, data_list):

    log.info("Table is being updated")

    # Convert UUID format to hex format  
    hex_tableUUID = uuid.UUID(table_name).hex 

    # Get the input data and create the new columns if there is a database schema change
    change_table = ""
    for (i,j) in zip(names, domain_datatypes): 
        sql = "ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} {} ;".format(hex_tableUUID, i,j)
        change_table +=  sql
    db.engine.execute(change_table)
    

    # Insert the new version_id and rows into the table
    insert_intotable(db,hex_tableUUID,column_names,data_list) 

    response = create_response("Dataset updated in the data storage",table_name, 200)
    return make_response (jsonify(response), 200)
   

