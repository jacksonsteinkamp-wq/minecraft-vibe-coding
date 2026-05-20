"""
    @author RazrCraft
    @create date 2025-06-25 15:36:23
    @modify date 2025-06-25 16:55:22
    @desc Discord Webhook Send Example
"""

import sys
import urllib.request
import json

print(sys.executable)

if len(sys.argv) < 2 or not sys.argv[1].strip():
    print("Error: Content argument is required and cannot be empty.", file=sys.stderr)
    print("Usage: discord_webhook <content>", file=sys.stderr)
    sys.exit(1)

content = " ".join(sys.argv[1:])

# Replace with your actual Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/1506790927040118927/MO_j7qDoG4sdjefWi6sYi7QXlcc7UngcMwLQ1LDz-hR3EvOCMOsqQIxPdCUO7exAJ0Di"

# Define the message data
data = {
    "content": content,
    "username": "Minecraft Bot",
    "avatar_url": "https://discord.com/channels/1506548208858431488/1506790908719398922/1506792757597831298"
}

# Convert data to JSON
json_data = json.dumps(data).encode("utf-8")

# Create request
req = urllib.request.Request(
    webhook_url,
    data=json_data,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
)

# Send request
try:
    with urllib.request.urlopen(req, timeout=10) as response:
        if response.status == 204:
            print("Message sent successfully!")
        else:
            print(f"Unexpected response: {response.status}")

except urllib.error.HTTPError as e:
    if e.code == 429:
        print("Rate limited by Discord. Please wait before sending again.")
    else:
        print(f"HTTP Error {e.code}: {e.read().decode()}")

except Exception as e:
    print(f"Failed to send message: {e}")