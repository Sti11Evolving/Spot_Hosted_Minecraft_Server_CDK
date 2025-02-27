import time
from app_helper import get_num_players, shutdown_helper, online_status, send_command
from dotenv import load_dotenv
import os

load_dotenv()

TIMEOUT_MINUTES = int(os.getenv("TIMEOUT_MINUTES", "30"))

def timeout():
    num_checks_without_players = 0

    while True:
        time.sleep(60)
        # Check if there are any players online

        if online_status() == "online":
            if get_num_players() == 0:
                num_checks_without_players += 1

                send_command(f"say No players online for {num_checks_without_players} minutes...")

                if num_checks_without_players > TIMEOUT_MINUTES:
                    shutdown_helper()
                    return
                
            else:
                num_checks_without_players = 0

if __name__ == "__main__":
    timeout()