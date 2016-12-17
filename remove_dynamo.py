#!/usr/bin/python2.7

"""
# remove.py
# Author: Miguel Saavedra
# Date: N/D
"""

import json
import os
import sys
import time

import boto3
import botocore

def print_help():
    print """
Run the following command to remove one table by Name

    python remove_dynamo [system-name the name you used in setup] [type of table e.g. USER_TABLE] 
    
Note :  new tables will have to be added to prostfixes.json for this script to work"""
    sys.exit()

# AWS clients used by the AWSCMS
dynamodb = boto3.client('dynamodb')
with open ("postfixes.json", "r") as postfixes_file:
    postfixes = json.loads(postfixes_file.read())

if str(sys.argv[1]) == "--help":
    print_help()
else:
    # Remove all AWSCMS dynamodb tables
    table_name = str(sys.argv[1]) + postfixes[str(sys.argv[2])]
    print "Removing dynamodb table " + table_name
    try:
        dynamodb.delete_table(TableName=table_name)
        print  "Successfully removed " + table_name
    except botocore.exceptions.ClientError as e:
            print e.response["Error"]["Code"]
            print e.response["Error"]["Message"]
            sys.exit()