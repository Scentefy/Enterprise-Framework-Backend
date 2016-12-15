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
        "get_record" : DynamoController.get_record,
        "login" : DynamoController.get_record,
        "put_record" : DynamoController.put_record,
        "remove_record" : DynamoController.remove_record,
        "edit_record" : DynamoController.put_record,
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
    
    if "token" in event:
        user_token = remove_prefix(event["token"])
    else:
        user_token = None
    
    """ Authenticate the request unless it is login, as login requires no
        authentication
    """
    if request != "loginUser":
        # Check that a token is provided with the request
        if user_token == None:
            Error.send_error("noToken")
        
        # Check that the user has the necessary permissions to make the request
        user_info = Security.authenticate_and_authorize(
            user_token, request, resources["TOKEN_TABLE"],
            resources["USER_TABLE"], resources["ROLE_TABLE"]
        )
        
        # Strip dynamo type identifiers from user info
        user_info = strip_dynamo_types(user_info)
        
        # Check if authentication or authorization returned an error
        if "error" in user_info:
            Error.send_error(authorized["error"], data=authorized["data"])
    else:
        user_info = None
    
    # Process the request
    if not user_info == None:
        response = process_request(request_body, resources, request,
                                   user_info=user_info, token=user_token)
    else:
        response = process_request(request_body, resources, request)
    
    # Check if response returned an error
    if "error" in response:
        Error.send_error(response["error"], data=response["data"])
    
    return strip_dynamo_types(response)

def process_request(request_body, resources, request, user_info=None, token=None):
    if request == "getAllUsers":
        """ Request structure
            {
                request: getAllUsers
            }
        """
        return User.get_all_users(resources["USER_TABLE"])
    elif request == "getUser":
        """ Request structure
            {
                request: getUser,
                email: <str: email>
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        
        email = request_body["email"]
        return User.get_user(email, resources["USER_TABLE"])
    elif request == "getUserFromId":
        """ Request structure
            {
                request: getUserFromId,
                userId: <str: user id>
            }
        """
        if not "userId" in request_body:
            Error.send_error("noUserId", data={"request": request})
        
        user_id = request_body["userId"]
        return User.get_user_from_id(user_id, resources["USER_TABLE"])
    elif request == "loginUser":
        """ Request structure
            {
                request: loginUser,
                email: <str: email>,
                password: <str: password>
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        if not "password" in request_body:
            Error.send_error("noPassword", data={"request": request})
        
        email = request_body["email"]
        password = request_body["password"]
        return User.login(email, password, token, resources["USER_TABLE"],
                          resources["TOKEN_TABLE"])
    elif request == "logoutUser":
        """ Request structure
            {
                request: logoutUser
            }
        """
        return User.logout(token, resources["TOKEN_TABLE"])
    elif request == "getPermissions":
        """ Request structure
            {
                request: logoutUser
            }
        """
        return Security.get_permissions(token, request, resources["TOKEN_TABLE"],
            resources["USER_TABLE"], resources["ROLE_TABLE"])
    elif request == "putUser":
        """ Request structure
            {
                request: putUser,
                email: <str: email>,
                username: <str: username>,
                password: <str: password>,
                roleName: <str: role name>
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        if not "username" in request_body:
            Error.send_error("noUsername", data={"request": request})
        if not "password" in request_body:
            Error.send_error("noPassword", data={"request": request})
        if not "roleName" in request_body:
            Error.send_error("noRoleName", data={"request": request})
        
        email = request_body["email"]
        username = request_body["username"]
        password = request_body["password"]
        role_name = request_body["roleName"]
        return User.put_user(email, username, password, role_name,
                             resources["USER_TABLE"])
    elif request == "deleteUser":
        """ Request structure
            {
                request: deleteUser,
                email: <str: email>
            }
        """
        if not "email" in request_body:
            Error.send_error("noEmail", data={"request": request})
        
        email = request_body["email"]
        return User.delete_user(email, resources["USER_TABLE"])
    elif request == "getAllRoles":
        """ Request structure
            {
                request: getAllRoles
            }
        """
        return User.get_all_roles(resources["ROLE_TABLE"])
    elif request == "getRole":
        """ Request structure
            {
                request: getRole,
                roleName: <str: role name>
            }
        """
        if not "roleName" in request_body:
            Error.send_error("noRoleName", data={"request": request})
        
        role_name = request_body["roleName"]
        return User.get_role(role_name, resources["ROLE_TABLE"])
    elif request == "putRole":
        """ Request structure
            {
                request: putRole,
                roleName: <str: role name>,
                permissions: <list:
                    <str: permission1>,
                    <str: permission2>,
                    <str: etc...>
                >
            }
        """
        if not "roleName" in request_body:
            Error.send_error("noRoleName", data={"request": request})
        if not "permissions" in request_body:
            Error.send_error("noPermissions", data={"request": request})
        
        role_name = request_body["roleName"]
        permissions = request_body["permissions"]
        return User.put_role(role_name, permissions, resources["ROLE_TABLE"])
    elif request == "deleteRole":
        """ Request structure
            {
                request: deleteRole,
                roleName: <str: role name>
            }
        """
        if not "roleName" in request_body:
            Error.send_error("noRoleName", data={"request": request})
        
        role_name = request_body["roleName"]
        return User.delete_role(role_name, resources["ROLE_TABLE"])


def supported_request(request):
    """Function which Returns back a boolean indicating if the request type is valid or not
    New request types need to be added to the corresponding arrays """

    supported_gets = [
        "getUser", "getUserFromId", "getAllUsers", "getAllRoles", "getRole", "getBlog",
        "getAllBlogs", "getPage", "getAllPages", "getPresignedPostImage",
        "getSiteSettings", "getNavItems"
    ]
    supported_puts = [
        "putUser", "putRole", "putBlog", "editBlog", "putPage", "putNavItems",
        "putSiteSettings"
    ]
    supported_posts = [
        "loginUser", "logoutUser"
    ]
    supported_deletes = [
        "deleteUser", "deleteRole", "deleteBlog", "deletePage"
    ]
    supported_requests = (supported_gets + supported_puts + supported_posts
        + supported_deletes)
    if request in supported_requests:
        return True
    else:
        return False

def remove_prefix(cookie):
    equals_index = cookie.find("=") + 1
    return cookie[equals_index:]

def strip_dynamo_types(response):
    type_identifiers = [
        "S", "N", "B", "SS", "NS", "BS", "M", "L", "NULL", "BOOL"
    ]

    if type(response).__name__ == "dict":
        if len(response) == 1:
            for key in response:
                if key in type_identifiers:
                    response = strip_dynamo_types(response[key])
                else:
                    response[key] = strip_dynamo_types(response[key])
        else:
            for key in response:
                response[key] = strip_dynamo_types(response[key])
    elif type(response).__name__ == "list":
        for index in range(len(response)):
            response[index] = strip_dynamo_types(response[index])
        
    return response
