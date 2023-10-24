from read_config import read_config_subscriber
from fitconnect import FITConnectClient, Environment
from jwcrypto.jwe import InvalidJWEData
import argparse
import json
import jsonschema
import logging
import os

# parse command line arguments
parser = argparse.ArgumentParser(
                    prog = 'subscriber_read_submission',
                    description = 'This script uses a subscriber client to retrieve a specific submission.')

parser.add_argument('-c', '--config', help='Path to config file', default='conf/subscriber.yaml')
parser.add_argument('-d', '--data_dir', help='Path to config file', default='./subscriber-data')
parser.add_argument('-v', '--verbose', help='Print decrypted metadata and data on console', action=argparse.BooleanOptionalAction)
parser.add_argument('submission_id', help='The submission that is being read')

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

# check for submission
submissions = fitc.available_submissions()
print (f"Looking for Submission {args.submission_id} in {config['destination_id']}")
for submission in submissions:
    submission_id = submission['submissionId']
    if submission_id == args.submission_id:
        print ("Sumission available")
        break
else:
    print ("Submission not found")
    quit()

# Verify folder exist, else create
try:
    if not os.path.exists(f'{args.data_dir}/{submission_id}'):
        os.makedirs(f'{args.data_dir}/{submission_id}')
except Exception as e:
    print("File odr Path Error", e)

# try reading submission and save files
try:
    print(f"\n== Retrieving submission {submission_id} ==")
    submission = fitc.retrieve_submission(submission_id, config['private_key_decryption'])

    if submission['metadata']:
        if args.verbose:
            print("=== Metadaten ===")
            print(json.dumps(submission['metadata'], indent=2, ensure_ascii=False).encode('utf-8').decode())
        with open (f'{args.data_dir}/{submission_id}/metadata-decrypted.json',mode='wt', encoding='utf-8') as f:
            json.dump(submission['metadata'], f)
        with open (f'{args.data_dir}/{submission_id}/metadata-encrypted.jwt',mode='wt', encoding='utf-8') as f:
            f.write(submission['encryptedMetadata'])
        print(f"Metadata verified: {submission['metadata_verified']}")

    if submission['data_json']:
        if args.verbose:
            print("\n=== Fachdaten ===")
            print(json.dumps(submission['data_json'], indent=2, ensure_ascii=False).encode('utf-8').decode())
        with open (f'{args.data_dir}/{submission_id}/data-decrypted.json',mode='wt',encoding='utf-8') as f:
            json.dump(submission['data_json'], f)
        with open (f'{args.data_dir}/{submission_id}/data-encrypted.jwt',mode='wt',encoding='utf-8') as f:
            f.write(submission['encryptedMetadata'])
        print(f"Data verified: {submission['data_json_verified']}")


    for attachment_id, attachment in submission['attachments'].items():
        if args.verbose:
            print(f"\n=== Anhang ({attachment_id}) ===")
        with open (f'{args.data_dir}/{submission_id}/{attachment_id}-encrypted.jwt',mode='wt', encoding='utf-8') as f:
            f.write(submission['encryptedAttachments'][attachment_id])       
        if attachment.startswith(b'%PDF'):
            with open(f'{args.data_dir}/{submission_id}/{attachment_id}-data.pdf', 'wb') as f:
                f.write(attachment)
                print("File written (Type: pdf)")
except InvalidJWEData as e:
    print(f"Could not decrypt submission {submission_id}")
except jsonschema.exceptions.ValidationError as e:
    print(f"Invalid schema in submission {submission_id}:", e)
except json.decoder.JSONDecodeError as e:
    print(f"Unparsable json in submission {submission_id}")
except ValueError as e:
    print("ValueError", e)

print(f"Submission {submission_id} erfolgreich gelesen.")

# fitc.writeEvent(submission, 'accept')