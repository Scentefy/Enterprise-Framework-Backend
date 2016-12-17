"""
# dynamocontroller.py
# Author: Miguel Saavedra
# Date: 10/12/2016
"""

import datetime
import json
import uuid

import boto3
import botocore

class DynamoController(object):
    """ Provides functions for handling dynamo related requests """
    
    @staticmethod
    def get_records(table, parameters):
        """
        Function which is used to fetch all records from a table

        Expected parameter input value
        {
            "request" : "get_records",
            "table_name" : "USER_TABLE",
            "parameters" : {

            }
        }
        """
        action = "Getting items from the " + table + " table"
        try:
            dynamodb = boto3.client("dynamodb")
            items = dynamodb.scan(
                TableName=table, 
                ConsistentRead=True
            )
        except botocore.exceptions.ClientError as e:
            return { 
                "status" : "failed",
                "error_message": e.response["Error"]["Code"],
                "data": {"exception": str(e), "action": action}
            }

        return {"message": "Successfully fetched items", "status" : "success", "data": items["Items"]}

    @staticmethod
    def get_record(table, parameters):
        """
        Function which is used to fetch a specific record using the primary 
        key identifier

        Expected parameter input value
        {
            "request" : "get_record",
            "table_name" : "USER_TABLE",
            "parameters" : {
                "key_name" : "ID",
                "key" : "123" 
            }
        }
        """
        action = "Getting item from the " + table + " table"
        try:
            dynamodb = boto3.client("dynamodb")
            item = dynamodb.get_item(
                TableName=table, Key={ parameters["key_name"] : {"S": parameters["key"]}}
            )
        except botocore.exceptions.ClientError as e:
            return { 
                "status" : "failed",
                "error_message": e.response["Error"]["Code"],
                "data": {"exception": str(e), "action": action}
            }
        if not "Item" in item:
            return {
                "status" : "failed",
                "error": "InvalidItemSelection",
                "data": {"key": parameters["key"],  "action": action}}
            
        return {"message": "Successfully fetched item", "status" : "success", "data": items["Item"]}
    
    @staticmethod
    def put_record(table, parameters):
        """
        Function which is used to insert a record into the respective dynamo table

        Expected parameter input value
        {
            "request" : "put_record",
            "table_name" : "USER_TABLE",
            "parameters" : {
                "Email" : { "S" :"example_email@emai.com"},
                "ID" : { "S": "123" },
                "Password" : { "S": "this will be hashed and salted here" },
                "Role" : { "S": "admin" },
                "Username" : { "S": "john123" }
            }
        }
        """
        try:
            dynamodb = boto3.client("dynamodb")
            put_response = dynamodb.put_item(
                TableName=table, Item=parameters, ReturnConsumedCapacity="TOTAL"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting item in the " + table + " table"
            return { 
                "status" : "failed",
                "error_message": e.response["Error"]["Code"],
                "data": {"exception": str(e), "action": action}
            }

        return {"message": "Successfully put item", "status" : "success", "data": parameters}

    @staticmethod
    def remove_record(table, parameters):
        """
        Function which is used to remove a record into the respective dynamo table
        using a key identifier

        Expected parameter input value
        {
            "request" : "remove_record",
            "table_name" : "USER_TABLE",
            "parameters" : {
                "key_name" : "ID",
                "key" : "123" 
            }
        }
        """
        try:
            dynamodb = boto3.client("dynamodb")
            delete_response = dynamodb.delete_item(
                TableName=table,
                Key={ parameters["key_name"] : {"S": parameters["key"]}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Removing item in the " + table + " table"
            return { 
                "status" : "failed",
                "error_message": e.response["Error"]["Code"],
                "data": {"exception": str(e), "action": action}
            }

        return {"message": "Successfully removed item", "status" : "success"}
        