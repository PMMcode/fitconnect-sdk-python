from read_config import read_config_subscriber
from fitconnect import FITConnectClient, Environment
from jwcrypto.jwe import InvalidJWEData
import argparse
import json
import jsonschema
import logging

# parse command line arguments
parser = argparse.ArgumentParser(
                    prog = 'subscriber_read_submission',
                    description = 'This script uses a subscriber client to retrieve all submissions the subscriber has access to')

parser.add_argument('-c', '--config', help='Path to config file', default='conf/subscriber.yaml')
parser.add_argument('-d', '--data_dir', help='Path to config file', default='./subscriber-data')

args = parser.parse_args()

# configure logging
logging.basicConfig()
#logging.getLogger('fitconnect').level = logging.INFO

# read config_file
config = read_config_subscriber(args.config)

# initialize SDK
fitc = FITConnectClient(Environment[config['sdk']['environment']], config['sdk']['client_id'], config['sdk']['client_secret'])

# activate destination
fitc.activate_destination(config['destination_id'])

# get a list of available submissions
submissions = fitc.available_submissions()

index = 1
print (f"Submissions available for {config['destination_id']}")
for submission in submissions:
    submission_id = submission['submissionId']
    case_id = submission['caseId']
    print (f"{index}: Submission: {submission_id}  Case: {case_id}")
    index=index+1
