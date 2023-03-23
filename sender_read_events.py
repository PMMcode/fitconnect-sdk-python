from read_config import read_config_sender
from fitconnect import FITConnectClient, Environment
from datetime import datetime
import argparse
import json
import logging

'''
This Script is intended to read a log for a specific submission

It is representing the sender client view on events so we need the sender.yaml to be configured.
'''
# parse command line arguments
parser = argparse.ArgumentParser(
                    prog = 'sender_read_events',
                    description = 'This script uses sender clients to read events for a submission.')

parser.add_argument('-c', '--config', help='Path to config file', default='conf/sender.yaml')
parser.add_argument('-v', '--verbose', help='Show full server response for event details', action=argparse.BooleanOptionalAction)
parser.add_argument('case_id', help='The destination that is being searched for')

args = parser.parse_args()

# configure logging
logging.basicConfig()
logging.getLogger('fitconnect').level = logging.INFO

# read config_file
config = read_config_sender((args.config))

# initialize SDK
fitc = FITConnectClient(Environment[config['sdk']['environment']], config['sdk']['client_id'], config['sdk']['client_secret'], True)

# get list of events for case_id
status = fitc.readEventLog(args.case_id)
if status.ok:
    events = json.loads(status.text)['eventLog']

    # Walk all events
    i=0
    while i < len(events):
        # verify signature
        event = fitc.verifyEventSignature(events[i])

        if event.is_valid:
            kidSET = event.jose_header['kid']
            issSET = json.loads(event.payload.decode('utf-8'))['iss']
            eventSET = list(json.loads(event.payload.decode('utf-8'))['events'])[0]
            iatDateTime = json.loads(event.payload.decode('utf-8'))['iat']
            iatDateTime = datetime.utcfromtimestamp(iatDateTime).strftime('%Y-%m-%d %H:%M:%S')
            print (f"Event {i}: date: {iatDateTime} UTC\n\t kid: {kidSET}\n\t issuer: {issSET}\n\t events: {eventSET}")
            print("\t Signatur ist gültig.")
            if args.verbose:
                print(json.dumps(event.jose_header, indent="\t") + '\n')
                print(json.dumps(json.loads(event.payload.decode('utf-8')), indent="\t") + '\n')
        else:
            print("\t Signatur ist ungültig.")
        
        i += 1
else:
    print("CaseID", args.case_id, "not found in", config['sdk']['environment'],".")    
