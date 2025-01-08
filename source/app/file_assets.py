from io import BytesIO
from flask import Flask, jsonify, request, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from sql_scripts import*
from table_ops import*
from log import*
import uuid,os
import json, psycopg2
from identity_manager import *
import sqlalchemy

# Handles all operations on datasets stored as files
class FileAssets():

    log = setup_logging()

    # Assigning an asset_type
    asset_type = "dataset"

    def __init__(self, db:SQLAlchemy) -> None:
        self.db = db
        pass
    

### CREATE FILE ------------------------------------------------------------------------
### Create a new file --------------------------------

    def create_file(self):

        input_file = request.files['file'].read()
        # Checking if the required input parameters exist
        if input_file == b'':
            return make_response (jsonify({ "message": "File is missing. Add file as a formdata paramater 'file'", "status": 400} ), 400)
        if request.headers.get("Authorization"):
            header = {"Authorization": request.headers.get("Authorization")}
            access_token = request.headers.get("Authorization").split(' ')[1] 
            lineage_json = IdentityManagerApi().jwt_decode(access_token)
            # print(lineage_json, flush=True)

        # Input arguments
        # input_file = request.files['file'].read()
        file_name = request.files["file"].filename
        name, extension = os.path.splitext(file_name)
        # print(len(input_file), flush=True)

        # Adding extension to add UUID in the PostgreSQL database
        self.db.engine.execute(initializeUUIDQuery) 
        
        # Check if the table for asset_type exists in the database, if not, create the table
        check_table = self.db.engine.execute(sqlalchemy.text(tableExistsQuery), self.asset_type)
        result_table_exists = [dict(row) for row in check_table]
        if ([d['exists'] for d in result_table_exists].pop()) is False:
            self.log.info("Table does not exist, creating table")
            self.db.engine.execute(createTableQuery.format(self.asset_type))

        # Add the new file into the table
        self.log.info("Creating a new file")
        new_fileUUID = uuid.uuid4().hex
        self.log.info("Inserting the file")
        self.db.engine.execute(insertFileQuery.format(self.asset_type), new_fileUUID, str(file_name),(psycopg2.Binary(input_file)))
        
        try:
            log.info("Creating lineage information")
            lineage_object = LineageTracker(lineage_json['username'],lineage_json['usergroup'],str(uuid.UUID(new_fileUUID)),str(file_name),"")
            provenance_response =LineageTrackerApi().create_asset(lineage_object, header)
            if provenance_response.status_code == 200:
                response = create_response("New dataset created in the Data Storage and lineage created in the Lineage Tracker",new_fileUUID, 200)
                return make_response (jsonify(response), 200)
            else:
                return make_response (jsonify({'message': provenance_response.text}), provenance_response.status_code)
        except:
                return make_response (jsonify({'message': "Cannot create lineage info of the dataset"}), 500)

    
    

### UPDATE A FILE----------------------------------------------------------------------------------
### Adds a new file in the database with a new UUID and the UUIDs are linked through lineage--------------------------------------------------
### BUG: The file is updated even if the file is not attached in postman


    def update_file(self):

        # Checking if the required input parameters exist
        # If the file is being read again, make the file pointer move to zero by input_file.seek(0)
        input_file = request.files['file'].read()
        if input_file == b'':
            return make_response (jsonify({ "message": "File is missing. Add file as a formdata paramater 'file'", "status": 400} ), 400)
        if request.args.get("asset_uuid") is None:
            return make_response (jsonify({ "message": "Query parameter 'asset_uuid' is missing", "status": 400} ), 400)
        if request.headers.get("Authorization"):
            header = {"Authorization": request.headers.get("Authorization")} 
            access_token = request.headers.get("Authorization").split(' ')[1] 
            lineage_json = IdentityManagerApi().jwt_decode(access_token)

        # Input arguments
        asset_uuid = request.args.get("asset_uuid")
        # input_file = request.files['file'].read()
        file_name = request.files["file"].filename
        name, extension = os.path.splitext(file_name)
        # print(len(input_file), flush=True)

        # Check if the requested file exists in the database
        # sql1 = checkFileExists.format(self.asset_type, asset_uuid)
        database_response = self.db.engine.execute(checkFileExists.format(self.asset_type), asset_uuid)
        result_file_exists = [dict(row) for row in database_response]
        if result_file_exists[0].get('exists') is True:
            self.log.info("File exists in the data storage, updating the file")

            # Add the new file into the table
            new_fileUUID = uuid.uuid4().hex
            self.db.engine.execute(insertFileQuery.format(self.asset_type), new_fileUUID, str(file_name), (psycopg2.Binary(input_file)))

            log.info("Creating lineage information")
            lineage_object = LineageTracker(lineage_json['username'],lineage_json['usergroup'], str(uuid.UUID(new_fileUUID)),"", str(uuid.UUID(asset_uuid)))
            provenance_response =LineageTrackerApi().update_asset(lineage_object, "File updated",header)
            response = create_response("File updated and lineage created in the lineage tracker",str(uuid.UUID(new_fileUUID)),200)
        else :
            response = create_response("The requested file does not exist".format(self.asset_type.upper()),asset_uuid,400)

        return make_response (jsonify(response),response["status_code"])

###  GET FILE ------------------------------------------------------------------------
    
    def get_file(self):
        
        # Checking if the required input parameters exist
        if request.args.get("asset_uuid") is None:
            return make_response (jsonify({ "message": "Query parameter 'asset_uuid' is missing", "status": 400} ), 400)
        if request.headers.get("Authorization"):
            header = {"Authorization": request.headers.get("Authorization")} 
            access_token = request.headers.get("Authorization").split(' ')[1] 
            lineage_json = IdentityManagerApi().jwt_decode(access_token)
        
        # Input arguments
        asset_uuid = request.args.get("asset_uuid")

        output_file = []

        # Check if the file exists in the database 
        database_response = self.db.engine.execute(checkFileExists.format(self.asset_type),asset_uuid )
        result_file_exists = [dict(row) for row in database_response]
        if ([d['exists'] for d in result_file_exists].pop()) is True:
            self.log.info("File exists in the data storage, fetching the file")
            
            # Get the file
            # sql = getFileQuery.format(self.asset_type, asset_uuid)
            database_output =self.db.engine.execute(getFileQuery.format(self.asset_type), asset_uuid )

            log.info("Creating lineage information")
            lineage_object = LineageTracker(lineage_json['username'],lineage_json['usergroup'], str(uuid.UUID(asset_uuid)), "", "")
            provenance_response =LineageTrackerApi().read_asset(lineage_object, header)

            for each in database_output:
                output_file.append(list(each))
            return send_file(BytesIO(output_file[0][0]), download_name=str(output_file[0][1]), as_attachment = True )
        else :
            response = create_response("The requested file does not exist",asset_uuid,400)

        return make_response (jsonify(response),response["status_code"])

           

###  GET ALL FILE NAMES ------------------------------------------------------------------------
 
    def get_all_names(self):
    
        self.log.info("Getting a list of file names")
        
        # Query all distinct assetUUDs from the table
        database_output = self.db.engine.execute(getAllIds.format(self.asset_type))
        list_ids = [dict(row) for row in database_output]
        allfiles = [str(d['id']) for d in list_ids]

        output_file = [] 
        for value in allfiles:
            database_output = self.db.engine.execute(getFileName.format(self.asset_type), value)
            for each in database_output:
                name, extension = os.path.splitext(each[1])
                result_entry = {
                    "uuid" : each[0],
                    "name" : each[1],
                    "type": extension[1:]
                }
                output_file.append(result_entry)
        output_name = self.asset_type + "s"
        response = {
            output_name : output_file
        }

        return make_response (jsonify(response), 200)

###  RENAME FILE ------------------------------------------------------------------------

    def rename_file(self):

        # Checking if the required input parameters exist
        if request.args.get("asset_uuid") is None:
            return make_response (jsonify({ "message": "Query parameter 'asset_uuid' is missing", "status": 400} ), 400)
        if request.args.get("file_name") is None:
            return make_response (jsonify({ "message": "Query parameter 'file_name' is missing", "status": 400} ), 400)
     
        # Input arguments
        asset_uuid = request.args.get("asset_uuid")
        new_name = request.args.get("file_name")
        
        # Checking if the name is provided with an extension so the file does not get corrupted
        name, extension = os.path.splitext(new_name)
        if not extension:
            response = create_response("The file extension is missing, this will corrupt the file",asset_uuid,400)
            return make_response (jsonify(response),response["status_code"])
   
        # Check if the requested file exists in the database
        # sql1 = checkFileExists.format(self.asset_type, asset_uuid)
        database_response = self.db.engine.execute(checkFileExists.format(self.asset_type), asset_uuid)
        result_file_exists = [dict(row) for row in database_response]
        if ([d['exists'] for d in result_file_exists].pop()) is True:
            self.log.info("File exists in the data storage, renaming the file")
            
            # Update the file name
            # sql2 = updateFileName.format(self.asset_type, new_name, asset_uuid)
            self.db.engine.execute(updateFileName.format(self.asset_type), new_name, asset_uuid)                              
            response = create_response("File name changed to {}".format(new_name),asset_uuid,200)

        else :
            response = create_response("Requested file does not exist",asset_uuid,400)

        return make_response (jsonify(response),response["status_code"])


###  DELETE A FILE ------------------------------------------------------------------------
### Deleting a file---------------------------------------------------------

    def delete_file(self):
   
        # Checking if the required input parameters exist
        if request.args.get("asset_uuid") is None:
            return make_response (jsonify({ "message": "Query parameter 'asset_uuid' is missing", "status": 400} ), 400)
        if request.headers.get("Authorization"):
            header = {"Authorization": request.headers.get("Authorization")} 
            access_token = request.headers.get("Authorization").split(' ')[1] 
            lineage_json = IdentityManagerApi().jwt_decode(access_token)

        # Input arguments
        asset_uuid = request.args.get('asset_uuid')
            
        # sql1 = checkFileExists.format(self.asset_type, asset_uuid)
        database_response = self.db.engine.execute(checkFileExists.format(self.asset_type), asset_uuid )
        result_file_exists = [dict(row) for row in database_response]

        if ([d['exists'] for d in result_file_exists].pop()) is True:
            
            self.log.info("File exists in the data storage, deleting the file")
            # sql2 = deleteFileQuery.format(self.asset_type, asset_uuid)
            self.db.engine.execute(deleteFileQuery.format(self.asset_type), asset_uuid)

            log.info("Creating lineage information")
            lineage_object = LineageTracker(lineage_json['username'],lineage_json['usergroup'], str(uuid.UUID(asset_uuid)), "", "")
            provenance_response =LineageTrackerApi().delete_asset(lineage_object,header)
            if provenance_response.status_code == 200:
                response = create_response("File and lineage info of the file deleted ",asset_uuid,200)
            else:
                return make_response (jsonify({'message': provenance_response.text}), provenance_response.status_code)
        else :
            response = create_response("The requested file does not exist",asset_uuid,400)


        return make_response (jsonify(response),response["status_code"])



