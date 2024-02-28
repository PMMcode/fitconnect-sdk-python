from read_config import read_config_subscriber
from fitconnect import FITConnectClient, Environment
from jwcrypto.jwe import InvalidJWEData
import json
import jsonschema
import logging
import argparse

'''
This Script is intended to collect a specific submission and its attachments
'''

# parse command line arguments
parser = argparse.ArgumentParser(
                    prog = 'acceptsubmission',
                    description = 'This script uses a subscriber client to send accept_submission.')

parser.add_argument('-c', '--config', help='Path to config file', default='conf/subscriber.yaml')
# parser.add_argument('-d', '--data_dir', help='Path to config file', default='./subscriber-data')
parser.add_argument('-v', '--verbose', help='Print decrypted metadata and data on console', action=argparse.BooleanOptionalAction)
parser.add_argument('submission_id', help='The submission that is being accepted')

args = parser.parse_args()

# configure logging
logging.basicConfig()
#logging.getLogger('fitconnect').level = logging.INFO

# read config_file
config = read_config_subscriber(args.config)

# initialize SDK
fitc = FITConnectClient(Environment[config['sdk']['environment']], config['sdk']['client_id'], config['sdk']['client_secret'])

# check for submission
submissions = fitc.available_submissions()
print (f"Looking for Submission {args.submission_id} in {config['destination_id']}")
for submission in submissions:
    submission_id = submission['submissionId']
    if submission_id == args.submission_id:
        print (f"Sumission available")
        break
else:
    print (f"Submission not found")
    quit()

#submission_id = submissions[number]['submissionId']
case_id = submission['caseId']
print (f"Selected Submission is: {submission_id} with Case {case_id}")

status = fitc.readEventLog(case_id)

# try reading submission and show metadata, data if verbose
try:
    print(f"\n== Retrieving submission {submission_id} ==")
    submission = fitc.retrieve_submission(submission_id, config['private_key_decryption'])

    if submission['metadata']:
        if args.verbose:
            print("=== Metadaten ===")
            print(json.dumps(submission['metadata'], indent=2, ensure_ascii=False).encode('utf-8').decode())
        print("Metada read")

    if submission['data_json']:
        if args.verbose:
            print("\n=== Fachdaten ===")
            print(json.dumps(submission['data_json'], indent=2, ensure_ascii=False).encode('utf-8').decode())
        print("Submission data read")


    for attachment_id, attachment in submission['attachments'].items():
        if args.verbose:
            print(f"\n=== Anhang ({attachment_id}) ===")
        print(f"Attachment {attachment_id} read")

except InvalidJWEData as e:
    print(f"Could not decrypt submission {submission_id}")
except jsonschema.exceptions.ValidationError as e:
    print(f"Invalid schema in submission {submission_id}:", e)
except json.decoder.JSONDecodeError as e:
    print(f"Unparsable json in submission {submission_id}")
except ValueError as e:
    print("ValueError", e)

print(f"Submission {submission_id} erfolgreich gelesen.")

# writig accept_submission
fitc.writeEvent(submission, config['private_key_signing'] ,'accept-problem')

print (f"Sumbission {submission_id} accepted")