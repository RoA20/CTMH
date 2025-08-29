import os
import subprocess
from pyngrok import ngrok
from app import app
import webbrowser

# ---------------------------
# Kill any existing Flask on 5050
# ---------------------------
try:
    result = subprocess.run(
        ["lsof", "-ti:5050"], capture_output=True, text=True
    )
    pids = result.stdout.strip().split("\n")
    for pid in pids:
        if pid:
            print(f"Killing old process on port 5050: {pid}")
            os.system(f"kill -9 {pid}")
except Exception as e:
    print("No existing processes to kill:", e)

# ---------------------------
# Start ngrok tunnel
# ---------------------------
tunnel = ngrok.connect(5050)
print(" * ngrok tunnel URL:", tunnel.public_url)

# Open in default browser
webbrowser.open(tunnel.public_url)

# ---------------------------
# Run Flask app
# ---------------------------
app.run(host="0.0.0.0", port=5050)
