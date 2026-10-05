import os
import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

# Login
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
    exit()

AUTH_TOKEN = session["data"]["jwtToken"]
FEED_TOKEN = smart_api.getfeedToken()

print("✅ Angel One login successful")
print("✅ Connecting to live market feed...")

# WebSocket
correlation_id = "stockmarket001"

sws = SmartWebSocketV2(
    AUTH_TOKEN,
    API_KEY,
    CLIENT_CODE,
    FEED_TOKEN
)

def on_data(wsapp, message):
    print("\n📈 LIVE MARKET DATA:")
    print(message)

def on_open(wsapp):
    print("✅ WebSocket connected")

    # RELIANCE - NSE
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

def on_error(wsapp, error):
    print("❌ WebSocket error:")
    print(error)

def on_close(wsapp):
    print("🔴 WebSocket connection closed")

sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

sws.connect()
