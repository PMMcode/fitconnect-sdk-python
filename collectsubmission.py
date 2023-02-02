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

# activate destination
#fitc.activate_destination(config['destination_id'])

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
print (f"Selected Submission is: {submission_id}")

# collecting submission 
try:
    print(f"\n== Retrieving submission {submission_id} ==")
    submission = fitc.retrieve_submission(submission_id, config['private_key_decryption'])

    if submission['metadata']:
        print("=== Metadaten ===")
        print(json.dumps(submission['metadata'], indent=2, ensure_ascii=False).encode('utf-8').decode())

    if submission['data_json']:
        print("\n=== Fachdaten ===")
        print(json.dumps(submission['data_json'], indent=2, ensure_ascii=False).encode('utf-8').decode())

    for attachment_id, attachment in submission['attachments'].items():
        print(f"\n=== Anhang ({attachment_id}) ===")
        if attachment.startswith(b'%PDF'):
            with open(f'./subscriber-data/{submission_id}--{attachment_id}-data.pdf', 'wb') as f:
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
