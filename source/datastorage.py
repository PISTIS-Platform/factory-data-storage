from functools import wraps
from sqlite3 import OperationalError, ProgrammingError
from flask_swagger_ui import get_swaggerui_blueprint
from database_config import Config
from identity_manager import *
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.exc import DataError
from psycopg2 import OperationalError
from werkzeug.exceptions import HTTPException
from app.tabular_assets import*
from app.file_assets import *
from flask_cors import CORS


#TODO: Add a wrong url error 

### Initialize Flask app and SQLalchmey database

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['CORS_SUPPORTS_CREDENTIALS']= True
app.config.from_object(Config)
app.debug = True
db = SQLAlchemy(app)
db2 = db.get_engine(app, 'two')

### ------------------------------------------------------

### Swagger specification
# SWAGGER_URL = ''
# API_URL = '/static/swagger.json'
SWAGGER_URL = '/srv/factory-data-storage'
API_URL = '/srv/factory-data-storage/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "PISTIS Data Factory Storage"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix='/')

### Authorization specification

def token_required(f):
    '''decorator function to check tokens in header'''
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.headers.get("Authorization")
        # if token == "3yF8!oNEzR2/bHDx*WU#F@^pLM9NQ$a6":      
        #     return f(*args,**kwargs)
        if token and token.startswith('Bearer '):
            # print("its a bearer token", flush=True)
            identity_object = IdentityManager('application/x-www-form-urlencoded', 'urn:ietf:params:oauth:grant-type:uma-ticket', '')
            response =IdentityManagerApi().user_account_authorize(identity_object,token.split(' ')[1])
            if response.status_code != 200:
                return make_response (jsonify({'message': 'Unauthorized access.'}), 401)
        else:             
            return make_response (jsonify({'message': 'API Key or token is missing, authentication failed'}), 401)
        
        return f(*args,**kwargs)
    return wrapped


### Error handling function

@app.errorhandler(Exception)
def handleInternalError(e):

    if type(e) is ProgrammingError: 
        return make_response (jsonify({"message": "The input data provided is wrong or is not in the right format {} ".format(str(e))}), 500)

    elif type(e) is DataError: 
        if  'invalid input syntax' in str(e)  :
            return make_response (jsonify({"message": 'Database Error, Check the input data {}'.format(str(e))}), 503)
        else:
            return make_response (jsonify({"message":'Database Error, Check the input data {} '.format(str(e))}), 500)

    elif type(e) is OperationalError: 
        return make_response (jsonify({"message": 'Database configuration has failed {} '.format(str(e))}), 500)


    elif isinstance(e, HTTPException):
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "message": e.description,
        })
        response.content_type = "application/json"
        return make_response(response)
    
    else:
        return make_response (jsonify({"message": '500 - Internal Server Error: {}, {}'.format(type(e), str(e))}), 500)



### ------------------------------------------------------------------------------------------------------
### Databases

tabularAssetsHandler = TabularAssets(db)
fileAssetsHandler = FileAssets(db2)

### TABULAR STORE API--------------------------------------------------------------------------------------  

@app.route('/api/tables/create_table', methods=['POST'])
@token_required
def create_table():   
    return tabularAssetsHandler.create_table()

@app.route('/api/tables/get_all_tables', methods=['GET'])
@token_required
def get_all_tables():   
    return tabularAssetsHandler.get_all_tables()

@app.route('/api/tables/add_rows', methods=['PUT'])
@token_required
def add_rows():    
    return tabularAssetsHandler.add_rows()

@app.route('/api/tables/get_table', methods=['GET'])
@token_required
def get_table():    
    return tabularAssetsHandler.get_table()

@app.route('/api/tables/get_fields', methods=['POST'])
@token_required
def get_fields():    
    return tabularAssetsHandler.get_fields()

@app.route('/api/tables/download_table', methods=['GET'])
@token_required
def download_table():    
    return tabularAssetsHandler.download_table()

@app.route('/api/tables/count_rows', methods=['GET'])
@token_required
def count_rows():    
    return tabularAssetsHandler.count_rows()

@app.route('/api/tables/delete_table', methods=['DELETE'])
@token_required
def delete_tables():
    return tabularAssetsHandler.delete_table()


### ----------------------------------------------------------------------------------------------------

### FILE STORE API--------------------------------------------------------------------------------------  

@app.route('/api/files/create_file', methods=['POST'])
@token_required
def create_file():
    return fileAssetsHandler.create_file()

@app.route('/api/files/update_file', methods=['PUT'])
@token_required
def update_file():    
    return fileAssetsHandler.update_file()

@app.route('/api/files/get_file', methods=['GET'])
@token_required
def get_file():
    return fileAssetsHandler.get_file()

@app.route('/api/files/get_all_names', methods=['GET'])
@token_required
def get_all_names():
    return fileAssetsHandler.get_all_names()


@app.route('/api/files/rename_file', methods=['PUT'])
@token_required
def rename_file():
    return fileAssetsHandler.rename_file()

@app.route('/api/files/delete_file', methods=['DELETE'])
@token_required
def delete_file():
    return fileAssetsHandler.delete_file()


### ------------------------------------------------------------------------------------




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port= 8080)