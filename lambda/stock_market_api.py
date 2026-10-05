import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("stock-market-data-v2")


def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):

    latest_stocks = {}

    # Read all records from DynamoDB
    response = table.scan(
        ProjectionExpression="#sym, #price, #exchange, #timestamp",
        ExpressionAttributeNames={
            "#sym": "symbol",
            "#price": "price",
            "#exchange": "exchange",
            "#timestamp": "exchange_timestamp"
        }
    )

    items = response.get("Items", [])

    # Handle pagination
    while "LastEvaluatedKey" in response:
        response = table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"],
            ProjectionExpression="#sym, #price, #exchange, #timestamp",
            ExpressionAttributeNames={
                "#sym": "symbol",
                "#price": "price",
                "#exchange": "exchange",
                "#timestamp": "exchange_timestamp"
            }
        )

        items.extend(response.get("Items", []))

    # Keep only latest record for each symbol
    for item in items:

        symbol = item.get("symbol")

        if not symbol:
            continue

        timestamp = item.get("exchange_timestamp", 0)

        if (
            symbol not in latest_stocks
            or timestamp > latest_stocks[symbol].get(
                "exchange_timestamp", 0
            )
        ):
            latest_stocks[symbol] = item

    # Convert dictionary to list
    stocks = list(latest_stocks.values())

    # Sort alphabetically
    stocks.sort(key=lambda x: x.get("symbol", ""))

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(
            {
                "count": len(stocks),
                "stocks": stocks
            },
            default=decimal_to_float
        )
    }
