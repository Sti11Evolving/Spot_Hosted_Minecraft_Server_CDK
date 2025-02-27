import os
import boto3
import json
from typing import Literal, Optional

instanceID = os.getenv("INSTANCE_ID")


def lambda_handler(event, context):

    # Get a resource handle to the minecraft instance
    minecraft_instance = boto3.resource('ec2').Instance(instanceID)

    response = minecraft_instance.start()
    current_state = response['StartingInstances'][0]['CurrentState']['Name']
    previous_state = response['StartingInstances'][0]['PreviousState']['Name']

    return {
        'statusCode': 200,
        "headers": {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS"
        },
        'body': json.dumps({"currentState": current_state, "previousState": previous_state})
    }