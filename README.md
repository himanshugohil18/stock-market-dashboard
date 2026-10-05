# Real-Time Stock Market Streaming Platform

A real-time stock market data project built on AWS. The system receives live market data from Angel One, sends the data from a Python producer running on EC2 into Amazon Kinesis, processes each event with AWS Lambda, stores the data in DynamoDB and Amazon S3, and exposes the latest stock prices through API Gateway to a React dashboard.

This project was built as a hands-on AWS/DevOps project to understand how a real streaming workload can be designed, deployed, monitored, and consumed by an application.

---

## What the project does

The complete flow is:

```text
Angel One SmartAPI
        |
        v
Python Producer on EC2
        |
        v
Amazon Kinesis Data Stream
        |
        v
StockMarketProcessor Lambda
        |
        +--------------------+
        |                    |
        v                    v
   DynamoDB                 S3
 historical data         raw market data
        |
        v
stock-market-api Lambda
        |
        v
Amazon API Gateway
        |
        v
React + Vite Dashboard
```

CloudWatch and IAM support the pipeline across the AWS environment.

---

## Why I built it

The initial idea was simple: receive live stock prices and display them.

Instead of connecting the frontend directly to a market API, I built the complete backend pipeline so the project could demonstrate real AWS concepts:

- live event ingestion
- streaming with Kinesis
- event-driven Lambda processing
- historical NoSQL storage
- raw data storage in S3
- API-based access to DynamoDB
- frontend/backend separation
- IAM roles
- CloudWatch monitoring
- environment-based secret management

The result is a small but realistic cloud data platform rather than only a stock-price UI.

---

# Architecture

```text
                           ANGEL ONE
                       SmartAPI WebSocket
                              |
                              v
                   +----------------------+
                   |   EC2 Python         |
                   |   Market Producer    |
                   +----------+-----------+
                              |
                              | Put records
                              v
                   +----------------------+
                   | Amazon Kinesis       |
                   | Data Stream          |
                   +----------+-----------+
                              |
                              | Event source
                              v
                   +----------------------+
                   | StockMarketProcessor |
                   | AWS Lambda            |
                   +----------+-----------+
                              |
                    +---------+---------+
                    |                   |
                    v                   v
             +-------------+     +-------------+
             |  DynamoDB   |     |     S3      |
             | Historical  |     | Raw Market  |
             | Stock Data  |     |    Data     |
             +------+------+     +-------------+
                    |
                    v
             +-------------+
             | stock-market|
             | api Lambda  |
             +------+------+
                    |
                    v
             +-------------+
             | API Gateway |
             |   /stocks   |
             +------+------+
                    |
                    v
             +-------------+
             | React/Vite  |
             |  Dashboard  |
             +-------------+

       CloudWatch + IAM + SNS
              support layer
```

---

# AWS services used

| Service | Purpose |
|---|---|
| Amazon EC2 | Runs the Python market-data producer |
| Amazon Kinesis Data Streams | Real-time event ingestion |
| AWS Lambda | Processes Kinesis events and serves API requests |
| Amazon DynamoDB | Stores historical stock records |
| Amazon S3 | Stores raw market-data objects |
| Amazon API Gateway | Exposes stock data to the frontend |
| Amazon CloudWatch | Logs, metrics and monitoring |
| AWS IAM | Roles and permissions |
| Amazon SNS | Notification layer for alarms |
| AWS Glue / Athena | Planned analytics layer |

---

# 1. Angel One market feed

The source of the market data is Angel One SmartAPI.

The producer authenticates with Angel One and establishes a WebSocket connection for live market updates.

The producer uses environment variables instead of putting credentials directly into Python code.

Example:

```env
ANGEL_API_KEY=your_angel_api_key
ANGEL_CLIENT_ID=your_angel_client_id
ANGEL_PASSWORD=your_angel_password
ANGEL_TOTP_SECRET=your_angel_totp_secret
```

The real `.env` file is never committed to GitHub.

Only `.env.example` is included in the repository.

---

# 2. EC2 Python producer

The market producer runs on an EC2 instance.

The producer handles:

1. Angel One authentication
2. TOTP generation
3. WebSocket connection
4. Stock subscription
5. Receiving live ticks
6. Converting the feed into JSON
7. Sending events to Kinesis

The producer code is kept under:

```text
producer/
```

Files:

```text
producer/
├── producer.py
├── stock_market_producer.py
├── test_angel.py
├── test_feed.py
├── .env.example
└── .gitignore
```

The main implementation is:

```text
stock_market_producer.py
```

The smaller scripts were used while testing authentication and the live feed.

---

# 3. Kinesis streaming layer

The producer sends market events to Amazon Kinesis.

Conceptually:

```text
EC2 Producer
     |
     | market event
     v
Kinesis Data Stream
```

A typical event contains information such as:

```json
{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "token": "2885",
  "price": 1189.40,
  "sequence_number": 12345,
  "exchange_timestamp": 1760000001,
  "received_at": 1760000002
}
```

Kinesis separates the producer from the processing layer. The producer does not need to know how DynamoDB or S3 works.

---

# 4. StockMarketProcessor Lambda

The first Lambda is the main stream processor:

```text
StockMarketProcessor
```

Its trigger is the Kinesis stream.

The processing flow is:

```text
Kinesis record
      |
      v
Base64 decode
      |
      v
JSON parsing
      |
      v
Extract stock fields
      |
      +------------+
      |            |
      v            v
  DynamoDB        S3
```

The Lambda reads:

- symbol
- exchange
- token
- price
- sequence number
- exchange timestamp
- received timestamp

The price is converted to `Decimal` before writing to DynamoDB.

---

# 5. DynamoDB historical storage

The DynamoDB table used by the processor is:

```text
stock-market-data-v2
```

The important design change in the project was moving away from storing only the latest value for a symbol.

The table uses:

```text
Partition Key:
symbol

Sort Key:
exchange_timestamp
```

That allows multiple price events for the same stock.

Example:

```text
RELIANCE | 10:00:01 | 1189.40
RELIANCE | 10:00:02 | 1189.45
RELIANCE | 10:00:03 | 1189.50
RELIANCE | 10:00:04 | 1189.42
```

Instead of:

```text
RELIANCE -> one value
```

the system can retain a sequence of historical observations.

Stored attributes include:

```text
symbol
exchange_timestamp
exchange
token
price
sequence_number
received_at
```

---

# 6. S3 raw-data storage

The same processing Lambda also stores the market event in S3.

Bucket used by the implementation:

```text
stock-market-pipeline-himanshu-2026
```

Objects are organized by date and symbol.

Example:

```text
stock-data/
└── 2026/
    └── 10/
        └── 05/
            ├── RELIANCE/
            │   ├── 1760000001.json
            │   └── 1760000002.json
            ├── TCS/
            └── SBIN/
```

This gives the project two storage paths:

```text
DynamoDB
    -> application/query-oriented historical data

S3
    -> raw and durable market-data storage
```

The S3 layer also gives the project a natural starting point for a future data lake.

---

# 7. Stock Market API Lambda

The second Lambda is:

```text
stock-market-api
```

This Lambda is not connected directly to Kinesis.

It reads from DynamoDB and prepares the data needed by the frontend.

Its job is to find the latest record for every stock symbol.

The flow is:

```text
DynamoDB
    |
    v
stock-market-api Lambda
    |
    v
latest record per symbol
```

The implementation also handles DynamoDB scan pagination.

It then:

1. reads the records
2. groups them by symbol
3. compares `exchange_timestamp`
4. keeps the newest record
5. sorts the result by symbol
6. converts DynamoDB `Decimal` values
7. returns JSON
8. adds CORS headers

Example response:

```json
{
  "count": 4,
  "stocks": [
    {
      "symbol": "ICICIBANK",
      "exchange": "NSE",
      "price": 1332.10,
      "exchange_timestamp": 1760000001
    },
    {
      "symbol": "INFY",
      "exchange": "NSE",
      "price": 1019.20,
      "exchange_timestamp": 1760000002
    }
  ]
}
```

---

# 8. API Gateway

The API Lambda is exposed through Amazon API Gateway.

The frontend calls the API rather than accessing DynamoDB directly.

```text
React
  |
  | HTTPS GET /stocks
  v
API Gateway
  |
  v
stock-market-api Lambda
  |
  v
DynamoDB
```

This keeps the database behind an application/API layer.

The frontend uses the API Gateway URL in its JavaScript code.

---

# 9. React dashboard

The frontend is under:

```text
frontend/
```

It was created with React and Vite.

Main technologies:

- React
- Vite
- JavaScript
- CSS
- Fetch API

The frontend calls the API Gateway endpoint and displays the returned stock information.

Example client-side request:

```javascript
const API_URL =
  "https://YOUR_API_GATEWAY_URL/stocks";

async function getStocks() {
  try {
    const response = await fetch(API_URL);

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const data = await response.json();

    console.log("Stock count:", data.count);
    console.log("Stocks:", data.stocks);

    return data.stocks;
  } catch (error) {
    console.error("Failed to fetch stocks:", error);
  }
}
```

The frontend does not contain AWS credentials.

---

# 10. CloudWatch monitoring

CloudWatch was used throughout the project for logs and metrics.

The main things to watch are:

### EC2 producer

- authentication failures
- WebSocket failures
- Kinesis publishing errors
- producer process failures

### Kinesis

- incoming records
- incoming bytes
- iterator age
- write throughput issues

### Lambda

- invocations
- errors
- duration
- throttles

### DynamoDB

- read/write consumption
- throttling
- capacity-related issues

CloudWatch logs were also used during development to verify that events were moving through the pipeline.

---

# 11. IAM

IAM roles are used so AWS services can communicate without embedding AWS access keys in application code.

The producer's EC2 role is used for access to the required AWS resources.

The processing Lambda needs permissions for:

```text
Kinesis
DynamoDB
S3
CloudWatch Logs
```

The API Lambda needs:

```text
DynamoDB read access
CloudWatch Logs
```

The production goal is least-privilege access rather than giving broad permissions such as AdministratorAccess.

---

# 12. Monitoring and alarms

The monitoring architecture can be extended as:

```text
CloudWatch
     |
     v
CloudWatch Alarm
     |
     v
SNS
     |
     v
Notification
```

Useful alarms include:

```text
Lambda Errors > 0
Lambda Throttles
Kinesis Iterator Age too high
Kinesis write failures
DynamoDB throttling
Producer failure
```

---

# 13. Analytics layer

The raw data in S3 can later be queried using Athena.

Planned architecture:

```text
S3
 |
 v
AWS Glue Data Catalog
 |
 v
Amazon Athena
 |
 v
SQL Analytics
```

Example query:

```sql
SELECT
    symbol,
    AVG(price) AS average_price
FROM stock_data
GROUP BY symbol;
```

Possible analysis includes:

- average price
- minimum price
- maximum price
- symbol-wise analysis
- time-based analysis
- volatility calculations
- historical trends

This is an extension of the current implementation rather than a claim that Athena is already deployed.

---

# 14. Project development phases

The project was built incrementally.

## Phase 1 — Real-time data pipeline

Completed:

```text
EC2
 |
 v
Angel One
 |
 v
Kinesis
 |
 v
Lambda
 |
 v
DynamoDB
```

Also configured:

- EC2 IAM role
- Elastic IP
- Angel One authentication
- live WebSocket feed
- CloudWatch logs
- CloudWatch metrics

---

## Phase 2 — Historical DynamoDB design

The original approach stored the symbol as the key.

That meant a new price could replace the previous price.

The table was redesigned around:

```text
symbol
exchange_timestamp
```

This changed the system from a simple latest-price tracker into a historical event store.

---

## Phase 3 — S3 storage

The processing Lambda was extended so each market event is also written to S3.

```text
Kinesis
   |
   v
Lambda
   |
   +--> DynamoDB
   |
   +--> S3
```

---

## Phase 4 — Monitoring

CloudWatch was used for:

- Lambda logs
- Lambda metrics
- producer visibility
- Kinesis monitoring
- troubleshooting

The next production step is formal CloudWatch alarms connected to SNS.

---

## Phase 5 — Analytics foundation

S3 was organized so historical data can later be consumed by:

```text
Glue
  |
Athena
  |
SQL analytics
```

---

## Phase 6 — Dashboard

The frontend was added after the API layer.

```text
DynamoDB
    |
    v
API Lambda
    |
    v
API Gateway
    |
    v
React dashboard
```

The dashboard consumes the latest stock data through the API.

---

## Phase 7 — Production hardening

The final production direction is:

```text
Route 53
   |
CloudFront
   |
WAF
   |
API Gateway
   |
Lambda
   |
DynamoDB / S3

Monitoring:
CloudWatch -> SNS
```

Additional improvements can include:

- Secrets Manager
- Terraform
- GitHub Actions
- CI/CD
- API authentication
- retry policies
- dead-letter handling
- stronger observability
- infrastructure as code

---

# Repository structure

```text
stock-market-dashboard/
|
├── frontend/
|   ├── public/
|   ├── src/
|   │   ├── assets/
|   │   ├── App.jsx
|   │   ├── App.css
|   │   ├── index.css
|   │   └── main.jsx
|   ├── App.jsx
|   ├── index.html
|   ├── package.json
|   ├── package-lock.json
|   └── vite.config.js
|
├── producer/
|   ├── producer.py
|   ├── stock_market_producer.py
|   ├── test_angel.py
|   ├── test_feed.py
|   ├── .env.example
|   └── .gitignore
|
├── lambda/
|   ├── stock_market_processor.py
|   └── stock_market_api.py
|
├── .gitignore
└── README.md
```

---

# Local producer setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/stock-market-dashboard.git
cd stock-market-dashboard
```

Go to the producer:

```bash
cd producer
```

Create a Python environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages.

If a `requirements.txt` is added:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Add your own Angel One credentials to `.env`.

Never commit the file.

Run the producer:

```bash
python3 stock_market_producer.py
```

---

# Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The Vite development server normally runs on:

```text
http://localhost:5173
```

Update the API URL in the frontend to point to the deployed API Gateway endpoint.

---

# Lambda deployment

There are two Lambda functions.

### StockMarketProcessor

```text
lambda/stock_market_processor.py
```

Trigger:

```text
Amazon Kinesis
```

Permissions:

```text
Kinesis
DynamoDB
S3
CloudWatch Logs
```

### stock-market-api

```text
lambda/stock_market_api.py
```

Trigger:

```text
API Gateway
```

Permissions:

```text
DynamoDB read
CloudWatch Logs
```

---

# Security

The repository intentionally does not contain:

```text
.env
AWS access keys
AWS secret keys
Angel One credentials
TOTP secrets
private keys
.pem files
JWT tokens
passwords
```

The `.gitignore` protects secret and local files.

The example configuration is:

```text
producer/.env.example
```

with placeholder values only.

Before pushing changes, check:

```bash
git status
git diff --cached --name-only
```

Never use:

```bash
git add .env
```

---

# Important implementation notes

## DynamoDB historical storage

The combination of:

```text
symbol
exchange_timestamp
```

is important because the project receives many events for the same stock.

Without a sort key, a latest-value design can overwrite previous observations.

---

## API design

The frontend does not directly query DynamoDB.

Instead:

```text
React
 |
API Gateway
 |
Lambda
 |
DynamoDB
```

This makes it easier to add authentication, validation, caching, rate limiting, and other API controls later.

---

## S3 design

S3 is used for durable raw-data storage.

This means the application database and raw historical data are separated:

```text
DynamoDB -> application access
S3       -> durable raw data / analytics
```

---

# Testing

The producer contains two testing scripts.

### Angel One authentication

```text
test_angel.py
```

Used to verify:

- API authentication
- credentials
- TOTP
- SmartAPI session creation

### Live feed

```text
test_feed.py
```

Used to verify:

- feed token
- WebSocket connection
- stock subscription
- incoming market data

---

# Cost considerations

This project uses several AWS services that can incur charges.

Important cost areas:

- EC2 runtime
- Kinesis stream capacity
- Lambda invocations
- DynamoDB usage
- S3 storage
- API Gateway requests
- CloudWatch logs

For development, unused infrastructure should be stopped or removed.

For production, cost monitoring should be added through AWS Cost Explorer, Budgets, and CloudWatch where appropriate.

---

# Production improvements

The current implementation is a working project architecture. A production version could add:

### Security

- AWS Secrets Manager
- WAF
- API authentication
- stricter IAM policies
- private networking where appropriate

### Reliability

- Lambda retry configuration
- dead-letter queue
- failure destinations
- Kinesis retention strategy
- producer process supervision

### Deployment

- Terraform
- GitHub Actions
- automated testing
- CI/CD
- separate dev/staging/prod environments

### Observability

- CloudWatch dashboards
- alarms
- SNS notifications
- structured logging
- Prometheus/Grafana where useful

### Analytics

- Glue Data Catalog
- Athena
- QuickSight
- historical price analysis

---

# What I learned from the project

This project helped me work through several practical AWS concepts instead of only studying them theoretically:

- designing a streaming pipeline
- EC2 IAM roles
- Kinesis ingestion
- Lambda event processing
- DynamoDB key design
- S3 object organization
- API Gateway integration
- React API consumption
- CloudWatch debugging
- environment variables and secret handling
- separating producer, processing, storage and presentation layers
- designing a system that can later be extended into an analytics platform

---

# Technology stack

### AWS

- Amazon EC2
- Amazon Kinesis Data Streams
- AWS Lambda
- Amazon DynamoDB
- Amazon S3
- Amazon API Gateway
- Amazon CloudWatch
- AWS IAM
- Amazon SNS

### Backend

- Python
- boto3
- Angel One SmartAPI
- WebSocket
- pyotp

### Frontend

- React
- Vite
- JavaScript
- CSS
- Fetch API

### Development

- Linux
- Git
- GitHub

---

# Current status

The main implementation is complete:

```text
[✓] EC2 producer
[✓] Angel One authentication
[✓] Live WebSocket market feed
[✓] Kinesis streaming
[✓] Kinesis -> Lambda processing
[✓] DynamoDB historical storage
[✓] S3 raw data storage
[✓] API Lambda
[✓] API Gateway
[✓] React dashboard
[✓] CloudWatch logging/metrics
[✓] IAM roles
[✓] GitHub repository structure
[✓] Environment secret protection
```

The next engineering improvements are production hardening, formal alarms/SNS, infrastructure as code, CI/CD, and the Athena analytics layer.

---

# Author

## Himanshu Gohil

DevOps & Cloud Engineer

Areas of interest:

- AWS
- DevOps
- Cloud Architecture
- Kubernetes
- Terraform
- CI/CD
- Observability
- Real-time systems
- Cloud-native applications

---

# Project summary

This project started as a live stock-price application and evolved into a complete AWS streaming pipeline:

```text
Angel One
    |
    v
EC2 + Python
    |
    v
Kinesis
    |
    v
Lambda
   / \
  /   \
 v     v
DynamoDB  S3
   |
   v
API Lambda
   |
   v
API Gateway
   |
   v
React Dashboard
```

The main goal was not just to display stock prices, but to understand how the individual AWS components work together to build a real event-driven cloud system.
