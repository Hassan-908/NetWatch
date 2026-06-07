from datetime import datetime

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs/incident.logs", "a") as file:
        file.write(f"[{timestamp}] {message}\n")