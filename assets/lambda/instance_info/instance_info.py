import os
import boto3
import json
from dataclasses import dataclass, asdict, field
from typing import Literal, Optional
import urllib3

instanceID = os.getenv("INSTANCE_ID")

statusType = Literal["online", "starting up", "shutting down", "offline"]
@dataclass
class ServerInfo:
    status: statusType
    numPlayers: int = 0
    maxPlayers: int = 0
    motd: str = ""
    version: str = ""
    players: list[str] = field(default_factory=list)
    port: int = 0
    logs: list[str] = field(default_factory=list)

@dataclass
class InstanceInfo:
    instanceStatus: Literal['pending','running','shutting-down','terminated','stopping','stopped']
    instanceIP: Optional[str] = None
    serverInfo: Optional[ServerInfo] = None

def lambda_handler(event, context):

    # Get a resource handle to the minecraft instance
    minecraft_instance = boto3.resource('ec2').Instance(instanceID)

    server_info = None
    try:
        if minecraft_instance.public_ip_address != None:
            # Get information about the minecraft server instance
            http = urllib3.PoolManager()
            response = http.request('GET', f"http://{minecraft_instance.public_ip_address}/server_info", 
                timeout=urllib3.Timeout(total=5), 
                retries=False
            )

            if response.status == 200:
                server_info = json.loads(response.data)
                server_info = ServerInfo(
                    status=server_info['status'],
                    numPlayers=server_info['numPlayers'],
                    maxPlayers=server_info['maxPlayers'],
                    motd=server_info['motd'],
                    version=server_info['version'],
                    players=server_info['players'],
                    port=server_info['port'],
                    logs=server_info['logs'],
                )
    except:
        pass


    return {
        'statusCode': 200,
        "headers": {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS"
        },
        'body': json.dumps(
            asdict(
                InstanceInfo(
                    instanceStatus=minecraft_instance.state['Name'],
                    instanceIP=minecraft_instance.public_ip_address,
                    serverInfo=server_info,
                )
            )
        )
    }