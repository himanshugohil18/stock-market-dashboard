import json
import base64
import boto3
from decimal import Decimal
from datetime import datetime, timezone

# DynamoDB
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("stock-market-data-v2")

# S3
s3 = boto3.client("s3")
BUCKET_NAME = "stock-market-pipeline-himanshu-2026"


def lambda_handler(event, context):

    print("===== STOCK MARKET EVENT RECEIVED =====")

    for record in event.get("Records", []):

        try:
            # Kinesis data is Base64 encoded
            encoded_data = record["kinesis"]["data"]

            decoded_data = base64.b64decode(
                encoded_data
            ).decode("utf-8")

            # Convert JSON string to Python dictionary
            stock_data = json.loads(decoded_data)

            print("Stock data:", stock_data)

            # -----------------------------
            # Basic fields
            # -----------------------------

            symbol = stock_data.get("symbol", "UNKNOWN")
            exchange = stock_data.get("exchange", "NSE")
            token = stock_data.get("token", "")

            price = Decimal(
                str(stock_data.get("price", 0))
            )

            sequence_number = stock_data.get(
                "sequence_number", 0
            )

            exchange_timestamp = stock_data.get(
                "exchange_timestamp", 0
            )

            received_at = stock_data.get(
                "received_at", 0
            )

            print("Partition key:", symbol)

            # -----------------------------
            # DynamoDB
            # -----------------------------

            item = {
                "symbol": symbol,
                "exchange_timestamp": exchange_timestamp,
                "exchange": exchange,
                "token": token,
                "price": price,
                "sequence_number": sequence_number,
                "received_at": received_at
            }

            table.put_item(Item=item)

            print("Saved to DynamoDB:", item)

            # -----------------------------
            # S3
            # -----------------------------

            now = datetime.now(timezone.utc)

            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")

            s3_key = (
                f"stock-data/"
                f"{year}/{month}/{day}/"
                f"{symbol}/"
                f"{exchange_timestamp}.json"
            )

            s3_body = json.dumps(
                {
                    "symbol": symbol,
                    "exchange": exchange,
                    "token": token,
                    "price": float(price),
                    "sequence_number": sequence_number,
                    "exchange_timestamp": exchange_timestamp,
                    "received_at": received_at
                }
            )

            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_key,
                Body=s3_body,
                ContentType="application/json"
            )

            print(
                f"Saved to S3: s3://{BUCKET_NAME}/{s3_key}"
            )

        except Exception as e:

            print(
                f"ERROR PROCESSING RECORD: {str(e)}"
            )

    print("===== PROCESSING COMPLETE =====")

    return {
        "statusCode": 200,
        "body": json.dumps(
            "Stock data processed successfully"
        )
    }
