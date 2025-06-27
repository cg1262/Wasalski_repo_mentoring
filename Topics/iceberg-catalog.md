# Iceberg Catalog - co to jest?

## Co to jest Iceberg Catalog?

Iceberg Catalog to **centralny rejestr metadanych** dla tabel Apache Iceberg. Pełni rolę "bazy danych" która śledzi:
- Lokalizacje tabel
- Schema tabel  
- Snapshots i wersje
- Partitioning information
- Table properties

### Dlaczego potrzebny jest Catalog?

```
Bez Catalog:
├── Pliki danych rozrzucone po storage
├── Brak centralnej informacji o tabelach
├── Trudne discovery 
├── Problemy z concurrent access
└── Zarządzanie metadata ręczne

Z Catalog:
├── Centralna rejestracja tabel
├── Metadata management
├── Atomowe operacje
├── Multi-engine compatibility
└── Security & governance
```

## Typy Iceberg Catalog

### 1. **Hive Metastore Catalog**

#### Konfiguracja Hive Catalog:
```python
from pyiceberg.catalog import load_catalog

# Hive Metastore catalog
catalog = load_catalog("hive", 
    type="hive",
    uri="thrift://hive-metastore:9083",  # Hive Metastore URI
    warehouse="s3://my-data-lake/warehouse/"
)

# Lista baz danych
databases = catalog.list_namespaces()
print("Databases:", databases)

# Lista tabel w bazie
tables = catalog.list_tables("default")
print("Tables in default:", tables)
```

#### Docker setup Hive Metastore:
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: metastore
      POSTGRES_USER: hive
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
  
  hive-metastore:
    image: apache/hive:3.1.3
    depends_on:
      - postgres
    environment:
      SERVICE_NAME: metastore
      DB_DRIVER: postgres
      SERVICE_OPTS: >
        -Djavax.jdo.option.ConnectionDriverName=org.postgresql.Driver
        -Djavax.jdo.option.ConnectionURL=jdbc:postgresql://postgres:5432/metastore
        -Djavax.jdo.option.ConnectionUserName=hive
        -Djavax.jdo.option.ConnectionPassword=password
    ports:
      - "9083:9083"
```

### 2. **AWS Glue Catalog**

#### Setup AWS Glue:
```python
import boto3
from pyiceberg.catalog import load_catalog

# AWS Glue catalog
catalog = load_catalog("glue",
    type="glue",
    warehouse="s3://my-data-lake/warehouse/",
    # AWS credentials z environment variables lub IAM role
)

# Lista baz danych w Glue
databases = catalog.list_namespaces()
print("Glue databases:", databases)

# Utwórz bazę danych
catalog.create_namespace("analytics")

# Utwórz tabelę w Glue
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, LongType, TimestampType

schema = Schema(
    NestedField(field_id=1, name="id", field_type=LongType(), required=True),
    NestedField(field_id=2, name="name", field_type=StringType(), required=True),
    NestedField(field_id=3, name="created_at", field_type=TimestampType(), required=True)
)

table = catalog.create_table(
    identifier="analytics.users",
    schema=schema,
    location="s3://my-data-lake/warehouse/analytics/users/"
)

print(f"Created table in Glue: {table}")
```

#### AWS Glue integration z Spark:
```python
# PySpark z Glue Catalog
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("IcebergGlueExample") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.glue_catalog.warehouse", "s3://my-data-lake/warehouse/") \
    .config("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog") \
    .config("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
    .getOrCreate()

# Użyj Glue catalog w SQL
spark.sql("CREATE DATABASE IF NOT EXISTS glue_catalog.analytics")

spark.sql("""
CREATE TABLE IF NOT EXISTS glue_catalog.analytics.events (
    id bigint,
    user_id bigint,
    event_type string,
    timestamp timestamp,
    properties map<string, string>
) USING ICEBERG
PARTITIONED BY (days(timestamp))
""")

# Wstaw dane
spark.sql("""
INSERT INTO glue_catalog.analytics.events VALUES 
(1, 123, 'click', TIMESTAMP '2024-01-15 10:30:00', map('page', 'home')),
(2, 124, 'view', TIMESTAMP '2024-01-15 11:00:00', map('page', 'product'))
""")

# Query
df = spark.sql("SELECT * FROM glue_catalog.analytics.events")
df.show()
```

### 3. **REST Catalog**

#### REST Catalog Server setup:
```bash
# Start REST catalog server (Java)
wget https://github.com/apache/iceberg/releases/download/apache-iceberg-1.4.0/iceberg-rest-catalog-1.4.0.jar

java -jar iceberg-rest-catalog-1.4.0.jar \
  --warehouse=s3://my-data-lake/warehouse/ \
  --catalog-backend=postgresql \
  --jdbc-url=jdbc:postgresql://localhost:5432/iceberg_catalog \
  --jdbc-user=iceberg \
  --jdbc-password=password
```

#### Python client dla REST Catalog:
```python
from pyiceberg.catalog import load_catalog

# REST catalog client
catalog = load_catalog("rest",
    type="rest",
    uri="http://localhost:8181",  # REST catalog server
    # Optional authentication
    # credential="user:password",
    # token="bearer_token"
)

# Wszystkie operacje jak w innych katalogach
databases = catalog.list_namespaces()
print("REST catalog databases:", databases)

# Utwórz namespace
catalog.create_namespace("lakehouse")

# Lista tabel
tables = catalog.list_tables("lakehouse")
print("Tables:", tables)
```

#### REST Catalog z autentykacją:
```python
import requests
from pyiceberg.catalog import load_catalog

# Custom authentication
class RestCatalogWithAuth:
    def __init__(self, base_uri, username, password):
        self.base_uri = base_uri
        self.session = requests.Session()
        
        # Login i pobierz token
        login_response = self.session.post(
            f"{base_uri}/v1/oauth/tokens",
            json={
                "grant_type": "password",
                "username": username,
                "password": password
            }
        )
        
        token = login_response.json()["access_token"]
        self.session.headers.update({
            "Authorization": f"Bearer {token}"
        })
    
    def get_catalog(self):
        return load_catalog("rest",
            type="rest", 
            uri=self.base_uri,
            token=self.session.headers["Authorization"].split(" ")[1]
        )

# Użycie
auth_catalog = RestCatalogWithAuth(
    "https://my-catalog-server.com",
    "username", 
    "password"
).get_catalog()
```

### 4. **Local/File-based Catalog**

#### SQLite catalog dla development:
```python
from pyiceberg.catalog import load_catalog
import os

# Local SQLite catalog
catalog = load_catalog("local",
    type="sql",
    uri="sqlite:///./iceberg_catalog.db",
    warehouse="file:///tmp/iceberg_warehouse"
)

# Utwórz namespace
catalog.create_namespace("dev")

# Utwórz tabelę
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, LongType

schema = Schema(
    NestedField(field_id=1, name="id", field_type=LongType(), required=True),
    NestedField(field_id=2, name="data", field_type=StringType(), required=False)
)

table = catalog.create_table(
    identifier="dev.test_table",
    schema=schema
)

# Dodaj dane
import pandas as pd
import pyarrow as pa

df = pd.DataFrame({
    'id': [1, 2, 3],
    'data': ['a', 'b', 'c']
})

arrow_table = pa.Table.from_pandas(df)
table.append(arrow_table)

# Sprawdź lokalne pliki
warehouse_path = "/tmp/iceberg_warehouse"
print("Warehouse contents:")
for root, dirs, files in os.walk(warehouse_path):
    level = root.replace(warehouse_path, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        print(f"{subindent}{file}")
```

## Catalog Management Operations

### 1. **Namespace (Database) management**:

```python
# Utwórz namespace z properties
catalog.create_namespace(
    namespace="production",
    properties={
        "owner": "data-team",
        "description": "Production analytics data",
        "location": "s3://prod-data-lake/",
        "retention_days": "365"
    }
)

# Aktualizuj properties namespace
catalog.update_namespace_properties(
    namespace="production",
    updates={
        "owner": "analytics-team",
        "last_updated": "2024-01-15"
    }
)

# Usuń namespace (jeśli pusty)
# catalog.drop_namespace("test_namespace")

# Lista wszystkich namespaces
for namespace in catalog.list_namespaces():
    props = catalog.load_namespace_properties(namespace)
    print(f"Namespace: {namespace}")
    for key, value in props.items():
        print(f"  {key}: {value}")
```

### 2. **Table Discovery i Metadata**:

```python
# Lista wszystkich tabel
all_tables = []
for namespace in catalog.list_namespaces():
    tables = catalog.list_tables(namespace)
    for table in tables:
        all_tables.append(f"{namespace}.{table}")

print("All tables in catalog:")
for table_name in all_tables:
    print(f"  {table_name}")

# Szczegóły tabeli
def describe_table(catalog, table_identifier):
    """Opisz tabelę - schema, partitions, snapshots"""
    table = catalog.load_table(table_identifier)
    
    print(f"\n=== Table: {table_identifier} ===")
    print(f"Location: {table.metadata.location}")
    print(f"Current Schema ID: {table.metadata.current_schema_id}")
    
    # Schema
    print("\nSchema:")
    for field in table.schema().fields:
        required = "required" if field.required else "optional"
        print(f"  {field.name}: {field.field_type} ({required})")
    
    # Partitioning
    if table.spec().fields:
        print("\nPartitioning:")
        for partition_field in table.spec().fields:
            print(f"  {partition_field.name}: {partition_field.transform}")
    else:
        print("\nPartitioning: None")
    
    # Snapshots
    snapshots = table.metadata.snapshots
    print(f"\nSnapshots ({len(snapshots)}):")
    for snapshot in snapshots[-5:]:  # Last 5 snapshots
        print(f"  {snapshot.snapshot_id}: {snapshot.timestamp_ms}")
    
    # Table properties
    if table.metadata.properties:
        print("\nTable Properties:")
        for key, value in table.metadata.properties.items():
            print(f"  {key}: {value}")

# Użycie
for table_name in all_tables[:3]:  # Pierwsze 3 tabele
    try:
        describe_table(catalog, table_name)
    except Exception as e:
        print(f"Error describing {table_name}: {e}")
```

### 3. **Table Evolution tracking**:

```python
from datetime import datetime, timedelta

def track_table_changes(catalog, table_identifier, days_back=7):
    """Śledź zmiany w tabeli przez ostatnie X dni"""
    table = catalog.load_table(table_identifier)
    
    cutoff_time = (datetime.now() - timedelta(days=days_back)).timestamp() * 1000
    
    recent_snapshots = [
        s for s in table.metadata.snapshots 
        if s.timestamp_ms > cutoff_time
    ]
    
    print(f"\nChanges in {table_identifier} (last {days_back} days):")
    print(f"Total snapshots: {len(recent_snapshots)}")
    
    for snapshot in recent_snapshots:
        timestamp = datetime.fromtimestamp(snapshot.timestamp_ms / 1000)
        operation = snapshot.summary.get('operation', 'unknown')
        added_files = snapshot.summary.get('added-data-files', '0')
        deleted_files = snapshot.summary.get('deleted-data-files', '0')
        
        print(f"  {timestamp.strftime('%Y-%m-%d %H:%M:%S')}: "
              f"{operation} (+{added_files}/-{deleted_files} files)")

# Monitoring wielu tabel
monitored_tables = ["analytics.users", "analytics.events"]
for table_name in monitored_tables:
    try:
        track_table_changes(catalog, table_name, days_back=30)
    except Exception as e:
        print(f"Error tracking {table_name}: {e}")
```

## Multi-Catalog Setup

### 1. **Multi-catalog configuration**:

```python
from pyiceberg.catalog import load_catalog

# Różne katalogi dla różnych środowisk
catalogs = {
    'dev': load_catalog("dev",
        type="sql",
        uri="sqlite:///dev_catalog.db",
        warehouse="file:///tmp/dev_warehouse"
    ),
    
    'staging': load_catalog("staging", 
        type="glue",
        warehouse="s3://staging-data-lake/"
    ),
    
    'prod': load_catalog("prod",
        type="glue", 
        warehouse="s3://prod-data-lake/"
    )
}

def get_catalog(environment):
    """Pobierz katalog dla środowiska"""
    if environment not in catalogs:
        raise ValueError(f"Unknown environment: {environment}")
    return catalogs[environment]

# Użycie
dev_catalog = get_catalog('dev')
prod_catalog = get_catalog('prod')

# Porównaj tabele między środowiskami
def compare_environments(table_name):
    """Porównaj tabelę między środowiskami"""
    for env_name, catalog in catalogs.items():
        try:
            table = catalog.load_table(table_name)
            snapshot_count = len(table.metadata.snapshots)
            schema_version = table.metadata.current_schema_id
            
            print(f"{env_name}: {snapshot_count} snapshots, schema v{schema_version}")
        except Exception as e:
            print(f"{env_name}: Table not found - {e}")

compare_environments("analytics.users")
```

### 2. **Cross-catalog operations**:

```python
import pyarrow as pa

def promote_table_dev_to_staging(table_name):
    """Promuj tabelę z dev do staging"""
    
    # Pobierz dane z dev
    dev_table = catalogs['dev'].load_table(table_name)
    
    # Scan wszystkich danych
    data_batches = []
    for batch in dev_table.scan().to_arrow():
        data_batches.append(batch)
    
    if not data_batches:
        print(f"No data in dev table {table_name}")
        return
    
    # Połącz wszystkie batches
    combined_table = pa.concat_tables(data_batches)
    
    # Sprawdź czy tabela istnieje w staging
    try:
        staging_table = catalogs['staging'].load_table(table_name)
        print(f"Appending to existing staging table {table_name}")
        staging_table.append(combined_table)
    except:
        # Utwórz nową tabelę w staging
        print(f"Creating new staging table {table_name}")
        namespace, table_name_only = table_name.split('.', 1)
        
        # Utwórz namespace jeśli nie istnieje
        try:
            catalogs['staging'].create_namespace(namespace)
        except:
            pass  # Namespace już istnieje
        
        # Utwórz tabelę
        staging_table = catalogs['staging'].create_table(
            identifier=table_name,
            schema=dev_table.schema()
        )
        staging_table.append(combined_table)
    
    print(f"Successfully promoted {table_name} from dev to staging")

# Przykład użycia
if 'analytics.test_table' in [t for namespace in catalogs['dev'].list_namespaces() 
                              for t in catalogs['dev'].list_tables(namespace)]:
    promote_table_dev_to_staging('analytics.test_table')
```

## Catalog Performance i Best Practices

### 1. **Catalog caching**:

```python
from functools import lru_cache
import time

class CachedCatalog:
    """Wrapper z cache dla catalog operations"""
    
    def __init__(self, catalog):
        self.catalog = catalog
        self._table_cache = {}
        self._cache_ttl = 300  # 5 minut
    
    @lru_cache(maxsize=100)
    def list_namespaces_cached(self):
        """Cache namespace list"""
        return self.catalog.list_namespaces()
    
    @lru_cache(maxsize=1000)
    def list_tables_cached(self, namespace):
        """Cache table list per namespace"""
        return self.catalog.list_tables(namespace)
    
    def load_table_cached(self, table_identifier):
        """Cache table metadata"""
        cache_key = table_identifier
        current_time = time.time()
        
        if (cache_key in self._table_cache and 
            current_time - self._table_cache[cache_key]['timestamp'] < self._cache_ttl):
            return self._table_cache[cache_key]['table']
        
        # Load from catalog
        table = self.catalog.load_table(table_identifier)
        
        # Cache result
        self._table_cache[cache_key] = {
            'table': table,
            'timestamp': current_time
        }
        
        return table
    
    def clear_cache(self):
        """Wyczyść cache"""
        self.list_namespaces_cached.cache_clear()
        self.list_tables_cached.cache_clear()
        self._table_cache.clear()

# Użycie
cached_catalog = CachedCatalog(catalog)

# Te operacje będą cache'owane
namespaces = cached_catalog.list_namespaces_cached()
tables = cached_catalog.list_tables_cached("analytics")
table = cached_catalog.load_table_cached("analytics.users")
```

### 2. **Monitoring catalog health**:

```python
import psutil
import time
from datetime import datetime

def monitor_catalog_performance(catalog, duration_minutes=5):
    """Monitor wydajności katalogu"""
    
    print(f"Monitoring catalog performance for {duration_minutes} minutes...")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    metrics = {
        'list_namespaces_times': [],
        'list_tables_times': [],
        'load_table_times': [],
        'errors': []
    }
    
    while time.time() < end_time:
        try:
            # Test list namespaces
            ns_start = time.time()
            namespaces = catalog.list_namespaces()
            metrics['list_namespaces_times'].append(time.time() - ns_start)
            
            # Test list tables
            if namespaces:
                lt_start = time.time()
                tables = catalog.list_tables(namespaces[0])
                metrics['list_tables_times'].append(time.time() - lt_start)
                
                # Test load table
                if tables:
                    table_id = f"{namespaces[0]}.{tables[0]}"
                    tl_start = time.time()
                    table = catalog.load_table(table_id)
                    metrics['load_table_times'].append(time.time() - tl_start)
            
        except Exception as e:
            metrics['errors'].append({
                'time': datetime.now(),
                'error': str(e)
            })
        
        time.sleep(10)  # Test co 10 sekund
    
    # Raport
    print("\n=== CATALOG PERFORMANCE REPORT ===")
    
    if metrics['list_namespaces_times']:
        avg_ns = sum(metrics['list_namespaces_times']) / len(metrics['list_namespaces_times'])
        print(f"List namespaces - Avg: {avg_ns:.3f}s, Count: {len(metrics['list_namespaces_times'])}")
    
    if metrics['list_tables_times']:
        avg_lt = sum(metrics['list_tables_times']) / len(metrics['list_tables_times'])
        print(f"List tables - Avg: {avg_lt:.3f}s, Count: {len(metrics['list_tables_times'])}")
    
    if metrics['load_table_times']:
        avg_tl = sum(metrics['load_table_times']) / len(metrics['load_table_times'])
        print(f"Load table - Avg: {avg_tl:.3f}s, Count: {len(metrics['load_table_times'])}")
    
    if metrics['errors']:
        print(f"Errors: {len(metrics['errors'])}")
        for error in metrics['errors'][-5:]:  # Show last 5 errors
            print(f"  {error['time']}: {error['error']}")

# Monitoring example (comment out for actual use)
# monitor_catalog_performance(catalog, duration_minutes=1)
```

## Podsumowanie

### ✅ Wybór Catalog według przypadku:

| Use Case | Recommended Catalog | Dlaczego |
|----------|-------------------|----------|
| **AWS Environment** | AWS Glue | Native integration, managed service |
| **On-premise Hadoop** | Hive Metastore | Existing infrastructure |
| **Multi-cloud** | REST Catalog | Vendor neutral, flexible |
| **Development** | SQLite Catalog | Lightweight, local |
| **Enterprise** | REST + Database | Scalable, customizable |

### 🔧 Best Practices:
- ✅ Używaj managed catalog w production (Glue, Confluent)
- ✅ Implementuj caching dla częstych operacji
- ✅ Monitoruj performance catalog operations
- ✅ Backup metadanych regularnie
- ✅ Używaj namespace do organizacji
- ✅ Wersjonuj schema changes
- ✅ Implementuj proper security (authentication/authorization)

**Catalog = Heart of Data Lake Governance** 📋