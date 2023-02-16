from read_config import read_config_subscriber
from fitconnect import FITConnectClient, Environment
from jwcrypto.jwe import InvalidJWEData
import json
import jsonschema
import logging
'''
This Script is intended to collect a specific submission and its attachments
'''
# configure logging
logging.basicConfig()
#logging.getLogger('fitconnect').level = logging.INFO

# read config_file
config = read_config_subscriber('conf/subscriber.yaml')

# initialize SDK
fitc = FITConnectClient(Environment[config['sdk']['environment']], config['sdk']['client_id'], config['sdk']['client_secret'])

# get a list of available submissions
submissions = fitc.available_submissions()

# list all available submissions and select one
print("Select one of the following submissions for retrival:")
index=0
for submission in submissions:
    print(f"{index}: {submission['submissionId']}")
    index=index + 1

maxSelect = len(submissions)-1
while True:
    number = input(f"Select [0 ... {maxSelect}]: ")
    try:
        number = int(number)
        if number >= 0 and number <= maxSelect:
            break
        else:
            print("Ungültige Eingabe")
    
    except ValueError:
        print("Ungültige Eingabe")
submission_id = submissions[number]['submissionId']
case_id = submissions[number]['caseId']
print (f"Selected Submission is: {submission_id} with Case {case_id}")

status = fitc.readEventLog(case_id)
