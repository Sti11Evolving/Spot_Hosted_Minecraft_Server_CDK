import subprocess
import os

from dotenv import load_dotenv
from mctools import RCONClient, QUERYClient, PINGClient
from typing import Literal
from dataclasses import dataclass, field

load_dotenv()
RCON_PASSWORD = os.getenv("RCON_PASSWORD")
MINECRAFT_PATH = os.getenv("MINECRAFT_PATH")
QUERY_PORT = 25585
shutting_down = False

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

def setup_minecraft_server():
    # Retrieve the rcon password and server path from the environment

    # Set up the minecraft servers properties
    # Reads the server.properties file
    server_properties = {}
    with open(f"{MINECRAFT_PATH}/server.properties", "r") as f:
        for line in f.readlines():
            if "=" in line:
                key, value = line.split("=", 1)
                server_properties[key] = value.strip()

    # Changes important server properties
    server_properties["rcon.password"] = RCON_PASSWORD
    server_properties["enable-rcon"] = "true"
    server_properties["rcon.port"] = "25575"
    server_properties["enable-query"] = "true"
    server_properties["query.port"] = QUERY_PORT
    server_properties["enable-status"] = "true"

    # Writes the updated server.properties file
    with open(f"{MINECRAFT_PATH}/server.properties", "w") as f:
        for key, value in server_properties.items():
            f.write(f"{key}={value}\n")

    # Confirms the eula
    with open(f"{MINECRAFT_PATH}/eula.txt", "w") as f:
        f.write("eula=true")

    # Start the minecraft server
    subprocess.Popen(["java", "-Xms1024M", "-jar", "server.jar", "nogui"],
        cwd=MINECRAFT_PATH
    )

    # Start the timeout helper
    subprocess.Popen(["sudo", "python3", "./timeout_helper.py"])
    #subprocess.Popen(["python", "./timeout_helper.py"])

def shutodown_minecraft_server():
    global shutting_down
    shutting_down = True
    with RCONClient("localhost", format_method=RCONClient.REMOVE) as rcon:
        if rcon.login(RCON_PASSWORD):
            rcon.command("save-all flush")
            rcon.command("stop")

def shutdown_helper() -> bool:
    global shutting_down
    if shutting_down:
        return False
    
    shutting_down = True

    subprocess.Popen(["sudo", "python3", "./shutdown.py"])
    #subprocess.Popen(["python", "./shutdown.py"])

    return True

def online_status() -> statusType:
    with PINGClient("localhost") as ping:
        try:
            ping.get_stats()
            return shutting_down and "shutting down" or "online"
        except KeyError:
            return shutting_down and "shutting down" or "starting up"
        except:
            return "offline"

def get_basic_stats():
    with QUERYClient("localhost", port=QUERY_PORT, format_method=QUERYClient.REMOVE) as query:
        return query.get_basic_stats()
    
def get_full_stats():
    with QUERYClient("localhost", port=QUERY_PORT, format_method=QUERYClient.REMOVE) as query:
        return query.get_full_stats()
    
def send_command(command: str) -> str:
    try:
        with RCONClient("localhost", format_method=RCONClient.REMOVE) as rcon:
            if rcon.login(RCON_PASSWORD):
                return rcon.command(command)
    except:
        return "Command failed"
    
def get_players():
    try:
        return get_full_stats()['players']
    except:
        return []

def get_num_players():
    try:
        return int(get_basic_stats()['numplayers'])
    except:
        return 0

def get_logs():
    with open(f"{MINECRAFT_PATH}/logs/latest.log", "r") as f:
        return f.read()

def get_server_info():
    server_status = online_status()
    logs = get_logs().split("\n")
    if server_status != "online":
        return ServerInfo(
            status=server_status,
            logs=logs[-200:]
        )

    
    stats = get_full_stats()

    return ServerInfo(
        status=server_status,
        numPlayers=int(stats['numplayers']),
        maxPlayers=int(stats['maxplayers']),
        motd=stats['motd'],
        version=stats['version'],
        players=stats['players'],
        port=stats['hostport'],
        logs=logs[-200:]
    )