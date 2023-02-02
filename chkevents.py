from read_config import read_config_sender
from fitconnect import FITConnectClient, Environment
#from jwcrypto.jwe import InvalidJWEData
from jwcrypto import jwk, jwe, jws, jwt
import json
#import base64
#import jsonschema
import logging
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

submissionId = '1880de16-716d-4f0f-9341-170a07b32ea1'
caseId = '2dea015b-ea74-450a-a0c0-ec0505a994c8'
destinationId = 'f6b22a15-0338-4d65-b3a4-e464776a711c'

# activate destination
# fitc.activate_destination(config['destination_id'])
fitc.activate_destination(destinationId)

# get a list of available submissions
status = fitc.readEventLog(caseId)

events = json.loads(status.content.decode())['eventLog']
i=0
for event in events:
    i += 1
    (setHeader,setPayload,setSignature) = event.split(".")
    
    #setHeader = setHeader + "="*divmod(len(setHeader),4)[1]
    #setHeader = base64.urlsafe_b64decode(setHeader)

    #setPayload = setPayload + "="*divmod(len(setPayload),4)[1]
    #setPayload = base64.urlsafe_b64decode(setPayload)

    jwsToken = jws.JWS()
    jwsToken.deserialize(event)

    # print (f"Event {i}: {event}\n{setHeader}\n{setPayload}\n{setSignature}")
    print (f"Event {i}: {jwsToken.objects['protected']}\n\t {jwsToken.objects['payload'].decode('utf-8')}")
