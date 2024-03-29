"""
# user.py
# Author: Adam Campbell
# Date: 23/06/2016
# Edited: N/D        | Miguel Saavedra
#         02/08/2016 | Christopher Treadgold
#         05/08/2016 | Adam Campbell
#         07/08/2016 | Christopher Treadgold
#         21/08/2016 | Christopher Treadgold
#         10/09/2016 | Christopher Treadgold
"""

import datetime
import uuid

import boto3
import botocore
from passlib.hash import pbkdf2_sha256

class User(object):
    """ Provides functions for handling user related requests """
    HASH_ROUNDS = 10000 # The number of rounds to use for hashing passwords
    
    @staticmethod
    def get_all_users(user_table):
        """ Fetches all entries from the user table """
        try:
            dynamodb = boto3.client("dynamodb")
            users = dynamodb.scan(
                TableName=user_table, ConsistentRead=True,
                ProjectionExpression="Email, Username, ID, #R",
                ExpressionAttributeNames={
                    "#R": "Role"
                }
            )
        except botocore.exceptions.ClientError as e:
            action = "Getting all users"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the email has a user associated with it
        if not "Items" in users:
            action = "Fetching users from the user table"
            return {"error": "noUsers",
                    "data": {"action": action}}
        
        users = users["Items"]
        
        return {"message": "Successfully fetched users", "data": users}
    
    @staticmethod
    def get_user(email, user_table):
        """ Fetches a user entry from the user table """
        try:
            dynamodb = boto3.client("dynamodb")
            user = dynamodb.get_item(
                TableName=user_table, Key={"Email": {"S": email}},
                ProjectionExpression="Email, Username, ID, #R",
                ExpressionAttributeNames={
                    "#R": "Role"
                }
            )
        except botocore.exceptions.ClientError as e:
            action = "Fetching user from the user table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the email has a user associated with it
        if not "Item" in user:
            action = "Fetching user from the user table"
            return {"error": "InvalidEmail",
                    "data": {"email": email, "action": action}}
        
        user = user["Item"]
        
        return {"message": "Successfully fetched user", "data": user}
    
    @staticmethod
    def get_user_from_id(user_id, user_table):
        """ Fetches a user entry from the user table """
        try:
            dynamodb = boto3.client("dynamodb")
            user = dynamodb.scan(
                TableName=user_table,
                FilterExpression="ID = :id",
                ExpressionAttributeValues={
                    ":id": {"S": user_id}
                },
                ProjectionExpression="Email, Username, ID, #R",
                ExpressionAttributeNames={
                    "#R": "Role"
                }
            )
        except botocore.exceptions.ClientError as e:
            action = "Fetching user from the user table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the email has a user associated with it
        if not "Items" in user:
            action = "Fetching user from the user table"
            return {"error": "InvalidUserId",
                    "data": {"userId": user_id, "action": action}}
        
        user = user["Items"][0]
        
        return {"message": "Successfully fetched user", "data": user}
        
    @staticmethod
    def put_user(email, username, password, role_name, user_table):
        """ Puts a user in the user table """
        # Hash the password
        hashed_pass = pbkdf2_sha256.encrypt(password,
                                            rounds=User.HASH_ROUNDS)
        # Create the user entry
        user = {
            "Email": {"S": email},
            "Username": {"S": username},
            "Password": {"S": hashed_pass},
            "ID": {"S": str(uuid.uuid4())},
            "Role": {"S": role_name}
        }
        
        # Put the user in the user table
        try:
            dynamodb = boto3.client("dynamodb")
            put_response = dynamodb.put_item(
                TableName=user_table, Item=user, ReturnConsumedCapacity="TOTAL"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting user in the user table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully put user", "data": user}

    @staticmethod
    def delete_user(email, user_table):
        """ Deletes a user from the user table """
        try:
            dynamodb = boto3.client("dynamodb")
            delete_response = dynamodb.delete_item(
                TableName=user_table,
                Key={"Email": {"S": email}},
                ConditionExpression="attribute_exists(Email)"
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting user from the user table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully deleted user"}
    
    @staticmethod
    def get_all_roles(role_table):
        """ Fetches all entries from the role table """
        try:
            dynamodb = boto3.client("dynamodb")
            roles = dynamodb.scan(
                TableName=role_table, ConsistentRead=True
            )
        except botocore.exceptions.ClientError as e:
            action = "Getting all roles"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the email has a user associated with it
        if not "Items" in roles:
            action = "Fetching roless from the role table"
            return {"error": "noRoles",
                    "data": {"action": action}}
        
        roles = roles["Items"]
        
        return {"message": "Successfully fetched roles", "data": roles}
    
    @staticmethod
    def get_role(role_name, role_table):
        """ Fetches a role entry from the role table """
        try:
            dynamodb = boto3.client("dynamodb")
            role = dynamodb.get_item(
                TableName=role_table, Key={"RoleName": {"S": role_name}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Fetching role from the role table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the email has a user associated with it
        if not "Item" in role:
            action = "Fetching role from the role table"
            return {"error": "InvalidRoleName",
                    "data": {"roleName": role_name, "action": action}}
        
        role = role["Item"]
        
        return {"message": "Successfully fetched role", "data": role}
    
    @staticmethod
    def put_role(role_name, permissions, role_table):
        """ Puts a role in the role table """
        # Create the role entry
        role = {
            "RoleName": {"S": role_name},
            "Permissions": {"SS": permissions}
        }
        
        # Put the role in the role table
        try:
            dynamodb = boto3.client("dynamodb")
            put_response = dynamodb.put_item(
                TableName=role_table, Item=role, ReturnConsumedCapacity="TOTAL"
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting role in the role table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully put role", "data": role}
    
    @staticmethod
    def delete_role(role_name, role_table):
        """ Deletes a role from the role table """
        try:
            dynamodb = boto3.client("dynamodb")
            delete_response = dynamodb.delete_item(
                TableName=role_table,
                Key={"RoleName": {"S": role_name}},
                ConditionExpression="attribute_exists(RoleName)"
            )
        except botocore.exceptions.ClientError as e:
            action = "Deleting role from the role table"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully deleted role"}