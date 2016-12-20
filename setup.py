#!/usr/bin/python2.7

"""
# setup.py
# Author: Miguel Saavedra
# Date: N/D
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

# # Create the rest api
# cms.create_rest_api()

# # Create the lambda function
# cms.create_lambda_function()

# # Setup the rest api
# cms.api_add_post_method()
# cms.api_add_options_method()
# cms.deploy_api()

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
# cms.create_table("ncr_d_table","NCR_D_TABLE")
# cms.create_table("ncr_nr_table","NCR_NR_TABLE" )
# cms.create_table("ncr_n_table","NCR_N_TABLE")
cms.create_table("ncr_r_table","NCR_R_TABLE")
# DEBUG Add a default values to the ncr table TODO: Remove for release
# cms.create_default_db_entry("ncr_d_item","NCR_D_TABLE")
# cms.create_default_db_entry("ncr_nr_item","NCR_NR_TABLE")
# cms.create_default_db_entry("ncr_n_item","NCR_N_TABLE")
cms.create_default_db_entry("ncr_r_item","NCR_R_TABLE")

# # # Print the default login credentials and the login link
# # cms.print_login_link()

# # Saves the cms installation information
cms.save_constants()
