import time
import os
import json
from dotenv import load_dotenv

# Ensure configuration environment elements are loaded
load_dotenv(override=True)

def tail_live_alerts(file_path: str):
    """
    Continuously monitors a log file for new lines, acting as a real-time
    ingestion pipeline listener.
    """
    print(f"👀 Watching {file_path} for real-time security events...")
    
    # Check if file exists, if not, create it blank
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass

    # Open the file and move the cursor to the very end so it only reads NEW events
    with open(file_path, "r") as f:
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            
            # If no new line was written, sleep briefly to prevent CPU spinning
            if not line:
                time.sleep(1)
                continue
                
            # Clean up whitespace and process the line
            line = line.strip()
            if not line:
                continue
                
            print("\n📥 New raw log event intercepted!")
            yield line