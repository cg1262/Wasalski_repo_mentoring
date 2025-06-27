# Delta Share - co to jest?

## Co to jest Delta Share?

Delta Share to **otwarty protokół** do bezpiecznego udostępniania danych między organizacjami bez kopiowania danych. Umożliwia:
- **Cross-organization data sharing** - współdzielenie między firmami
- **No data movement** - dane pozostają u właściciela
- **Real-time access** - dostęp do najświeższych danych
- **Unified governance** - centralne zarządzanie dostępem
- **Multi-cloud support** - działa na AWS, Azure, GCP

### Architektura Delta Share:
```
Data Provider                    Data Recipient
├── Delta Tables                 ├── Client Application
├── Delta Share Server           ├── Delta Share Client
├── Access Control               └── Query Engine
└── Audit Logs                      (Spark, Pandas, etc.)
        │
        └─── HTTPS/REST API ─────────┘
```

## Główne koncepty

### 1. **Provider (Dostawca danych)**:
```
Delta Share Provider
├── Shares (logical grouping)
│   ├── Schema 1
│   │   ├── Table A
│   │   └── Table B
│   └── Schema 2
│       └── Table C
├── Recipients (who can access)
└── Access Control (permissions)
```

### 2. **Recipient (Odbiorca danych)**:
```
Data Recipient
├── Profile (connection details)
├── Shares (available to them)
└── Client Tools
    ├── Python/Pandas
    ├── Apache Spark
    ├── Power BI
    └── Tableau
```

### 3. **Security model**:
```
Security Layers
├── Authentication (bearer tokens)
├── Authorization (per-table permissions)
├── Encryption (TLS in transit)
├── Audit logging (access tracking)
└── Data lineage (usage monitoring)
```

## Setup Delta Share Server

### 1. **Instalacja i konfiguracja**:

```bash
# Download Delta Share server
wget https://github.com/delta-io/delta-sharing/releases/download/v0.6.4/delta-sharing-server-0.6.4.zip
unzip delta-sharing-server-0.6.4.zip
cd delta-sharing-server-0.6.4
```

#### Konfiguracja serwera:
```yaml
# conf/delta-sharing-server.yaml
version: 1
shares:
- name: "sales_data_share"
  schemas:
  - name: "sales"
    tables:
    - name: "transactions"
      location: "s3://my-bucket/delta-tables/transactions/"
    - name: "customers" 
      location: "s3://my-bucket/delta-tables/customers/"
  - name: "marketing"
    tables:
    - name: "campaigns"
      location: "s3://my-bucket/delta-tables/campaigns/"

host: "0.0.0.0"
port: 8080
endpoint: "/delta-sharing/"

# Authorization (bearer tokens)
authorization:
  bearerTokens:
    - "recipient1-token-12345": 
        - "sales_data_share"
    - "recipient2-token-67890":
        - "sales_data_share"

# Storage configuration
storage:
  s3:
    region: "us-west-2"
    # AWS credentials via IAM role or environment variables

# Logging
logging:
  level: "INFO"
  file: "/var/log/delta-sharing/server.log"
```

#### Uruchomienie serwera:
```bash
# Start server
./bin/delta-sharing-server \
  --config conf/delta-sharing-server.yaml

# Server będzie dostępny na http://localhost:8080
```

### 2. **Docker deployment**:

```dockerfile
# Dockerfile dla Delta Share Server
FROM openjdk:11-jre-slim

# Install Delta Share Server
WORKDIR /opt/delta-sharing
COPY delta-sharing-server-0.6.4 .

# Copy configuration
COPY conf/delta-sharing-server.yaml conf/

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/delta-sharing/health || exit 1

# Start server
CMD ["./bin/delta-sharing-server", "--config", "conf/delta-sharing-server.yaml"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  delta-share-server:
    build: .
    ports:
      - "8080:8080"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=us-west-2
    volumes:
      - ./conf:/opt/delta-sharing/conf
      - ./logs:/var/log/delta-sharing
    restart: unless-stopped

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - delta-share-server
    restart: unless-stopped
```

## Client-side - konsumowanie danych

### 1. **Python Delta Share Client**:

```python
# pip install delta-sharing

import delta_sharing
import pandas as pd

# Profile configuration (connection details)
profile = {
    "shareCredentialsVersion": 1,
    "endpoint": "https://my-delta-share-server.com/delta-sharing/",
    "bearerToken": "recipient1-token-12345"
}

# Save profile to file
import json
with open("profile.json", "w") as f:
    json.dump(profile, f)

# Initialize client
client = delta_sharing.SharingClient("profile.json")

# List available shares
shares = client.list_shares()
print("Available shares:")
for share in shares:
    print(f"  - {share.name}")

# List schemas in a share
schemas = client.list_schemas("sales_data_share")
print("\nAvailable schemas:")
for schema in schemas:
    print(f"  - {schema.name}")

# List tables in schema
tables = client.list_tables("sales_data_share.sales")
print("\nAvailable tables:")
for table in tables:
    print(f"  - {table.name}")

# Load table as Pandas DataFrame
df = delta_sharing.load_as_pandas(
    "profile.json",
    "sales_data_share.sales.transactions"
)

print(f"\nLoaded transactions table: {len(df)} rows")
print(df.head())

# Load with filtering (predicate pushdown)
filtered_df = delta_sharing.load_as_pandas(
    "profile.json", 
    "sales_data_share.sales.transactions",
    predicates=["date >= '2024-01-01'", "amount > 100"]
)

print(f"Filtered data: {len(filtered_df)} rows")

# Get table version and metadata
table_version = client.get_table_version("sales_data_share.sales.transactions")
print(f"Table version: {table_version}")

table_metadata = client.get_table_metadata("sales_data_share.sales.transactions")
print(f"Table schema: {table_metadata.schema}")
```

### 2. **Spark integration**:

```python
from pyspark.sql import SparkSession

# Setup Spark with Delta Share
spark = SparkSession.builder \
    .appName("DeltaShareExample") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtensions") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Load shared table
df = spark.read \
    .format("deltaSharing") \
    .option("profile", "profile.json") \
    .load("sales_data_share.sales.transactions")

# Show data
df.show(10)

# Create temporary view for SQL queries
df.createOrReplaceTempView("shared_transactions")

# SQL queries on shared data
result = spark.sql("""
    SELECT 
        DATE(date) as transaction_date,
        COUNT(*) as transaction_count,
        SUM(amount) as total_amount
    FROM shared_transactions 
    WHERE date >= '2024-01-01'
    GROUP BY DATE(date)
    ORDER BY transaction_date
""")

result.show()

# Join with local data
local_customers = spark.read.parquet("local_customers.parquet")

joined_data = spark.sql("""
    SELECT 
        t.transaction_id,
        t.amount,
        c.customer_name,
        c.customer_segment
    FROM shared_transactions t
    JOIN local_customers c ON t.customer_id = c.customer_id
""")

joined_data.show()
```

### 3. **Streaming consumption**:

```python
# Real-time streaming z Delta Share
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("DeltaShareStreaming") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# Stream shared table changes
shared_stream = spark.readStream \
    .format("deltaSharing") \
    .option("profile", "profile.json") \
    .option("startingVersion", "latest") \
    .load("sales_data_share.sales.transactions")

# Process stream
processed_stream = shared_stream \
    .withColumn("processing_time", current_timestamp()) \
    .withColumn("amount_category", 
                when(col("amount") > 1000, "high")
                .when(col("amount") > 100, "medium")
                .otherwise("low"))

# Output to console
query = processed_stream.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
```

## Advanced Delta Share features

### 1. **Change Data Feed**:

```python
# Enable Change Data Feed na provider side
from delta.tables import DeltaTable

# Enable CDF for existing table
delta_table = DeltaTable.forPath(spark, "s3://bucket/transactions/")
delta_table.alter().property("delta.enableChangeDataFeed", "true").execute()

# Read changes from shared table
changes_df = spark.read \
    .format("deltaSharing") \
    .option("profile", "profile.json") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 10) \
    .option("endingVersion", 15) \
    .load("sales_data_share.sales.transactions")

# CDF columns: _change_type, _commit_version, _commit_timestamp
changes_df.select("_change_type", "_commit_version", "transaction_id", "amount").show()

# Filter by change type
inserts_only = changes_df.filter(col("_change_type") == "insert")
updates_only = changes_df.filter(col("_change_type") == "update_postimage")
deletes_only = changes_df.filter(col("_change_type") == "delete")
```

### 2. **Time Travel through shares**:

```python
# Read historical version of shared table
historical_df = spark.read \
    .format("deltaSharing") \
    .option("profile", "profile.json") \
    .option("versionAsOf", 5) \
    .load("sales_data_share.sales.transactions")

# Read as of timestamp
timestamp_df = spark.read \
    .format("deltaSharing") \
    .option("profile", "profile.json") \
    .option("timestampAsOf", "2024-01-15") \
    .load("sales_data_share.sales.transactions")

# Compare versions
current_count = df.count()
historical_count = historical_df.count()
print(f"Current: {current_count}, Historical: {historical_count}")
```

### 3. **Row-level security**:

```yaml
# Advanced server configuration with row filtering
version: 1
shares:
- name: "regional_sales"
  schemas:
  - name: "sales"
    tables:
    - name: "transactions"
      location: "s3://bucket/transactions/"
      # Row-level filters per recipient
      filters:
        "recipient-europe-token": "region = 'EU'"
        "recipient-asia-token": "region = 'ASIA'"
        "recipient-americas-token": "region = 'Americas'"
```

### 4. **Monitoring i audit**:

```python
# Custom audit logging
import logging
from datetime import datetime

class DeltaShareAuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("delta_share_audit")
        handler = logging.FileHandler("/var/log/delta-share-audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_access(self, recipient_token, share_name, table_name, 
                   rows_accessed=None, bytes_transferred=None):
        """Log data access"""
        self.logger.info(f"ACCESS - Token: {recipient_token[:10]}... "
                        f"Share: {share_name} Table: {table_name} "
                        f"Rows: {rows_accessed} Bytes: {bytes_transferred}")
    
    def log_share_created(self, share_name, created_by):
        """Log share creation"""
        self.logger.info(f"SHARE_CREATED - Name: {share_name} "
                        f"CreatedBy: {created_by}")
    
    def log_permission_granted(self, recipient_token, share_name, granted_by):
        """Log permission grant"""
        self.logger.info(f"PERMISSION_GRANTED - Token: {recipient_token[:10]}... "
                        f"Share: {share_name} GrantedBy: {granted_by}")

# Usage tracking
class DeltaShareMetrics:
    def __init__(self):
        self.access_counts = {}
        self.data_transferred = {}
    
    def track_access(self, recipient, table, rows, bytes_size):
        """Track access metrics"""
        key = f"{recipient}:{table}"
        
        if key not in self.access_counts:
            self.access_counts[key] = 0
            self.data_transferred[key] = 0
        
        self.access_counts[key] += 1
        self.data_transferred[key] += bytes_size
    
    def get_usage_report(self):
        """Generate usage report"""
        report = []
        for key, count in self.access_counts.items():
            recipient, table = key.split(":", 1)
            bytes_transferred = self.data_transferred[key]
            
            report.append({
                "recipient": recipient,
                "table": table,
                "access_count": count,
                "bytes_transferred": bytes_transferred,
                "mb_transferred": bytes_transferred / 1024 / 1024
            })
        
        return sorted(report, key=lambda x: x["bytes_transferred"], reverse=True)

# Example usage
audit_logger = DeltaShareAuditLogger()
metrics = DeltaShareMetrics()

# Simulate access tracking
audit_logger.log_access("recipient1-token", "sales_data", "transactions", 1000, 2048000)
metrics.track_access("recipient1", "sales.transactions", 1000, 2048000)

print("Usage Report:")
for item in metrics.get_usage_report():
    print(f"  {item['recipient']} - {item['table']}: "
          f"{item['access_count']} accesses, {item['mb_transferred']:.1f} MB")
```

## Production deployment

### 1. **High Availability setup**:

```yaml
# kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: delta-share-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: delta-share-server
  template:
    metadata:
      labels:
        app: delta-share-server
    spec:
      containers:
      - name: delta-share-server
        image: my-registry/delta-share-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: AWS_REGION
          value: "us-west-2"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /delta-sharing/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /delta-sharing/health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: delta-share-service
spec:
  selector:
    app: delta-share-server
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: delta-share-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - delta-share.mycompany.com
    secretName: delta-share-tls
  rules:
  - host: delta-share.mycompany.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: delta-share-service
            port:
              number: 80
```

### 2. **Security hardening**:

```python
# Enhanced security configuration
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta

class EnhancedTokenManager:
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def generate_recipient_token(self, recipient_id, shares, expires_hours=24):
        """Generate JWT token for recipient"""
        payload = {
            "recipient_id": recipient_id,
            "shares": shares,
            "issued_at": datetime.utcnow().timestamp(),
            "expires_at": (datetime.utcnow() + timedelta(hours=expires_hours)).timestamp()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
    
    def validate_token(self, token):
        """Validate and decode token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Check expiration
            if datetime.utcnow().timestamp() > payload["expires_at"]:
                raise Exception("Token expired")
            
            return payload
        except jwt.InvalidTokenError as e:
            raise Exception(f"Invalid token: {e}")
    
    def revoke_token(self, token):
        """Add token to revocation list"""
        # In production, store in Redis or database
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        # Add to revocation list
        pass

# Rate limiting
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id):
        """Check if request is allowed"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] 
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True

# Example middleware
token_manager = EnhancedTokenManager("your-secret-key")
rate_limiter = RateLimiter(max_requests=1000, window_seconds=3600)

def security_middleware(request):
    """Security validation middleware"""
    
    # Extract token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise Exception("Missing or invalid authorization header")
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    # Validate token
    payload = token_manager.validate_token(token)
    client_id = payload["recipient_id"]
    
    # Rate limiting
    if not rate_limiter.is_allowed(client_id):
        raise Exception("Rate limit exceeded")
    
    return payload
```

## Use cases i korzyści

### 1. **Cross-company analytics**:
```python
# Company A shares sales data with Company B for joint analytics
# Company B shares marketing data with Company A

# Company A (Provider)
company_a_config = {
    "shares": {
        "joint_analytics": {
            "schemas": {
                "sales": ["transactions", "customers"],
                "inventory": ["products", "stock_levels"]
            }
        }
    },
    "recipients": {
        "company_b_token": ["joint_analytics"]
    }
}

# Company B (Consumer + Provider)
company_b_config = {
    "consumes": {
        "company_a_sales": "joint_analytics.sales.transactions"
    },
    "provides": {
        "marketing_share": {
            "schemas": {
                "campaigns": ["ad_performance", "customer_segments"]
            }
        }
    }
}
```

### 2. **Data marketplace**:
```python
# Data marketplace scenario
marketplace_shares = {
    "financial_data": {
        "provider": "FinanceCorpInc",
        "schemas": {
            "market_data": ["stock_prices", "trading_volumes"],
            "economic_indicators": ["gdp", "inflation", "employment"]
        },
        "pricing": "per_query",
        "cost_per_gb": 0.10
    },
    "weather_data": {
        "provider": "WeatherGlobal",
        "schemas": {
            "forecasts": ["daily", "hourly"],
            "historical": ["temperature", "precipitation"]
        },
        "pricing": "subscription",
        "monthly_cost": 500.00
    }
}
```

### 3. **Regulatory compliance**:
```python
# GDPR/CCPA compliant data sharing
compliance_config = {
    "data_retention": {
        "max_days": 90,
        "auto_cleanup": True
    },
    "privacy_controls": {
        "pii_filtering": True,
        "anonymization": "k_anonymity",
        "consent_required": True
    },
    "audit_requirements": {
        "log_all_access": True,
        "retention_period": "7_years",
        "export_capability": True
    }
}
```

## Porównanie z alternatywami

| Feature | Delta Share | Data Warehouse | File Transfer | API |
|---------|-------------|----------------|---------------|-----|
| **Data Movement** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Real-time** | ✅ Yes | ❌ Batch | ❌ Manual | ✅ Yes |
| **Governance** | ✅ Centralized | ⚠️ Complex | ❌ Manual | ⚠️ Distributed |
| **Cost** | 💰 Low | 💰💰 High | 💰 Medium | 💰💰 Medium |
| **Security** | ✅ Built-in | ✅ Configurable | ❌ Manual | ⚠️ Custom |
| **Scalability** | ✅ High | ⚠️ Limited | ❌ Poor | ✅ High |

## Podsumowanie

### ✅ Używaj Delta Share gdy:
- Cross-organization data sharing
- Real-time access do danych
- Centralized governance wymagana
- Minimalne data movement
- Multi-cloud environment
- Compliance requirements

### ❌ Unikaj Delta Share gdy:
- Simple internal sharing
- Batch-only requirements
- Legacy systems integration
- High-frequency small queries
- Custom transformation needs

### 🔧 Best Practices:
- ✅ Implementuj strong authentication
- ✅ Monitor usage i costs
- ✅ Use row-level security
- ✅ Regular audit logs review
- ✅ Version control share configs
- ✅ Test disaster recovery
- ✅ Document data lineage

**Delta Share = Secure, governed data sharing without data movement** 🤝