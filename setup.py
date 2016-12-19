#!/usr/bin/python2.7

"""
# setup.py
# Author: Christopher Treadgold
# Date: N/D
# Edited: 07/08/2016 | Christopher Treadgold
"""

import cms_functions
import sys
import os

if len(sys.argv) not in range(2, 4):
    command = ''
    for arg in sys.argv:
        command += arg + ' '
    print 'Invalid command: ' + command
    print 'Usage: %s <cms_prefix> <region (optional)>' % sys.argv[0]
    sys.exit()

# Instantiate an AwsFunc class
if len(sys.argv) == 3:
    cms = cms_functions.AwsFunc(sys.argv[1], region=sys.argv[2])
else:
    cms = cms_functions.AwsFunc(sys.argv[1])

# Create the rest api
cms.create_rest_api()

# Create the lambda function
cms.create_lambda_function()

# Setup the rest api
cms.api_add_post_method()
cms.api_add_options_method()
cms.deploy_api()

# Create the s3 bucket
# cms.create_bucket()
# Create the cloudfront distribution
# cms.create_cloudfront_distribution() TODO: Reactivate

# # Create the dynamodb token table
# cms.create_token_table()

# # Create the dunamodb role table
# cms.create_role_table()
# # Add an admin role to the role table
# # cms.create_admin_role_db_entry()

# # Create the dynamodb user table
# cms.create_user_table()
# cms.create_table("user_table","USER_TABLE")
# Add an admin to the user table
# cms.create_default_db_entry("user","USER_TABLE")

# Creates the NCR table
cms.create_table("ncr_table","NCR_TABLE")
# Add a default value to the ncr table
cms.create_default_db_entry("ncr_item","NCR_TABLE")
cms.create_default_db_entry("ncr_item_2","NCR_TABLE")

# # # Print the default login credentials and the login link
# # cms.print_login_link()

# # Saves the cms installation information
cms.save_constants()
