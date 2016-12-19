"""
# controller.py
# Author: Miguel Saavedra
# Date: 10/12/2016
"""

import json

import boto3
import botocore

from error              import Error
from security           import Security
from user               import User
from dynamocontroller   import DynamoController

def handler(event, context):
    # Uncomment this to view parameters sent to the back end from the post
    # return json.dumps(event)

    # Get info on the cms' resources from the constants file
    with open("constants.json", "r") as resources_file:
        resources = json.loads(resources_file.read())

    # Function dispatcher dictionary
    functions = {
        "get_records" : DynamoController.get_records,
        "get_records_query" : DynamoController.get_records_query,
        "get_record" : DynamoController.get_record,
        "put_record" : DynamoController.put_record,
        "remove_record" : DynamoController.remove_record,
        "edit_record" : DynamoController.put_record,
		"login" : Security.login,
		"logout" : Security.logout
     }
    
    # Extract the request body
    request_body = event["body"]
    
    # Check that a request is included
    if "request" in request_body:
        request = request_body["request"]
    else:
        # Throw an error
        Error.send_error("noRequest")
    
    # Run Dynamo if request is supported
    if request in functions:
        return functions[request](resources[request_body["table_name"]], request_body["parameters"])
    else:
        Error.send_error("unsupportedRequest", data={"request": request})