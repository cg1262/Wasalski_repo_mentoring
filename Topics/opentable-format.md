# OpenTable Format - co to jest?

## Co to jest OpenTable Format?

OpenTable Format to **otwarty standard** dla formatów tabel danych w data lake'ach. Główne implementacje to:
- **Apache Iceberg** 
- **Delta Lake**
- **Apache Hudi**

Te formaty rozwiązują problemy tradycyjnych formatów (jak Parquet) w środowiskach data lake.

## Problemy tradycyjnych formatów

### Ograniczenia Parquet w data lake:
```
Traditional Data Lake Problems:
├── Brak ACID transactions
├── Trudne updates/deletes  
├── Brak schema evolution
├── Problemy z concurrent writes
├── Brak time travel
└── Metadata management issues
```

### Przykład problemów:
```python
# ❌ Problemy z tradycyjnym Parquet
import pandas as pd

# Dane w wielu plikach Parquet
files = [
    'data/year=2023/month=01/part-001.parquet',
    'data/year=2023/month=01/part-002.parquet', 
    'data/year=2023/month=02/part-001.parquet'
]

# Problem 1: Trudne updates
# Aby zaktualizować jeden rekord, musisz:
# 1. Przeczytać cały plik
# 2. Zaktualizować dane
# 3. Przepisać cały plik
df = pd.read_parquet('data/year=2023/month=01/part-001.parquet')
df.loc[df['id'] == 123, 'status'] = 'updated'
df.to_parquet('data/year=2023/month=01/part-001.parquet')  # Cały plik!

# Problem 2: Brak transakcji
# Jeśli update się nie powiedzie w połowie, data lake jest w niespójnym stanie

# Problem 3: Schema evolution
# Dodanie nowej kolumny wymaga przepisania wszystkich plików
```

## Apache Iceberg - rozwiązanie OpenTable

### Architektura Iceberg:
```
Iceberg Table
├── Metadata Files (.json)
│   ├── Table metadata
│   ├── Manifest list  
│   └── Manifests
├── Data Files (.parquet, .orc, .avro)
│   ├── part-00000.parquet
│   ├── part-00001.parquet
│   └── ...
└── Delete Files
    ├── delete-00000.parquet
    └── ...
```

### Kluczowe koncepty:

#### 1. **Metadata Layer**:
```json
// table-metadata.json
{
  "format-version": 2,
  "table-uuid": "9c12d441-03fe-4693-9a96-a0705ddf69c1",
  "location": "s3://my-bucket/warehouse/db/table",
  "last-sequence-number": 34,
  "last-updated-ms": 1602638573590,
  "last-column-id": 3,
  "current-schema-id": 1,
  "schemas": [
    {
      "schema-id": 1,
      "type": "struct",
      "fields": [
        {"id": 1, "name": "id", "required": true, "type": "long"},
        {"id": 2, "name": "data", "required": false, "type": "string"},
        {"id": 3, "name": "category", "required": false, "type": "string"}
      ]
    }
  ],
  "current-snapshot-id": 3055729675574597004,
  "snapshots": [
    {
      "snapshot-id": 3055729675574597004,
      "timestamp-ms": 1555100955770,
      "sequence-number": 34,
      "summary": {"operation": "append", "added-data-files": "4", "added-records": "4444"}
    }
  ]
}
```

#### 2. **Manifest Files**:
```json
// manifest-list.json
{
  "manifests": [
    {
      "manifest-path": "s3://bucket/warehouse/db/table/metadata/snap-001-manifest.avro",
      "manifest-length": 4567,
      "partition-spec-id": 0,
      "added-snapshot-id": 3055729675574597004,
      "added-data-files-count": 2,
      "existing-data-files-count": 0,
      "deleted-data-files-count": 0
    }
  ]
}
```

## Praktyczne przykłady z Apache Iceberg

### 1. **Setup i podstawowe operacje**:

```python
# PyIceberg installation
# pip install pyiceberg[s3,sql]

from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, LongType, TimestampType
import pyarrow as pa

# Katalog Iceberg (może być AWS Glue, Hive, REST API)
catalog = load_catalog("default", 
    type="rest",
    uri="http://localhost:8181"  # REST catalog
)

# Lub lokalny katalog dla testów
catalog = load_catalog("local",
    type="sql", 
    uri="sqlite:///pyiceberg_catalog.db",
    warehouse="file:///tmp/warehouse"
)

# Definiuj schema
schema = Schema(
    NestedField(field_id=1, name="id", field_type=LongType(), required=True),
    NestedField(field_id=2, name="name", field_type=StringType(), required=True),
    NestedField(field_id=3, name="email", field_type=StringType(), required=False),
    NestedField(field_id=4, name="created_at", field_type=TimestampType(), required=True),
    NestedField(field_id=5, name="status", field_type=StringType(), required=True)
)

# Utwórz tabelę
table = catalog.create_table(
    identifier="warehouse.users",
    schema=schema
)

print(f"Created table: {table}")
```

### 2. **Wstawianie i czytanie danych**:

```python
import pyarrow as pa
import pandas as pd
from datetime import datetime

# Przygotuj dane
data = {
    'id': [1, 2, 3, 4, 5],
    'name': ['Jan Kowalski', 'Anna Nowak', 'Piotr Wiśniewski', 'Maria Kowalczyk', 'Tomasz Zieliński'],
    'email': ['jan@example.com', 'anna@example.com', 'piotr@example.com', 'maria@example.com', 'tomasz@example.com'],
    'created_at': [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3), datetime(2024, 1, 4), datetime(2024, 1, 5)],
    'status': ['active', 'active', 'inactive', 'active', 'pending']
}

df = pd.DataFrame(data)
arrow_table = pa.Table.from_pandas(df)

# Wstaw dane (append)
table.append(arrow_table)

print("Data appended successfully")

# Czytanie danych
table = catalog.load_table("warehouse.users")

# Scan całej tabeli
for batch in table.scan().to_arrow():
    print("Batch:")
    print(batch.to_pandas())

# Filtrowanie podczas skanowania
filtered_scan = table.scan(
    row_filter="status == 'active'"
).to_arrow()

print("\nFiltered results (active users):")
for batch in filtered_scan:
    print(batch.to_pandas())
```

### 3. **Schema Evolution**:

```python
from pyiceberg.types import BooleanType

# Pokaż aktualną schema
print("Current schema:")
for field in table.schema().fields:
    print(f"  {field.field_id}: {field.name} ({field.field_type})")

# Dodaj nową kolumnę
table = table.update_schema().add_column(
    path="is_premium", 
    field_type=BooleanType(),
    required=False
).commit()

print("\nSchema after adding is_premium column:")
for field in table.schema().fields:
    print(f"  {field.field_id}: {field.name} ({field.field_type})")

# Dodaj dane z nową kolumną
new_data = {
    'id': [6, 7],
    'name': ['Kasia Nowak', 'Marcin Kowal'],
    'email': ['kasia@example.com', 'marcin@example.com'],
    'created_at': [datetime(2024, 1, 6), datetime(2024, 1, 7)],
    'status': ['active', 'active'],
    'is_premium': [True, False]  # Nowa kolumna
}

new_df = pd.DataFrame(new_data)
new_arrow_table = pa.Table.from_pandas(new_df)

table.append(new_arrow_table)

# Stare rekordy będą miały NULL w nowej kolumnie
print("\nData with new column:")
for batch in table.scan().to_arrow():
    print(batch.to_pandas())
```

### 4. **Time Travel**:

```python
# Pokaż historię snapshots
snapshots = table.metadata.snapshots
print("Table snapshots:")
for snapshot in snapshots:
    print(f"  Snapshot {snapshot.snapshot_id}: {snapshot.timestamp_ms}")

# Czytaj dane z konkretnego snapshot
if len(snapshots) > 1:
    previous_snapshot = snapshots[-2]  # Przedostatni snapshot
    
    # Time travel do poprzedniej wersji
    historical_table = table.scan(
        snapshot_id=previous_snapshot.snapshot_id
    ).to_arrow()
    
    print(f"\nData from snapshot {previous_snapshot.snapshot_id}:")
    for batch in historical_table:
        print(batch.to_pandas())

# Time travel po timestamp
import time
from datetime import datetime, timedelta

# Dane sprzed godziny (teoretycznie)
hour_ago = datetime.now() - timedelta(hours=1)
timestamp_ms = int(hour_ago.timestamp() * 1000)

try:
    historical_scan = table.scan(
        as_of_timestamp=timestamp_ms
    ).to_arrow()
    
    print(f"\nData as of {hour_ago}:")
    for batch in historical_scan:
        print(batch.to_pandas())
except Exception as e:
    print(f"No data available for timestamp {hour_ago}: {e}")
```

## Zaawansowane funkcje

### 1. **Partycjonowanie**:

```python
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import DayTransform, BucketTransform

# Utwórz tabelę z partycjonowaniem
partitioned_schema = Schema(
    NestedField(field_id=1, name="id", field_type=LongType(), required=True),
    NestedField(field_id=2, name="user_id", field_type=LongType(), required=True),
    NestedField(field_id=3, name="event_type", field_type=StringType(), required=True),
    NestedField(field_id=4, name="timestamp", field_type=TimestampType(), required=True),
    NestedField(field_id=5, name="data", field_type=StringType(), required=False)
)

# Partition spec
partition_spec = PartitionSpec(
    # Partycjonuj po dniach (timestamp -> day)
    PartitionField(
        source_id=4,  # timestamp field
        field_id=1000,
        transform=DayTransform(),
        name="day"
    ),
    # Bucket by user_id
    PartitionField(
        source_id=2,  # user_id field  
        field_id=1001,
        transform=BucketTransform(num_buckets=16),
        name="user_bucket"
    )
)

# Utwórz partycjonowaną tabelę
events_table = catalog.create_table(
    identifier="warehouse.events",
    schema=partitioned_schema,
    partition_spec=partition_spec
)

# Dodaj przykładowe dane
import random
from datetime import datetime, timedelta

events_data = []
base_time = datetime(2024, 1, 1)

for i in range(1000):
    events_data.append({
        'id': i,
        'user_id': random.randint(1, 100),
        'event_type': random.choice(['click', 'view', 'purchase']),
        'timestamp': base_time + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
        'data': f'event_data_{i}'
    })

events_df = pd.DataFrame(events_data)
events_arrow = pa.Table.from_pandas(events_df)

events_table.append(events_arrow)

# Query z partition pruning
filtered_events = events_table.scan(
    row_filter="event_type == 'purchase'"
).to_arrow()

print("Purchase events:")
for batch in filtered_events:
    df = batch.to_pandas()
    print(f"Found {len(df)} purchase events")
    print(df.head())
```

### 2. **Maintenance operations**:

```python
# Pokaż statystyki tabeli
print("Table statistics:")
print(f"  Location: {table.metadata.location}")
print(f"  Schema ID: {table.metadata.current_schema_id}")
print(f"  Snapshot ID: {table.metadata.current_snapshot_id}")

# Pokaż pliki danych
manifests = table.inspect.files()
print(f"\nData files ({len(manifests)}):")
for manifest in manifests[:5]:  # Pokaż pierwsze 5
    print(f"  {manifest.file_path} ({manifest.file_size_in_bytes} bytes)")

# Expire old snapshots (cleanup)
# W praktyce robiłbyś to ostrożnie z odpowiednim retention period
if len(table.metadata.snapshots) > 2:
    old_snapshots = table.metadata.snapshots[:-2]  # Zostaw 2 najnowsze
    
    print(f"\nWould expire {len(old_snapshots)} old snapshots:")
    for snapshot in old_snapshots:
        print(f"  Snapshot {snapshot.snapshot_id} from {snapshot.timestamp_ms}")

# Note: Actual expiration would be:
# table.expire_snapshots(expire_older_than=datetime.now() - timedelta(days=7))
```

## Porównanie OpenTable formatów

### Iceberg vs Delta Lake vs Hudi:

| Feature | Apache Iceberg | Delta Lake | Apache Hudi |
|---------|----------------|------------|-------------|
| **Vendor** | Apache | Databricks | Apache |
| **License** | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| **Engine Support** | Spark, Flink, Trino | Spark primarily | Spark, Flink |
| **Schema Evolution** | ✅ Full | ✅ Full | ✅ Partial |
| **Time Travel** | ✅ Snapshot-based | ✅ Version-based | ✅ Timeline-based |
| **ACID** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Upserts** | ✅ Yes | ✅ Yes | ✅ Native |
| **Incremental Processing** | ✅ Yes | ✅ Yes | ✅ Native |
| **Partition Evolution** | ✅ Hidden partitioning | ❌ Limited | ✅ Yes |

### Wybór formatu:

```python
def choose_open_table_format(requirements):
    """
    Pomoc w wyborze OpenTable formatu
    """
    
    if requirements.get('primary_engine') == 'databricks':
        return "Delta Lake - Native integration"
    
    if requirements.get('multi_engine') and requirements.get('vendor_neutral'):
        return "Apache Iceberg - Best multi-engine support"
    
    if requirements.get('heavy_upserts') and requirements.get('streaming'):
        return "Apache Hudi - Optimized for updates"
    
    if requirements.get('partition_flexibility'):
        return "Apache Iceberg - Hidden partitioning"
    
    return "Evaluate based on specific needs"

# Przykłady
print("Multi-engine environment:", 
      choose_open_table_format({'multi_engine': True, 'vendor_neutral': True}))
print("Databricks environment:", 
      choose_open_table_format({'primary_engine': 'databricks'}))
print("Heavy upsert workload:", 
      choose_open_table_format({'heavy_upserts': True, 'streaming': True}))
```

## Korzyści OpenTable Format

### 1. **ACID Transactions**:
```python
# Transakcyjne operacje
try:
    # Begin transaction (implicit)
    table.append(new_data_batch_1)
    table.append(new_data_batch_2)
    # Commit transaction (implicit)
    print("Transaction committed successfully")
except Exception as e:
    # Automatic rollback
    print(f"Transaction failed: {e}")
```

### 2. **Concurrent Access**:
```python
# Multiple writers can work simultaneously
# Each creates new snapshot
# No locking required
# Readers see consistent view
```

### 3. **Performance Benefits**:
```python
# Partition pruning
scan = table.scan(
    row_filter="date >= '2024-01-01' AND date < '2024-02-01'"
)  # Only reads relevant partitions

# Projection pushdown  
scan = table.scan(
    selected_fields=["id", "name", "status"]
)  # Only reads needed columns

# Predicate pushdown
scan = table.scan(
    row_filter="status == 'active'"
)  # Filtering happens at storage level
```

## Podsumowanie

### ✅ Używaj OpenTable Format gdy:
- Potrzebujesz ACID transactions w data lake
- Wymagana schema evolution
- Concurrent read/write access
- Time travel capabilities
- Complex update/delete operations
- Multi-engine compatibility

### ❌ Tradycyjny Parquet gdy:
- Proste append-only workloads  
- Brak requirements na ACID
- Minimal metadata overhead
- Legacy system compatibility

**OpenTable Format = ACID + Analytics in Data Lake** 🏗️