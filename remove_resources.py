#!/usr/bin/python2.7

"""
# remove.py
# Author: Christopher Treadgold
# Date: N/D
# Edited: 07/08/2016 | Christopher Treadgold
"""

import json
import os
import sys
import time

import boto3

# AWS clients used by the AWSCMS
apigateway = boto3.client('apigateway')
lmda = boto3.client('lambda')
iam = boto3.client('iam')
dynamodb = boto3.client('dynamodb')

rest_api_names = []
lmda_function_names = [
]
role_names = [
]
dynamodb_table_names = [
]

# Remove all AWSCMS api gateways
print "Querying all rest api end point in your AWS account...."

rest_apis = apigateway.get_rest_apis()["items"]
print rest_apis

rest_apis_deleted = 0

print "Removing rest api"
for rest_api in rest_apis:
    if rest_api != rest_apis[-1]:
        time.sleep(30.5)
    apigateway.delete_rest_api(restApiId=rest_api["id"])
    rest_apis_deleted += 1
    print "sucessfully deleted " + rest_api["id"] + " api enpoint"

if rest_apis_deleted > 0:
    print rest_apis_deleted, 'Rest api(s) removed'
else:
    print 'No apis to remove'
