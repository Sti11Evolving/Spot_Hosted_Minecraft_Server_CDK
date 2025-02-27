from app_helper import shutodown_minecraft_server, online_status, send_command
from time import sleep
import subprocess

def shutdown_with_notice():
    for i in range(2, 1, -1):
        send_command(f"say Shutting down in {i} minutes...")
        sleep(60)

    for i in range(60, 0, -5):
        send_command(f"say Shutting down in {i} seconds...")
        sleep(5)

    shutodown_minecraft_server()
    while online_status() != "offline":
        sleep(1)

    sleep(10)
    subprocess.run(["sudo", "shutdown", "now"])

if __name__ == "__main__":
    shutdown_with_notice()