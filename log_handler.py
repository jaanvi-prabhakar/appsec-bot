import json
import os
from datetime import datetime, timezone

LOG_FILE = "logs/ticket_logs.json"

def ensure_log_file_exists():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

def log_event(ticket_id, comment_type, status_transition=None):
    ensure_log_file_exists()

    log_entry = {
        "ticket_id": ticket_id,
        "comment_type": comment_type,
        "status_transition": status_transition,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    with open(LOG_FILE, "r+") as f:
        data = json.load(f)
        data.append(log_entry)
        f.seek(0)
        json.dump(data, f, indent=2)

def get_logs():
    ensure_log_file_exists()
    with open(LOG_FILE, "r") as f:
        return json.load(f)