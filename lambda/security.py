"""
# security.py
# Author: Miguel Saavedra
# Date: 05/08/2016
# Edited: 11/10/2016 | Miguel Saavedra
"""

import datetime
import uuid
import json

import boto3
import botocore
from dynamocontroller   import DynamoController
from passlib.hash import pbkdf2_sha256

class Security(object):
    """ Provides a function for authentication and authorization of requests
    through a provided token.
    """
    
    @staticmethod
    def login(table_name, parameters):
        """ Validates a user login request.
            Adds a token to the token table and provides it as a cookie in the
            response for use in future request validation.

            Expected parameter input value
            {
                "request" : "login",
                "table_name" : "USER_TABLE",
                "parameters" : {
                    "username" : "mack123",
                    "password" : "hello123"
                }
            }
        """  
        # Get info on the cms' resources from the constants file
        with open("constants.json", "r") as resources_file:
            resources = json.loads(resources_file.read())

        # Use username to fetch user information from the user table
        try:
            dynamodb = boto3.client("dynamodb")
            user = dynamodb.get_item(TableName=table_name, Key={"Username" : {"S": parameters["username"]}})
        except botocore.exceptions.ClientError as e:
            action = "Fetching user from the user table for login"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Check that the username has a user associated with it
        if not "Item" in user:
            action = "Attempting to log in"
            return {"error": "invalidUsername",
                    "data": {"username": parameters["username"], "action": action}}
        
        user = user["Item"]
                    
        # Check that the role has a user associated with it
        # if not "Role" in user:
        #     action = "Attempting to log in"
        #     return {"error": "userHasNoRole",
        #             "data": {"user": user, "action": action}}
        
        # Check that the user has a password associated with it
        if not "Password" in user:
            action = "Attempting to log in"
            return {"error": "userHasNoPassword",
                    "data": {"user": user, "action": action}}
        
        actual_password = user["Password"]["S"]
        
        # Verify that the password provided is correct
        valid_password = pbkdf2_sha256.verify(parameters["password"], actual_password)
        if not valid_password:
            action = "Attempting to log in"
            return {"error": "invalidPassword",
                    "data": {"password": parameters["password"], "action": action}}
        
        # Calculate an exiration date a day from now
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        expiration = expiration.strftime("%a, %d-%b-%Y %H:%M:%S UTC")
        # Generate a uuid for use as a token
        token = str(uuid.uuid4())
        
        # Add the generated token to the token table
        try:
            dynamodb.put_item(
                TableName=resources["TOKEN_TABLE"],
                Item={"Token": {"S": token},
                      "Username": {"S": parameters["username"]},
                      "Expiration": {"S": expiration}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Putting token in the token table for login"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Create the cookie that will be returned
        cookie = "token=%s; expires=%s" % (token, expiration)
        # Return the cookie
        return {"message": "Successfully logged in", "Set-Cookie": cookie}
    
    @staticmethod
    def logout(token, token_table):
        """ Logs out the user who made this request by removing their active
        token from the token table
        """
        try:
            dynamodb = boto3.client("dynamodb")
            delete_response = dynamodb.delete_item(
                TableName=token_table, Key={"Token": {"S": token}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Logging out user"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}

        return {"message": "Successfully logged out"}
    
    @staticmethod
    def authenticate(token, request, token_table, user_table, role_table):
        """
        Function which checks if the user has an active session with system
        by checking if the user has a token
        """
        pass

    @staticmethod
    def authorize(token, request, token_table, user_table, role_table):
        """
        Function checks if the user is allowed to perform the request
        """
        pass

    @staticmethod
    def authenticate_and_authorize(token, request, token_table, user_table,
                                   role_table):
        """ Authenticates a token and checks that the associated user has the
        rights to be making a provided request.
        """
        # Get a dynamodb client object from boto3
        try:
            dynamodb = boto3.client('dynamodb')
        except botocore.exceptions.ClientError as e:
            action = "Getting dynamodb client"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Get Token info
        token_info = Security.get_token_info(token_table, token, dynamodb)
        
        # Check that the token has an entry in the database associated with it
        if not "Item" in token_info:
            action = "Validating token"
            return {"error": "invalidToken",
                    "data": {"token": token, "action": action}}
        
        token_info = token_info["Item"]
        
        # Checks if request is logoutUser as permission is not required
        if request == "logoutUser":
            return True
        
        # Checks that the token has an expiration date
        if not "Expiration" in token_info:
            action = "Validating token"
            return {"error": "invalidTokenNoExpiration",
                    "data": {"token": token, "action": action}}
                    
        token_expiration = token_info["Expiration"]["S"]
        
        # Check that the token is not expired
        if not token_expiration == "None":
            expiration = datetime.datetime.strptime(token_expiration,
                                                    "%a, %d-%b-%Y %H:%M:%S UTC")
            if expiration < datetime.datetime.utcnow():
                action = "Validating token"
                return {"error": "expiredToken",
                        "data": {"token": token, "action": action}}
            
        # Check that the token has a user associated with it
        try:
            user_email = token_info["UserEmail"]["S"]
        except KeyError:
            action = "Fetching user from the user table for authorization"
            return {"error": "tokenHasNoUser",
                    "data": {"token": token, "action": action}}
        
        # Get user Information from the user table
        user_info = Security.get_user_info(user_table, user_email, dynamodb)

        # Check that the user id has an entry in the database associated with it
        if not "Item" in user_info:
            action = "Fetching user from the user table for authorization"
            return {"error": "invalidUserAssociatedWithToken",
                    "data": {"user": user_email, "action": action}}

        # Extract Item from dynamo response
        user_info = user_info["Item"]

        # Check that the user has a role associated with it
        if not "Role" in user_info:
            action = "Fetching user from the user table for authorization"
            return {"error": "userHasNoRole",
                    "data": {"user": user_email, "action": action}}
        
        user_role = user_info["Role"]["S"]

        # Query the role table for the role extracted from the user
        role_info = Security.get_role_info(role_table, user_role, dynamodb)

        # Check for return of item or items
        if not role_info.get("Items") is None:
            collectionName = "Items"
        elif not role_info.get("Item") is None:
            collectionName = "Item"

        # Get collection out of dynamo reponse value
        role_info = role_info[collectionName]
            
        role_permissions = role_info["Permissions"]["SS"]

        # Check that the user is authorized to perform the request
        if not request == "getPermissions":
            if request in role_permissions or "all" in role_permissions:
                user_info["Permissions"] = role_permissions
                return user_info
        else:
            user_info["Permissions"] = ["getPermissions"];
            return user_info

        # Return error as user did not pass permissions check
        return {"error": "notAuthorizedForRequest",
                "data": {"user": user_email, "request": request}}

    
    @staticmethod
    def get_permissions(token, request, token_table, user_table, role_table):
        """ Function Checks the user permissions by their token and returns 
        the permissions as an array 
        """
        # Get a dynamodb client object from boto3
        try:
            dynamodb = boto3.client('dynamodb')
        except botocore.exceptions.ClientError as e:
            action = "Getting dynamodb client"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        
        # Get Token info
        token_info = Security.get_token_info(token_table, token, dynamodb)
        
        # Check that the token has an entry in the database associated with it
        if not "Item" in token_info:
            action = "Validating token"
            return {"error": "invalidToken",
                    "data": {"token": token, "action": action}}
        
        token_info = token_info["Item"]
        
        # Checks if request is logoutUser as permission is not required
        if request == "logoutUser":
            return True
        
        # Checks that the token has an expiration date
        if not "Expiration" in token_info:
            action = "Validating token"
            return {"error": "invalidTokenNoExpiration",
                    "data": {"token": token, "action": action}}
                    
        token_expiration = token_info["Expiration"]["S"]
        
        # Check that the token is not expired
        if not token_expiration == "None":
            expiration = datetime.datetime.strptime(token_expiration,
                                                    "%a, %d-%b-%Y %H:%M:%S UTC")
            if expiration < datetime.datetime.utcnow():
                action = "Validating token"
                return {"error": "expiredToken",
                        "data": {"token": token, "action": action}}
            
        # Check that the token has a user associated with it
        try:
            user_email = token_info["UserEmail"]["S"]
        except KeyError:
            action = "Fetching user from the user table for authorization"
            return {"error": "tokenHasNoUser",
                    "data": {"token": token, "action": action}}
        
        # Get user Information from the user table
        user_info = Security.get_user_info(user_table, user_email, dynamodb)

        # Check that the user id has an entry in the database associated with it
        if not "Item" in user_info:
            action = "Fetching user from the user table for authorization"
            return {"error": "invalidUserAssociatedWithToken",
                    "data": {"user": user_email, "action": action}}

        # Extract Item from dynamo response
        user_info = user_info["Item"]

        # Check that the user has a role associated with it
        if not "Role" in user_info:
            action = "Fetching user from the user table for authorization"
            return {"error": "userHasNoRole",
                    "data": {"user": user_email, "action": action}}
        
        user_role = user_info["Role"]["S"]

        # Query the role table for the role extracted from the user
        role_info = Security.get_role_info(role_table, user_role, dynamodb)

        # Check for return of item or items
        if not role_info.get("Items") is None:
            collectionName = "Items"
        elif not role_info.get("Item") is None:
            collectionName = "Item"

        # Check that the role name has a role associated with it
        if not collectionName in role_info:
            action = "Fetching role from the role table for authorization"
            return {"error": "invalidRoleAssociatedWithUser",
                    "data": {"user": user_email, "action": action}}

        role_info = role_info[collectionName]
                    
        # Check that the role has permissions
        if not "Permissions" in role_info:
            action = "Fetching role from the role table for authorization"
            return {"error": "roleHasNoPermissions",
                    "data": {"user": user_email, "action": action}}
        
        return {"message": "Successfully fetched permissions", "data": role_info["Permissions"]["SS"]}

        return {"error": "RoleFormatError",
                    "data": {"user": user_email, "action": action}}

    @staticmethod
    def get_user_info(user_table, user_email, dynamodb):
        # Query the user table for the user id extracted from the token table
        try:
            user_info = dynamodb.get_item(
                TableName=user_table,
                Key={"Email": {"S": user_email}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Querying the user table for authorization"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        return user_info

    @staticmethod
    def get_token_info(token_table, token, dynamodb):
        # Fetch token information from the token table
        try:
            token_info = dynamodb.get_item(TableName=token_table,
                                            Key={"Token": {"S": token}})
        except botocore.exceptions.ClientError as e:
            action = "Fetching token from the token table for authentication"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        return token_info

    @staticmethod
    def get_role_info(role_table, user_role, dynamodb):
        # Query the role table for the role extracted from the user
        try:
            role_info = dynamodb.get_item(
                TableName=role_table,
                Key={"RoleName": {"S": user_role}}
            )
        except botocore.exceptions.ClientError as e:
            action = "Querying the role table for authorization"
            return {"error": e.response["Error"]["Code"],
                    "data": {"exception": str(e), "action": action}}
        return role_info
    
    @staticmethod
    def get_permissions_info():
        pass
