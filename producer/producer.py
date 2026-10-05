import os
import json
import time
import boto3
import pyotp

from dotenv import load_dotenv
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

load_dotenv()

# -----------------------------
# Configuration
# -----------------------------
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

STREAM_NAME = "stock-market-stream"
AWS_REGION = "ap-south-1"

# -----------------------------
# AWS Kinesis
# -----------------------------
kinesis = boto3.client(
    "kinesis",
    region_name=AWS_REGION
)

# -----------------------------
# Angel One Login
# -----------------------------
totp = pyotp.TOTP(TOTP_SECRET).now()

smart_api = SmartConnect(api_key=API_KEY)

session = smart_api.generateSession(
    CLIENT_CODE,
    PASSWORD,
    totp
)

if not session.get("status"):
    print("❌ Angel One login failed")
    print(session.get("message"))
    exit(1)

AUTH_TOKEN = session["data"]["jwtToken"]
FEED_TOKEN = smart_api.getfeedToken()

print("✅ Angel One login successful")
print("✅ Kinesis client ready")

# -----------------------------
# WebSocket
# -----------------------------
correlation_id = "stockmarket001"

sws = SmartWebSocketV2(
    AUTH_TOKEN,
    API_KEY,
    CLIENT_CODE,
    FEED_TOKEN
)


def on_open(wsapp):
    print("✅ WebSocket connected")
    print("📡 Subscribing to RELIANCE...")

    token_list = [
        {
            "exchangeType": 1,
            "tokens": ["2885"]
        }
    ]

    sws.subscribe(
        correlation_id,
        1,
        token_list
    )

    print("✅ Subscription successful")


def on_data(wsapp, message):

    print("📈 Received tick:", message)

    try:

        # Convert paise → rupees
        price = message.get("last_traded_price", 0) / 100

        record = {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "token": message.get("token"),
            "price": price,
            "sequence_number": message.get("sequence_number"),
            "exchange_timestamp": message.get("exchange_timestamp"),
            "received_at": int(time.time() * 1000)
        }

        response = kinesis.put_record(
            StreamName=STREAM_NAME,
            Data=json.dumps(record),
            PartitionKey="RELIANCE"
        )

        print(
            f"🚀 Sent to Kinesis | "
            f"RELIANCE ₹{price:.2f} | "
            f"Shard: {response['ShardId']}"
        )

    except Exception as e:
        print("❌ Kinesis error:", e)


def on_error(wsapp, error):
    print("❌ WebSocket error:", error)


def on_close(wsapp):
    print("🔴 WebSocket closed")


sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close


print("🚀 Starting Stock Market Producer...")

sws.connect()
