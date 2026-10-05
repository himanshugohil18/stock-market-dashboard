import os
import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect

load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

totp = pyotp.TOTP(TOTP_SECRET).now()

smart_api = SmartConnect(api_key=API_KEY)

session = smart_api.generateSession(
    CLIENT_CODE,
    PASSWORD,
    totp
)

print("Login response:")
print(session)

if session.get("status"):
    print("\n✅ Angel One login successful!")
    print("Auth token received.")
else:
    print("\n❌ Angel One login failed.")
