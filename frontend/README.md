# 📈 Stock Market Dashboard — AWS Serverless

A cloud-native stock market dashboard built with **React + Vite** and an **AWS serverless backend** using Amazon API Gateway, AWS Lambda, and Amazon DynamoDB.

The project demonstrates how to build and integrate a scalable, API-driven application using managed AWS services.

---

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      Web Browser      │
                         │    React + Vite       │
                         └──────────┬───────────┘
                                    │
                              HTTPS Request
                              GET /stocks
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Amazon API Gateway │
                         │      REST API        │
                         │       /stocks        │
                         └──────────┬───────────┘
                                    │
                              Invoke Lambda
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      AWS Lambda      │
                         │   Stock API Logic    │
                         │       Python         │
                         └──────────┬───────────┘
                                    │
                              Query Data
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Amazon DynamoDB   │
                         │   Stock Market Data  │
                         │    5,477+ Records    │
                         └──────────────────────┘

              Supporting AWS Services
          ┌────────┬──────────┬───────────┐
          │  IAM   │CloudWatch│ CloudTrail│
          │ Access │  Logs    │  Auditing │
          └────────┴──────────┴───────────┘
```

### Request Flow

1. User opens the React dashboard.
2. React sends an HTTPS `GET /stocks` request.
3. Amazon API Gateway receives the request.
4. API Gateway invokes the AWS Lambda function.
5. Lambda queries stock data from DynamoDB.
6. Lambda formats the response as JSON.
7. API Gateway returns the response to the frontend.
8. React renders the stock market data in the dashboard.

---

## 🎯 Project Overview

The goal of this project was to build an end-to-end AWS application demonstrating:

- Serverless backend architecture
- REST API development
- AWS Lambda integration
- NoSQL database integration
- React frontend development
- Cloud-based application design
- IAM-based access control
- AWS monitoring and logging
- Git/GitHub version control

The application currently displays **5,477+ stock records** retrieved through the AWS API.

---

## ✨ Features

### Frontend

- 📊 Stock market dashboard
- 🔄 Refresh stock data
- 📈 Latest stock price display
- 🏢 Exchange information
- 🔢 Total record count
- 📋 Stock market data table
- 🌐 API-driven data loading
- 📱 Responsive dashboard interface

### Backend

- ⚡ AWS Lambda serverless API
- 🔗 Amazon API Gateway REST endpoint
- 🗄️ Amazon DynamoDB data storage
- 🔐 IAM permissions
- 📊 CloudWatch logging
- 🔎 CloudTrail auditing

---

## 🛠️ Technology Stack

### Frontend

| Technology | Purpose |
|---|---|
| React | Frontend UI |
| Vite | Development & build tooling |
| JavaScript | Application logic |
| HTML5 | Structure |
| CSS | Styling |

### AWS

| AWS Service | Purpose |
|---|---|
| Amazon API Gateway | REST API |
| AWS Lambda | Serverless backend |
| Amazon DynamoDB | Stock data storage |
| AWS IAM | Access control |
| Amazon CloudWatch | Logging & monitoring |
| AWS CloudTrail | API auditing |

### DevOps / Tools

| Tool | Purpose |
|---|---|
| Git | Version control |
| GitHub | Source code hosting |
| SSH | Secure EC2 access |
| Linux | Development environment |

---

## 🔌 API

### Get Stock Data

```http
GET /stocks
```

API endpoint:

```text
https://hp2m8veeog.execute-api.ap-south-1.amazonaws.com/stocks
```

### Example Response

```json
{
  "count": 5477,
  "stocks": [
    {
      "symbol": "INFY",
      "exchange": "NSE",
      "price": 1019.25,
      "token": 1594
    }
  ]
}
```

---

## 📊 Dashboard

The dashboard displays:

- Total stock records
- Stock symbol
- Exchange
- Latest price
- Token
- Sequence number
- Received timestamp

Example:

```text
┌─────────────────────────────────────────────────┐
│             📈 Stock Market Dashboard           │
│       AWS Lambda + API Gateway + DynamoDB       │
├───────────┬───────────┬───────────┬─────────────┤
│  Records  │  Symbol   │  Exchange │ Latest Price│
│   5,477   │   INFY    │    NSE    │  ₹1019.25   │
├───────────┴───────────┴───────────┴─────────────┤
│                  Market Data                    │
├────────┬──────────┬────────┬──────────┬─────────┤
│ Symbol │ Exchange │ Price  │ Sequence │ Time    │
├────────┼──────────┼────────┼──────────┼─────────┤
│ INFY   │ NSE      │₹1019.25│ 15696380 │ ...     │
│ INFY   │ NSE      │₹1019.30│ 15697775 │ ...     │
└────────┴──────────┴────────┴──────────┴─────────┘
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have:

- Node.js 22+
- npm
- Git
- AWS account
- AWS API Gateway endpoint
- AWS Lambda function
- DynamoDB table

---

## 📥 Clone Repository

```bash
git clone https://github.com/himanshugohil18/stock-market-dashboard.git
cd stock-market-dashboard
```

---

## 📦 Install Dependencies

```bash
npm install
```

---

## ▶️ Run Development Server

```bash
npm run dev
```

The application will be available at:

```text
http://localhost:5173
```

---

## 🔧 API Configuration

The frontend uses the AWS API Gateway endpoint.

```javascript
const API_URL =
  "https://hp2m8veeog.execute-api.ap-south-1.amazonaws.com/stocks";
```

The frontend fetches stock data using:

```javascript
const response = await fetch(API_URL);
const data = await response.json();
```

---

## 📁 Project Structure

```text
stock-market-dashboard/
│
├── public/
│
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   └── ...
│
├── .gitignore
├── index.html
├── package.json
├── package-lock.json
├── vite.config.js
└── README.md
```

---

## ☁️ AWS Architecture

### Amazon API Gateway

Acts as the public API entry point for the frontend.

```text
Client
  │
  │ HTTPS
  ▼
API Gateway
  │
  ▼
Lambda
```

### AWS Lambda

Handles the application logic and retrieves stock data from DynamoDB.

```text
API Gateway
     │
     ▼
AWS Lambda
     │
     ▼
DynamoDB
```

### Amazon DynamoDB

Stores stock market records in a scalable NoSQL database.

---

## 🔐 Security

The project follows AWS security principles by using:

- IAM permissions
- Least-privilege access where applicable
- HTTPS API communication
- AWS-managed services
- No AWS credentials stored in source code

> **Important:** Never commit AWS access keys, secret keys, passwords, tokens, or `.env` files to GitHub.

---

## 📈 Scalability

The architecture is based on managed AWS services:

```text
React
  │
  ▼
API Gateway
  │
  ▼
Lambda
  │
  ▼
DynamoDB
```

This approach minimizes server management and allows AWS services to handle infrastructure scaling.

---

## 📊 Monitoring

AWS CloudWatch can be used to monitor:

- Lambda invocations
- Lambda errors
- Lambda duration
- API Gateway requests
- API Gateway errors
- Application logs

AWS CloudTrail can be used for auditing AWS API activity.

---

## 🧪 Testing

The API can be tested independently:

```bash
curl "https://hp2m8veeog.ap-south-1.amazonaws.com/stocks"
```

> Replace the URL above with the current API Gateway endpoint if it changes.

Expected response:

```json
{
  "count": 5477,
  "stocks": []
}
```

The frontend can then consume the same API endpoint.

---

## 💡 Engineering Concepts Demonstrated

This project demonstrates practical knowledge of:

- REST API architecture
- Serverless computing
- Event-driven cloud architecture
- NoSQL database design
- API integration
- IAM security
- Cloud monitoring
- Cloud auditing
- React application development
- Linux-based development
- Git workflow
- AWS regional architecture

---

## 🚀 Future Improvements

- [ ] Deploy React frontend using Amazon S3
- [ ] Add Amazon CloudFront CDN
- [ ] Configure custom domain with Route 53
- [ ] Configure HTTPS using ACM
- [ ] Implement GitHub Actions CI/CD
- [ ] Add stock search
- [ ] Add pagination
- [ ] Add price history charts
- [ ] Add authentication
- [ ] Add CloudWatch alarms
- [ ] Add API rate limiting
- [ ] Improve API caching
- [ ] Add automated testing

### Planned Production Architecture

```text
                    GitHub
                       │
                       ▼
                GitHub Actions
                       │
                       ▼
                React Build
                       │
                       ▼
                 Amazon S3
                       │
                       ▼
                CloudFront CDN
                       │
                       ▼
                    Users

                    API
                     │
                     ▼
              API Gateway
                     │
                     ▼
                  Lambda
                     │
                     ▼
                DynamoDB
```

---

## 🌎 AWS Region

```text
ap-south-1
Mumbai, India
```

---

## 📌 Project Status

```text
Status: Completed ✅

Frontend:         React + Vite       ✅
API:              API Gateway        ✅
Backend:          AWS Lambda         ✅
Database:         DynamoDB           ✅
IAM:              Configured         ✅
Monitoring:       CloudWatch         ✅
Version Control:  Git + GitHub       ✅
```

---

## 👨‍💻 Author

### Himanshu Gohil

**DevOps & Cloud Engineer | AWS | Kubernetes | Docker | Terraform | CI/CD**

GitHub:  
https://github.com/himanshugohil18

---

## ⭐ If you found this project useful

Give the repository a ⭐ and feel free to explore the implementation.

---

## 📄 License

This project is available for educational and portfolio purposes.

