from __future__ import print_function

import boto3
from decimal import Decimal
import json
from urllib.parse import unquote_plus

rekognition = boto3.client('rekognition')
sns = boto3.client('sns')

# --------------- Main handler ------------------

def lambda_handler(event, context):
    # Get the object from the event
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'], encoding = 'utf8')
    try:
        # Calls rekognition DetectLabels API to detect labels in S3 object
        response = detect_labels(bucket, key)
        
        if response == True:
            sendPushNotification()
        
        # Print response to console.
        print(response)

        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e

# --------------- Functions ------------------

def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    labels = [{'Name': label_prediction['Name']} for label_prediction in response['Labels']]
    for item in labels: 
        if item['Name'] == 'Weapon':
            # print(item['Width'])
            return True
    
    return False
    
def sendPushNotification():
    apns_dict = {
                  "typeOfGun": "pistol",
                  "aps": {
                    "alert": {
                      "title": "Weapon Alert",
                      "body": "Someone has a weapon!"
                    }
                  }
                }
    apns_string = json.dumps(apns_dict,ensure_ascii=False)
    message = {'default':'default message','APNS_SANDBOX':apns_string}
    messageJSON = json.dumps(message,ensure_ascii=False)
    sns.publish(Message=messageJSON,TargetArn='arn:aws:sns:us-east-1:756906170378:endpoint/APNS_SANDBOX/iOS_AWS_APNs_Receiver/b71f3c43-dcbd-34c9-9d0f-abe6f450a94d',MessageStructure='json')
