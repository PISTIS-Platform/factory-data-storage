#lineage_engine.py
# TODO: need to define what results in an update

from dataclasses import dataclass
import time, os, requests
from identity_manager import *

LINEAGE_TRACKER_URL = os.getenv('LINEAGE TRACKER','https://develop.pistis-market.eu/srv/lineage-tracker')
##TODO: remove when lineage tracker adds authorization
api_key = "3yF8!oNEzR2/bHDx*WU#F@^pLM9NQ$a6"

@dataclass
class LineageTracker():
    username:str
    user_group:str
    uuid:str
    dataset_name:str
    uuid_prev:str

class LineageTrackerApi ():

    def authorization_token(self):
        identity_object = IdentityManager('application/x-www-form-urlencoded', 'password', '')
        keycloak_response = IdentityManagerApi().user_account_authenticate(identity_object)
        access_token = keycloak_response.json()["access_token"]
        return access_token

    def create_asset(self,lineage_object,header):

        # header = {"Authorization": 'Bearer '+ self.authorization_token()} 
        # header = {"Authorization": api_key} 

        lineage_entry = {
            "username": lineage_object.username,
            "user_group": lineage_object.user_group,
            "uuid": lineage_object.uuid,
            "dataset_name": lineage_object.dataset_name
            }
        
        lineage_response = requests.post(LINEAGE_TRACKER_URL+"/create_dataset", json=lineage_entry,headers=header)
        print(f"lineage_response: {lineage_response.status_code}")
        print(f"lineage_response: {lineage_response.text}")
        return lineage_response


    def update_asset(self, lineage_object, update_description, header):

        # header = {"Authorization": 'Bearer '+ self.authorization_token()} 

        header = {"Authorization": api_key} 

        lineage_entry = {
            "username": lineage_object.username,
            "user_group": lineage_object.user_group,
            "uuid": lineage_object.uuid,
            "uuid_prev": lineage_object.uuid_prev,
            "update_description": update_description
            }

        lineage_response = requests.post(LINEAGE_TRACKER_URL+"/update_dataset", json=lineage_entry,headers=header)

        return lineage_response


    def read_asset(self, lineage_object, header):

        # header = {"Authorization": 'Bearer '+ self.authorization_token()} 

        # header = {"Authorization": api_key} 

        lineage_entry =  {
            "username": lineage_object.username,
            "user_group": lineage_object.user_group,
            "uuid": lineage_object.uuid
            }
        
        lineage_response = requests.post(LINEAGE_TRACKER_URL+"/read_dataset", json=lineage_entry,headers=header)

        return lineage_response
     

    def delete_asset(self, lineage_object, header):

        # header = {"Authorization": 'Bearer '+ self.authorization_token()} 

        # header = {"Authorization": api_key} 
        lineage_entry =  {
            "username": lineage_object.username,
            "user_group": lineage_object.user_group,
            "uuid": lineage_object.uuid,
            }
        
        print(lineage_entry, flush=True)
        lineage_response = requests.post(LINEAGE_TRACKER_URL+"/delete_dataset", json=lineage_entry,headers=header)
        return lineage_response


