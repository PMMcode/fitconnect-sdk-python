from read_config import read_config_sender
from fitconnect import FITConnectClient, Environment
from jwcrypto import jwk, jwe, jws, jwt
import json
import logging
import requests

'''
This Script is intended to read a log for a specific submission
'''
# configure logging
logging.basicConfig()
#logging.getLogger('fitconnect').level = logging.INFO

# read config_file
config = read_config_sender('conf/sender.yaml')

# initialize SDK
fitc = FITConnectClient(Environment[config['sdk']['environment']], config['sdk']['client_id'], config['sdk']['client_secret'])

# submission identifier
# 01.02.2023
# 'destinationId': 'f6b22a15-0338-4d65-b3a4-e464776a711c', 'submissionId': '1880de16-716d-4f0f-9341-170a07b32ea1', 'caseId': '2dea015b-ea74-450a-a0c0-ec0505a994c8'
# 'destinationId': 'f6b22a15-0338-4d65-b3a4-e464776a711c', 'submissionId': '88c6d8a7-d5d3-4f5a-ba2c-6c27b707dcee', 'caseId': '60edf914-ce25-4e80-bd57-aed4332e2102'

submissionId = 'dd78ca05-f361-4082-8349-965be827682e'
caseId = '874751cc-ffec-441b-b880-55ad87d0e8d9'
destinationId = 'a2de8f0e-27a1-44fa-81af-b3f330b4ca6b'

# get list of events for a case_id
status = fitc.readEventLog(caseId)

events = json.loads(status.text)['eventLog']
# Walk all events
i=0
while i < len(events):
# for event in events:
    event = fitc.verifyEventSignature(events[i])

    if event.is_valid:
        kidSET = event.jose_header['kid']
        issSET = json.loads(event.payload.decode('utf-8'))['iss']
        eventSET = list(json.loads(event.payload.decode('utf-8'))['events'])[0]
        print (f"Event {i}: kid: {kidSET}\n\t issuer: {issSET}\n\t events: {eventSET}")
        print("\t Signatur ist gültig.")
    else:
        print("\t Signatur ist ungültig.")
    
    i += 1
    

    # pubSigKey = requests.get(issuerURL)
    # print (f"Event {i}: {event}\n{setHeader}\n{setPayload}\n{setSignature}")
    
    
