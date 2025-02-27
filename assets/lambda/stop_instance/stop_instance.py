import os
import boto3
import json
import urllib3

instanceID = os.getenv("INSTANCE_ID")


def lambda_handler(event, context):

    minecraft_instance = boto3.resource('ec2').Instance(instanceID)

    if minecraft_instance.public_ip_address != None:
        # Get information about the minecraft server instance
        http = urllib3.PoolManager()
        response = http.request('GET', f"http://{minecraft_instance.public_ip_address}/shutdown",
            timeout=urllib3.Timeout(total=5), 
            retries=False
        )

    return {
        'statusCode': 200,
        "headers": {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS"
        },
        'body': response.data
    }