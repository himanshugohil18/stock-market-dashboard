import os
import json
import time
import boto3
import pyotp

from dotenv import load_dotenv
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

AWS_REGION = "ap-south-1"
KINESIS_STREAM_NAME = "stock-market-stream"


# ============================================================
# VALIDATE CONFIGURATION
# ============================================================

required_values = {
    "ANGEL_API_KEY": API_KEY,
    "ANGEL_CLIENT_CODE": CLIENT_CODE,
    "ANGEL_PASSWORD": PASSWORD,
    "ANGEL_TOTP_SECRET": TOTP_SECRET,
}

missing = [
    name for name, value in required_values.items()
    if not value
]

if missing:
    print("❌ Missing environment variables:")
    for name in missing:
        print(f"   - {name}")
    raise SystemExit(1)

print("✅ Environment configuration loaded")


# ============================================================
# STOCK TOKEN → SYMBOL MAPPING
# ============================================================

TOKEN_TO_SYMBOL = {
    "2885": "RELIANCE",
    "11536": "TCS",
    "1594": "INFY",
    "1333": "HDFCBANK",
    "4963": "ICICIBANK",
    "3045": "SBIN",
    "1660": "ITC",
    "11483": "LT",
    "1394": "HINDUNILVR",
    "5900": "AXISBANK",
}


# ============================================================
# KINESIS CLIENT
# ============================================================

kinesis = boto3.client(
    "kinesis",
    region_name=AWS_REGION
)

print("✅ Kinesis client ready")


# ============================================================
# ANGEL ONE LOGIN
# ============================================================

try:

    # Generate current TOTP automatically
    totp = pyotp.TOTP(TOTP_SECRET).now()

    smart_api = SmartConnect(
        api_key=API_KEY
    )

    session = smart_api.generateSession(
        CLIENT_CODE,
        PASSWORD,
        totp
    )

    if not session or not session.get("status"):

        print("❌ Angel One login failed")

        if session:
            print(
                "Message:",
                session.get("message")
            )

        raise SystemExit(1)

    auth_token = session["data"]["jwtToken"]

    feed_token = smart_api.getfeedToken()

    print("✅ Angel One login successful")


except Exception as e:

    print(
        "❌ Angel One authentication error:",
        e
    )

    raise SystemExit(1)


# ============================================================
# WEBSOCKET
# ============================================================

correlation_id = "stock-market-10"

sws = SmartWebSocketV2(
    auth_token,
    API_KEY,
    CLIENT_CODE,
    feed_token
)


# ============================================================
# WEBSOCKET CONNECTED
# ============================================================

def on_open(wsapp):

    print("🚀 WebSocket connected")

    # NSE exchange type = 1
    token_list = [
        {
            "exchangeType": 1,
            "tokens": [
                "2885",     # RELIANCE
                "11536",    # TCS
                "1594",     # INFY
                "1333",     # HDFCBANK
                "4963",     # ICICIBANK
                "3045",     # SBIN
                "1660",     # ITC
                "11483",    # LT
                "1394",     # HINDUNILVR
                "5900",     # AXISBANK
            ]
        }
    ]

    print("📡 Subscribing to 10 NSE stocks...")

    try:

        sws.subscribe(
            correlation_id,
            1,
            token_list
        )

        print("✅ Subscription successful")
        print()
        print("📊 Subscribed stocks:")

        for token in token_list[0]["tokens"]:

            symbol = TOKEN_TO_SYMBOL.get(
                token,
                "UNKNOWN"
            )

            print(
                f"   {symbol:<12} Token: {token}"
            )

        print()

    except Exception as e:

        print(
            "❌ Subscription failed:",
            e
        )


# ============================================================
# MARKET DATA RECEIVED
# ============================================================

def on_data(wsapp, message):

    try:

        # ----------------------------------------------------
        # Convert message
        # ----------------------------------------------------

        if isinstance(message, str):

            data = json.loads(message)

        else:

            data = message


        # ----------------------------------------------------
        # Token
        # ----------------------------------------------------

        token = str(
            data.get("token", "")
        )

        if not token:

            return


        # ----------------------------------------------------
        # Symbol
        # ----------------------------------------------------

        symbol = TOKEN_TO_SYMBOL.get(
            token,
            f"TOKEN_{token}"
        )


        # ----------------------------------------------------
        # Last traded price
        # Angel One sends price in paise
        # ----------------------------------------------------

        raw_price = data.get(
            "last_traded_price"
        )

        if raw_price is None:

            return


        price = float(raw_price) / 100


        # ----------------------------------------------------
        # Create clean stock record
        # ----------------------------------------------------

        stock_data = {

            "symbol": symbol,

            "exchange": "NSE",

            "token": token,

            "price": price,

            "sequence_number": data.get(
                "sequence_number"
            ),

            "exchange_timestamp": data.get(
                "exchange_timestamp"
            ),

            "received_at": int(
                time.time() * 1000
            )
        }


        # ----------------------------------------------------
        # Send record to Kinesis
        # ----------------------------------------------------

        response = kinesis.put_record(

            StreamName=KINESIS_STREAM_NAME,

            Data=json.dumps(
                stock_data
            ).encode("utf-8"),

            PartitionKey=symbol
        )


        # ----------------------------------------------------
        # Display result
        # ----------------------------------------------------

        shard_id = response.get(
            "ShardId",
            "unknown"
        )

        print(
            f"📈 {symbol:<12} "
            f"₹{price:,.2f}  →  "
            f"Kinesis {shard_id}"
        )


    except Exception as e:

        print(
            "❌ Error processing tick:",
            e
        )


# ============================================================
# WEBSOCKET ERROR
# ============================================================

def on_error(wsapp, error):

    print(
        "❌ WebSocket error:",
        error
    )


# ============================================================
# WEBSOCKET CLOSED
# ============================================================

def on_close(wsapp):

    print(
        "🔌 WebSocket connection closed"
    )


# ============================================================
# CALLBACKS
# ============================================================

sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close


# ============================================================
# START PRODUCER
# ============================================================

print()
print("==============================================")
print("🚀 STOCK MARKET PRODUCER")
print("==============================================")
print("📊 Stocks: 10")
print("📡 Exchange: NSE")
print("☁️  Kinesis:", KINESIS_STREAM_NAME)
print("🌍 Region:", AWS_REGION)
print("==============================================")
print()

try:

    sws.connect()

except KeyboardInterrupt:

    print()
    print("🛑 Producer stopped by user")

except Exception as e:

    print()
    print(
        "❌ Producer stopped:",
        e
    )
