from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import Flask, jsonify, request, make_response, send_file
from sql_scripts import*
from table_ops import*
from log import*
import uuid, random
from lineage_tracker import *
from io import BytesIO
import csv

log = setup_logging()
class TabularAssets():
 
    def __init__(self, db:SQLAlchemy) -> None:
        self.db = db
        pass 

### CREATE TABLE -------------------------------------------------------------------------------------------------------------------------------
### Creating tables in the Assets Store---------------------------------------------------------------------------------------------------------
### TODO: Check if the body of the request is in correct format
## TODO: Remove alter column queries as database schema changes will not be made as a new version
## TODO: Add an error when column names have spaces
## TODO: Fix the update table request
## TODO: Fix Response 200 even though the table is not created

    def create_table(self):
        
        # Input arguments
        metadata = request.json['metadata']
        datamodel_list = request.json['data_model']
        data_list = request.json['data']
        log.info("Input variables received")
        if request.headers.get("Authorization"):
            header = {"Authorization": request.headers.get("Authorization")}
            access_token = request.headers.get("Authorization").split(' ')[1] 
            lineage_json = IdentityManagerApi().jwt_decode(access_token)

        # Adding extension to add UUID in the PostgreSQL database
        self.db.engine.execute(initializeUUIDQuery)

        # Creating new UUID which will be the table name in hex format (i.e., 6f4e0f99de334617964f0bfe4190f06e)
        newTableUUID = uuid.uuid4().hex

        #PostgreSQL does not allow table names to start with an integer, so adding a character from "abcdef" to the beginning of the UUID
        beginning_character = random.choice('abcdef')
        table_name = beginning_character + newTableUUID[1:]
        print("table name: " + table_name, flush=True)

        # Creating a string that includes all column names and datatypes
        columns = ""

        #Not needed as KGM does not allow creation of property names with spaces
        names = [name["name"].replace(" ", "") for name in datamodel_list['columns'] ]
        data_types = [data_type["dataType"] for data_type in datamodel_list['columns'] ]
        domain_datatypes = [datamodel[key.lower()] for key in data_types]

        for (i,j) in zip(names, domain_datatypes):  
            columns = columns + "{} {} ,".format(i,j)

        # Get only the column names 
        column_names = ""
        for i in names:
            column_names = column_names + "{}, ".format(i)

        response = new_table(self.db, table_name, columns, column_names, data_list, metadata, datamodel_list)

        if response.status_code == 200:
            log.info("Creating lineage information")
            if request.headers.get("file_distribution_id"):
                log.info("Request coming from the enrichment service")
                file_distribution_id = request.headers.get("file_distribution_id")
                lineage_object = LineageTracker(lineage_json['username'],lineage_json['usergroup'], str(uuid.UUID(table_name)),"", file_distribution_id)
                provenance_response = LineageTrackerApi().update_asset(lineage_object, "Table created from file", header)
                # response = create_response("Table created and lineage updated in the lineage tracker",str(uuid.UUID(table_name)),200)
            else:    
                lineage_object = LineageTracker(lineage_json['username'],lineage_json['usergroup'],str(uuid.UUID(table_name)), metadata["id"],"")
                provenance_response =LineageTrackerApi().create_asset(lineage_object, header)
                
            if provenance_response.status_code == 200:
                response = create_response("Table created in the Data Storage and lineage created in the Lineage Tracker",table_name, 200)
                return make_response (jsonify(response), 200)
            else:
                return make_response (jsonify({'message': provenance_response.text}), provenance_response.status_code)
        else:
            response = create_response("Table not created", table_name, 500)
            
        return response
           

### ADD ROWS -------------------------------------------------------------------------------------------------

    def add_rows(self):
        
        log.info("Adding new rows to a table")

        # Input arguments
        tablename = request.args.get("asset_uuid")
        datamodel_list = request.json['data_model']
        data_list = request.json['data']

        # Checking if the query parameters exist
        if request.args.get("asset_uuid") is None:
            return make_response (jsonify({ "message": "Query parameter 'asset_uuid' is missing", "status": 400} ), 400)
        if request.headers.get("Authorization"):
            header = {"Authorization": request.headers.get("Authorization")}
            access_token = request.headers.get("Authorization").split(' ')[1] 
            lineage_json = IdentityManagerApi().jwt_decode(access_token)

        newTableUUID = uuid.uuid4().hex
        
        #PostgreSQL does not allow table names to start with an integer, so adding a character from "abcdef" to the beginning of the UUID
        beginning_character = random.choice("abcdef")
        newTableUUID = beginning_character + newTableUUID[1:]

        sql = copyTableQuery.format(newTableUUID, str(uuid.UUID(tablename).hex))
        database_output= self.db.engine.execute(sql)

        # sql = insertCopyTableQuery.format(newTableUUID, str(uuid.UUID(tablename).hex))
        # database_output= self.db.engine.execute(sql)

        # TODO: Should be removed as KGM makes the changes     
        names = [name["name"].replace(" ", "") for name in datamodel_list['columns'] ]

        column_names = ""
        hex_assetUUID = uuid.UUID(tablename).hex
        for i in names:
            column_names = column_names + "{}, ".format(i)

        # Inserting the new values
        insert_intotable(self.db,newTableUUID,column_names,data_list)

        log.info("Creating lineage information")
        lineage_object = LineageTracker(lineage_json['username'],lineage_json['usergroup'], str(uuid.UUID(newTableUUID)),"", str(uuid.UUID(tablename)))
        provenance_response =LineageTrackerApi().update_asset(lineage_object, "rows added",header)
        if provenance_response.status_code == 200:
            response = create_response("Dataset updated in the Data Storage and lineage created in the Lineage Tracker",newTableUUID, 200)
            return make_response (jsonify(response), 200)
        else:
            return make_response (jsonify({'message': provenance_response.text}), provenance_response.status_code)
               
    ### GET TABLES ------------------------------------------------------------------------
    ### TODO: Add error if table does not exist

    def get_table(self):
        try:
            print("*** Inside tabular_assets get_table", flush=True)
            log.info("*** Inside tabular_assets get_table")
            
            # Input arguments
            tablename = request.args.get("asset_uuid")
            log.info(f"Tablename (UUID): {tablename}")
            output_format = request.args.get("JSON_output")

            # Validate input parameters
            if not tablename:
                return make_response(jsonify({"message": "Query parameter 'asset_uuid' is missing", "status": 400}), 400)
            if output_format is None:
                return make_response(jsonify({"message": "Query parameter 'JSON_output' is missing", "status": 400}), 400)
            
            # Authorization header handling
            if request.headers.get("Authorization"):
                header = {"Authorization": request.headers.get("Authorization")}
                access_token = request.headers.get("Authorization").split(' ')[1] 
                lineage_json = IdentityManagerApi().jwt_decode(access_token)

            # TODO: Update this to use catalogue or query from the database
            log.info("Fetching the table")
            
            # Generate hex name from UUID for the query
            log.info(f"Table name: {tablename}")
            hex_name = uuid.UUID(tablename).hex
            log.info(f"hex_name for database query: {hex_name}")

            # Prepare SQL query to retrieve data
            dataQuery = f'SELECT * FROM {hex_name};'
            log.info(f"Executing data query: {dataQuery}")

            # Execute the data query and handle potential missing table errors
            try:
                database_output = self.db.engine.execute(text(dataQuery))
                data_result_list = [list(row) for row in database_output]
            except Exception as e:
                log.error(f"Failed to fetch data for table '{hex_name}': {e}")
                return make_response(jsonify({"message": "Table not found or inaccessible", "status": 404}), 404)

            # Query the data model associated with the table
            datamodel_query = f'SELECT * FROM "{hex_name}";'  # Adjust as needed
            log.info(f"Executing data model query: {datamodel_query}")

            data_model_list = []
            try:
                datamodel_output = self.db.engine.execute(text(datamodel_query))
                data_model_list = [list(row) for row in datamodel_output]
            except Exception as e:
                log.error(f"Failed to fetch data model for table '{hex_name}': {e}")
                return make_response(jsonify({"message": "Data model not found or inaccessible", "status": 404}), 404)

            # Prepare final data structure
            final_data = {"rows": data_result_list}
            final_data_model = {"columns": data_model_list}

            final_result = {
                "data_model": final_data_model,
                "data": final_data
            }

            log.info("Creating lineage information")
            lineage_object = LineageTracker(lineage_json['username'], lineage_json['usergroup'], str(uuid.UUID(tablename)), "", "")
            provenance_response = LineageTrackerApi().read_asset(lineage_object, header)

            # Output JSON or CSV based on request
            if output_format.lower() == "true":
                return make_response(jsonify([final_result]), 200)
            else:
                # Prepare CSV output
                fields = [sublist[0] for sublist in data_model_list if sublist]
                with open('dataset.csv', 'w') as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerow(fields)
                    csv_writer.writerows(data_result_list)

                return send_file("dataset.csv", download_name="dataset.csv", as_attachment=True)

        except Exception as e:
            log.error(f"Unexpected error in get_table: {e}")
            return make_response(jsonify({"message": "Internal server error", "status": 500}), 500)

### GET VERSIONS
### TODO: Implement endpoint to retrieve multiple versions of the same table
        
### GET FIELDS ----------------------------------------------------------------------------

    def get_fields(self):
        
        log.info("Fetching the fields of the table")
        # Input arguments
        columnnames = request.get_json()
        tablename = request.args.get("asset_uuid")
        distinct = request.args.get("DISTINCT")
        offset = request.args.get("OFFSET")
        limit = request.args.get("LIMIT")

        # Checking if the required input parameters exist
        if request.headers.get("Authorization"):
            header = {"Authorization": request.headers.get("Authorization")}
            access_token = request.headers.get("Authorization").split(' ')[1] 
            lineage_json = IdentityManagerApi().jwt_decode(access_token)
        if request.args.get("asset_uuid") is None:
            return make_response (jsonify({ "message": "Query parameter 'asset_uuid' is missing", "status": 400} ), 400)
        if 'sort_type' in request.args and "sort_column" in request.args:
            sort_type = request.args.get("sort_type")
            sort_column = request.args.get("sort_column")      
        if 'column_names' not in columnnames:         
                response = {
                    "message": "Input data should be in a key-value form with the key column_names ",
                    "status_code": 400
                }
                return make_response (jsonify(response),response["status_code"])

        columns = ""
        where_string = ""
        for key, value in columnnames['column_names'].items():
            columns +=  "{} ,".format(key)
            if value :
                where_string += " {} = '{}' AND" . format(key, value)

        columns=columns[0:-1] 
        where_string=where_string[0:-3]  


        # Getting the sorted results
        if 'sort_type' in request.args and "sort_column" in request.args:
            log.info("Sorting the values")
            if sort_column not in columns:
                return make_response (jsonify({ "message": "Value of the query parameter 'sort_column' is not present in the body of the request. Please add this column name in the json body of the request along with other columns with a null value", "status": 400} ), 400)
                        
            sql = getSortedFieldsFromTables.format(columns, uuid.UUID(tablename).hex, sort_column, sort_type)
            if distinct.lower() == "true":
                if where_string:
                    sql = "SELECT DISTINCT {} from {} where ".format(columns, uuid.UUID(tablename).hex) + where_string + "order by {} {}".format(sort_column, sort_type)
                else:
                    sql = "SELECT DISTINCT {} from {} order by {} {}".format(columns, uuid.UUID(tablename).hex, sort_column, sort_type) 
            else:
                if where_string:
                    sql = "SELECT {} from {} where ".format(columns, uuid.UUID(tablename).hex) + where_string + "order by {} {}".format(sort_column, sort_type)

        # Unsorted results
        else:
            log.info("Unsorted results")
            print(columns, flush=True)
            sql = getFieldsFromTables.format(columns, uuid.UUID(tablename).hex)
            print(sql, flush=True)
            if distinct is not None:
                if distinct.lower() == "true": 
                    if where_string:
                        sql = "SELECT DISTINCT {} from {} where ".format(columns, uuid.UUID(tablename).hex) + where_string
                    else:
                        sql = "SELECT DISTINCT {} from {}".format(columns, uuid.UUID(tablename).hex) 
            else:
                if where_string:
                    sql = "SELECT {} from {} where ".format(columns, uuid.UUID(tablename).hex) + where_string
        if offset:
            sql = sql + " OFFSET {} ".format(offset) 
        if limit:
            sql = sql + " LIMIT {} ".format(limit)


        database_output= self.db.engine.execute(sql) 
        data_result_list = []
        for each in database_output:
            data_result_list.append(each)

        final_data = {
                "Data": [list(row) for row in data_result_list]
            }
        
        log.info("Creating lineage information")
        lineage_object = LineageTracker(lineage_json['username'],lineage_json['usergroup'], str(uuid.UUID(tablename)), "", "")
        provenance_response =LineageTrackerApi().read_asset(lineage_object,header)
        

        return make_response (jsonify(final_data), 200)
    
### GET ALL TABLE NAMES -------------------------------------------------------------------------------------

    def get_all_tables(self):

        log.info("Getting the table names")
        database_output= self.db.engine.execute(getAllTableNames, 'public', 'BASE TABLE').fetchall()
        table_uuids = [r[0] for r in database_output]

        final_output = {
                "Table names" : [uuid.UUID(row) for row in table_uuids]
            }

        return make_response (jsonify(final_output), 200) 
        
### COUNT ROWS -------------------------------------------------------------------------------------------------

    def count_rows(self):

        log.info("Counting the rows")

        # Input arguments
        tablename = request.args.get("asset_uuid")
   
        # Checking if the query parameters exist
        if request.args.get("asset_uuid") is None:
            return make_response (jsonify({ "message": "Query parameter 'asset_uuid' is missing", "status": 400} ), 400)
        if request.headers.get("Authorization"):
            header = {"Authorization": request.headers.get("Authorization")}
            access_token = request.headers.get("Authorization").split(' ')[1] 
            lineage_json = IdentityManagerApi().jwt_decode(access_token)
        # Convert UUID format to hex format  
        hex_assetUUID = uuid.UUID(tablename).hex
        
        database_output= self.db.engine.execute(getCountNumberOfRows.format(hex_assetUUID)).fetchall()
        rows = [dict(r) for r in database_output]

        log.info("Creating lineage information")
        lineage_object = LineageTracker(lineage_json['username'],lineage_json['usergroup'], str(uuid.UUID(tablename)), "", "")
        provenance_response =LineageTrackerApi().read_asset(lineage_object,header)
        
        response = {
                "Number of rows": str(rows[0]["count"])
            }
        return make_response(response, 200)

          

### DELETE TABLES ------------------------------------------------------------------------
### Delete all versions of multiple tables from the database
### TODO: Add id not UUID error

    def delete_table(self):
        
        log.info("Deleting the table")

         # Input arguments
        tablename = request.args.get("asset_uuid")

        if request.args.get("asset_uuid") is None:
            return make_response (jsonify({ "message": "Query parameter 'asset_uuid' is missing", "status": 400} ), 400)
        if request.headers.get("Authorization"):
            header = {"Authorization": request.headers.get("Authorization")}
            access_token = request.headers.get("Authorization").split(' ')[1] 
            lineage_json = IdentityManagerApi().jwt_decode(access_token)

        # Delete the table from the assets store
        sql = deleteTableQuery.format(str(uuid.UUID(tablename).hex))
        self.db.engine.execute(sql)
        
        log.info("Creating lineage information")
        lineage_object = LineageTracker(lineage_json['username'],lineage_json['usergroup'], str(uuid.UUID(tablename)), "", "")
        provenance_response =LineageTrackerApi().delete_asset(lineage_object,header)

        # TODO: Adjust according to the json input
        response = {
            "message": "Table deleted",
            "asset_uuid": tablename
        }

        return make_response (jsonify(response), 200)


    



    
