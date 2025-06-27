# Formaty danych - Parquet, Delta, JSON - co do czego najlepsze?

## Przegląd formatów danych

### Klasyfikacja formatów:
- **Tekstowe**: JSON, CSV, XML
- **Binarne**: Parquet, Avro, ORC
- **Hybrydowe**: Delta Lake, Iceberg
- **Specjalistyczne**: Protocol Buffers, MessagePack

## JSON - JavaScript Object Notation

### Charakterystyka:
- 📝 **Tekstowy** - human-readable
- 🌐 **Uniwersalny** - obsługiwany wszędzie
- 🚀 **Szybki parsing** - natywne wsparcie w językach
- 📦 **Schemaless** - elastyczna struktura

### Przykład JSON:
```json
{
  "user": {
    "id": 12345,
    "name": "Jan Kowalski",
    "email": "jan@example.com",
    "active": true,
    "last_login": "2024-01-15T10:30:00Z",
    "preferences": {
      "theme": "dark",
      "language": "pl",
      "notifications": ["email", "push"]
    },
    "orders": [
      {
        "id": "ORD-001",
        "amount": 299.99,
        "items": ["laptop", "mouse"],
        "date": "2024-01-10"
      }
    ]
  }
}
```

### ✅ JSON najlepszy do:
- **REST APIs** - standard web
- **Konfiguracja** - łatwa do czytania
- **NoSQL databases** - MongoDB, CouchDB
- **Real-time data** - WebSocket, messaging
- **Frontend-backend** - komunikacja

### ❌ JSON unikaj gdy:
- **Duże objętości** - brak kompresji
- **Analityka** - brak kolumnowej struktury
- **Typy danych** - wszystko to string/number
- **Schema validation** - brak built-in validation

### Praktyczny przykład - API Response:
```json
{
  "status": "success",
  "data": {
    "products": [
      {
        "id": 1,
        "name": "Laptop Dell XPS",
        "price": 3500.00,
        "currency": "PLN",
        "available": true,
        "categories": ["electronics", "computers"],
        "specifications": {
          "cpu": "Intel i7",
          "ram": "16GB",
          "storage": "512GB SSD"
        }
      }
    ]
  },
  "pagination": {
    "page": 1,
    "total_pages": 10,
    "total_items": 100
  }
}
```

## Parquet - kolumnowy format dla analityki

### Charakterystyka:
- 🏗️ **Kolumnowy** - dane przechowywane kolumnami
- 📊 **Analityczny** - zoptymalizowany pod zapytania
- 🗜️ **Kompresja** - bardzo dobra kompresja
- ⚡ **Wydajność** - szybkie filtrowanie i agregacje

### Struktura Parquet:
```
Parquet File
├── Metadata
├── Row Group 1
│   ├── Column A (compressed)
│   ├── Column B (compressed)
│   └── Column C (compressed)
├── Row Group 2
│   ├── Column A (compressed)
│   ├── Column B (compressed)
│   └── Column C (compressed)
└── Footer
```

### Przykład Python - zapisywanie do Parquet:
```python
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Przykładowe dane
data = {
    'user_id': [1, 2, 3, 4, 5],
    'name': ['Jan', 'Anna', 'Piotr', 'Maria', 'Tomek'],
    'age': [25, 30, 35, 28, 42],
    'salary': [5000.0, 6500.0, 7200.0, 5800.0, 8900.0],
    'department': ['IT', 'HR', 'Finance', 'IT', 'Finance'],
    'date_hired': pd.to_datetime(['2020-01-15', '2019-03-20', '2018-07-10', '2021-11-05', '2017-09-30'])
}

df = pd.DataFrame(data)

# Zapisz jako Parquet
df.to_parquet('employees.parquet', 
              compression='snappy',  # gzip, lz4, brotli
              index=False)

# Czytanie Parquet
df_read = pd.read_parquet('employees.parquet')

# Filtrowanie podczas czytania (predicate pushdown)
df_it = pd.read_parquet('employees.parquet', 
                        filters=[('department', '==', 'IT')])

# Czytanie tylko wybranych kolumn
df_subset = pd.read_parquet('employees.parquet', 
                           columns=['name', 'salary'])
```

### Parquet z partycjonowaniem:
```python
# Zapisz z partycjonowaniem po departamentach
df.to_parquet('employees_partitioned/', 
              partition_cols=['department'],
              compression='snappy')

# Struktura plików:
# employees_partitioned/
# ├── department=Finance/
# │   └── part-0.parquet
# ├── department=HR/
# │   └── part-0.parquet
# └── department=IT/
#     └── part-0.parquet

# Czytanie z automatycznym filtrowaniem
df_finance = pd.read_parquet('employees_partitioned/', 
                            filters=[('department', '==', 'Finance')])
```

### ✅ Parquet najlepszy do:
- **Data analytics** - OLAP queries
- **Data warehouses** - Snowflake, BigQuery
- **ETL pipelines** - batch processing
- **Data science** - ML datasets
- **Archiwizacja** - długoterminowe przechowywanie

### ❌ Parquet unikaj gdy:
- **Real-time updates** - immutable format
- **Małe pliki** - overhead metadata
- **Transactional workloads** - OLTP
- **Streaming** - nie nadaje się do stream processing

## Delta Lake - wersjonowana tabela danych

### Charakterystyka:
- 🔄 **ACID transactions** - konsystentność danych
- 📈 **Time travel** - dostęp do historii
- 🔀 **Schema evolution** - zmiany struktury
- ⚡ **Upserts/Deletes** - modyfikacja danych
- 📊 **Parquet under the hood** - wydajność kolumnowa

### Struktura Delta Table:
```
delta_table/
├── _delta_log/
│   ├── 00000000000000000000.json    # Transaction log
│   ├── 00000000000000000001.json
│   └── _last_checkpoint
├── part-00000-123.snappy.parquet    # Data files
├── part-00001-456.snappy.parquet
└── part-00002-789.snappy.parquet
```

### Przykład Python - Delta Lake:
```python
from delta import *
from pyspark.sql import SparkSession

# Konfiguracja Spark z Delta
builder = SparkSession.builder \
    .appName("DeltaExample") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Przykładowe dane
data = [
    (1, "Jan Kowalski", "IT", 5000, "2024-01-15"),
    (2, "Anna Nowak", "HR", 5500, "2024-01-15"),
    (3, "Piotr Wiśniewski", "Finance", 6000, "2024-01-15")
]

columns = ["id", "name", "department", "salary", "date"]
df = spark.createDataFrame(data, columns)

# Zapisz jako Delta Table
df.write.format("delta").save("/path/to/delta-table")

# Lub z użyciem SQL
df.write.format("delta").saveAsTable("employees")

# Czytanie Delta Table
delta_df = spark.read.format("delta").load("/path/to/delta-table")

# Time Travel - dostęp do poprzedniej wersji
df_version_0 = spark.read.format("delta").option("versionAsOf", 0).load("/path/to/delta-table")
df_timestamp = spark.read.format("delta").option("timestampAsOf", "2024-01-15").load("/path/to/delta-table")

# Historia zmian
deltaTable = DeltaTable.forPath(spark, "/path/to/delta-table")
deltaTable.history().show()

# Upsert (merge)
new_data = [
    (1, "Jan Kowalski", "IT", 5200, "2024-02-01"),  # Update salary
    (4, "Maria Kowalczyk", "Marketing", 4800, "2024-02-01")  # New employee
]

new_df = spark.createDataFrame(new_data, columns)

deltaTable.alias("target") \
  .merge(new_df.alias("source"), "target.id = source.id") \
  .whenMatchedUpdateAll() \
  .whenNotMatchedInsertAll() \
  .execute()

# Delete
deltaTable.delete("department = 'HR'")

# Schema evolution
new_schema_data = [
    (5, "Tomek Nowak", "IT", 5300, "2024-02-01", "tomek@company.com")  # Nowa kolumna email
]

new_schema_df = spark.createDataFrame(new_schema_data, ["id", "name", "department", "salary", "date", "email"])

new_schema_df.write \
  .format("delta") \
  .mode("append") \
  .option("mergeSchema", "true") \
  .save("/path/to/delta-table")
```

### Delta Lake SQL:
```sql
-- Tworzenie Delta Table
CREATE TABLE employees (
  id INT,
  name STRING,
  department STRING,
  salary DOUBLE,
  hire_date DATE
) USING DELTA

-- Insert
INSERT INTO employees VALUES 
(1, 'Jan Kowalski', 'IT', 5000, '2024-01-15'),
(2, 'Anna Nowak', 'HR', 5500, '2024-01-15')

-- Time Travel
SELECT * FROM employees VERSION AS OF 1
SELECT * FROM employees TIMESTAMP AS OF '2024-01-15'

-- Merge (Upsert)
MERGE INTO employees target
USING updates source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *

-- Optimize (compaction)
OPTIMIZE employees

-- Vacuum (cleanup old files)
VACUUM employees RETAIN 168 HOURS
```

### ✅ Delta Lake najlepszy do:
- **Data lakes** - structured + unstructured
- **ETL pipelines** - reliable data processing
- **Data versioning** - audit trails
- **ML datasets** - reproducible experiments
- **Real-time + batch** - lambda architecture

### ❌ Delta Lake unikaj gdy:
- **Simple use cases** - overkill for basic needs
- **Non-Spark environments** - requires Spark
- **Storage constraints** - więcej metadanych
- **Legacy systems** - może wymagać zmian

## Porównanie wydajności

### Test na 10M rekordów:

```python
import pandas as pd
import time
import json

# Przykładowe dane
data = {
    'id': range(10_000_000),
    'name': [f'User_{i}' for i in range(10_000_000)],
    'value': [i * 1.5 for i in range(10_000_000)],
    'category': ['A', 'B', 'C'] * (10_000_000 // 3 + 1)
}

df = pd.DataFrame(data)

# Test zapisywania
formats = {}

# JSON
start = time.time()
df.to_json('test.json', orient='records')
formats['JSON write'] = time.time() - start

# Parquet
start = time.time()
df.to_parquet('test.parquet', compression='snappy')
formats['Parquet write'] = time.time() - start

# CSV
start = time.time()
df.to_csv('test.csv', index=False)
formats['CSV write'] = time.time() - start

# Test czytania
start = time.time()
pd.read_json('test.json')
formats['JSON read'] = time.time() - start

start = time.time()
pd.read_parquet('test.parquet')
formats['Parquet read'] = time.time() - start

start = time.time()
pd.read_csv('test.csv')
formats['CSV read'] = time.time() - start

# Rozmiary plików
import os
formats['JSON size MB'] = os.path.getsize('test.json') / 1024 / 1024
formats['Parquet size MB'] = os.path.getsize('test.parquet') / 1024 / 1024
formats['CSV size MB'] = os.path.getsize('test.csv') / 1024 / 1024

for format_name, value in formats.items():
    print(f"{format_name}: {value:.2f}")
```

### Typowe wyniki:
| Format | Write Time | Read Time | File Size | Compression |
|--------|------------|-----------|-----------|-------------|
| **JSON** | 15s | 12s | 800MB | Brak |
| **Parquet** | 8s | 2s | 180MB | Excellent |
| **CSV** | 10s | 8s | 400MB | Brak |
| **Delta** | 10s | 3s | 190MB | Excellent + metadata |

## Przypadki użycia - matryca decyzyjna

### Wybór formatu według scenariusza:

#### 🌐 **Web Applications**:
```json
// Użyj JSON
{
  "user_profile": {...},
  "real_time_data": {...},
  "api_responses": {...}
}
```

#### 📊 **Data Analytics**:
```python
# Użyj Parquet
df.groupby('department').agg({
    'salary': ['mean', 'count'],
    'age': 'mean'
}).to_parquet('analytics_result.parquet')
```

#### 🔄 **Data Lake Architecture**:
```python
# Użyj Delta Lake
from delta.tables import DeltaTable

# Bronze layer (raw data) - JSON/CSV → Delta
raw_data.write.format("delta").save("/data/bronze/transactions")

# Silver layer (cleaned) - Delta → Delta
cleaned_data.write.format("delta").save("/data/silver/transactions")

# Gold layer (aggregated) - Delta → Delta/Parquet
aggregated_data.write.format("delta").save("/data/gold/daily_summary")
```

#### ⚡ **Real-time Processing**:
```python
# JSON dla messaging
{
  "event_type": "user_click",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": 12345,
  "properties": {...}
}
```

## Najlepsze praktyki

### 1. **Wybór formatu**:
```python
def choose_format(use_case):
    if use_case == "api_communication":
        return "JSON"
    elif use_case == "analytics_readonly":
        return "Parquet"
    elif use_case == "data_lake_updates":
        return "Delta Lake"
    elif use_case == "streaming_events":
        return "JSON/Avro"
    elif use_case == "ml_training":
        return "Parquet/Delta"
```

### 2. **Optymalizacja Parquet**:
```python
# Optymalne rozmiary plików (128MB - 1GB)
df.to_parquet('data.parquet', 
              compression='snappy',  # Dobra balance speed/size
              row_group_size=50000)  # Optimize for query patterns

# Partycjonowanie
df.to_parquet('partitioned_data/', 
              partition_cols=['year', 'month'])
```

### 3. **Delta Lake maintenance**:
```python
# Regularne optymalizacje
OPTIMIZE employees ZORDER BY (department, salary)

# Cleanup starych plików
VACUUM employees RETAIN 168 HOURS

# Monitoring
DESCRIBE HISTORY employees
```

## Migration strategies

### JSON → Parquet:
```python
import pandas as pd
import glob

# Batch convert JSON files
json_files = glob.glob("data/*.json")

for json_file in json_files:
    df = pd.read_json(json_file)
    parquet_file = json_file.replace('.json', '.parquet')
    df.to_parquet(parquet_file, compression='snappy')
    print(f"Converted {json_file} → {parquet_file}")
```

### Parquet → Delta:
```python
# Convert existing Parquet to Delta
parquet_df = spark.read.parquet("/path/to/parquet/")
parquet_df.write.format("delta").save("/path/to/delta/")

# Or create external table
spark.sql("""
CREATE TABLE parquet_as_delta
USING DELTA
LOCATION '/path/to/delta/'
AS SELECT * FROM parquet.`/path/to/parquet/`
""")
```

## Podsumowanie

### 🎯 **Quick Decision Guide**:

| Scenariusz | Format | Dlaczego |
|------------|--------|----------|
| **REST API** | JSON | Standard web, szybki parsing |
| **Data Warehouse** | Parquet | Kompresja, kolumnowy dostęp |
| **ML Pipeline** | Parquet/Delta | Wydajność + wersjonowanie |
| **Event Streaming** | JSON/Avro | Schema registry, real-time |
| **Data Lake** | Delta Lake | ACID + analytics + updates |
| **Configuration** | JSON/YAML | Human readable |
| **Archival** | Parquet | Najlepsza kompresja |
| **Transactional** | Delta Lake | ACID properties |

### 💡 **Złote zasady**:
1. **JSON** - komunikacja i konfiguracja
2. **Parquet** - analityka read-only
3. **Delta** - gdy potrzebujesz updates + analytics
4. **Zawsze testuj** na swoich danych!

**Right format = Right performance** 🚀