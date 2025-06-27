# Schema Evolution - ewolucja schematu danych

## Co to jest Schema Evolution?

Schema Evolution to **proces zmiany struktury danych** w sposób kontrolowany i kompatybilny. Pozwala na:
- Dodawanie nowych kolumn
- Usuwanie starych kolumn  
- Zmianę typów danych
- Reorganizację struktury
- Utrzymanie kompatybilności z istniejącymi danymi

### Problemy bez Schema Evolution:
```
Traditional Data Problems:
├── Breaking changes przy aktualizacji
├── Konieczność migracji wszystkich danych
├── Downtime aplikacji
├── Strata starych danych
├── Wersjonowanie "big bang"
└── Brak kompatybilności wstecznej
```

## Typy Schema Evolution

### 1. **Forward Compatibility** (Kompatybilność w przód):
```python
# Stara aplikacja może czytać nowe dane
# Nowe pole jest ignorowane przez starą aplikację

# Schema v1
{
    "name": "John Doe",
    "age": 30
}

# Schema v2 - dodano nowe pole
{
    "name": "John Doe", 
    "age": 30,
    "email": "john@example.com"  # Nowe pole - ignorowane przez v1
}
```

### 2. **Backward Compatibility** (Kompatybilność wstecz):
```python
# Nowa aplikacja może czytać stare dane

# Schema v1
{
    "name": "John Doe",
    "age": 30,
    "address": "123 Main St"
}

# Schema v2 - pole "address" jest opcjonalne/ma default
{
    "name": "John Doe",
    "age": 30,
    "email": "john@example.com",
    "address": "123 Main St"  # Może być None w nowych rekordach
}
```

### 3. **Full Compatibility**:
```python
# Zarówno forward jak i backward compatibility
# Najsilniejsza forma kompatybilności
```

## Schema Evolution w różnych systemach

### 1. **Apache Avro - native schema evolution**

#### Setup Avro:
```python
import avro.schema
import avro.io
import io
import json

# Schema v1
schema_v1_json = {
    "type": "record",
    "name": "User", 
    "fields": [
        {"name": "id", "type": "long"},
        {"name": "name", "type": "string"},
        {"name": "age", "type": "int"}
    ]
}

# Schema v2 - dodano email z default value
schema_v2_json = {
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "id", "type": "long"},
        {"name": "name", "type": "string"}, 
        {"name": "age", "type": "int"},
        {"name": "email", "type": "string", "default": ""}  # Nowe pole z default
    ]
}

# Schema v3 - usunięto age, dodano timestamp
schema_v3_json = {
    "type": "record", 
    "name": "User",
    "fields": [
        {"name": "id", "type": "long"},
        {"name": "name", "type": "string"},
        {"name": "email", "type": "string", "default": ""},
        {"name": "created_at", "type": "long", "default": 0}  # Timestamp
    ]
}

schema_v1 = avro.schema.parse(json.dumps(schema_v1_json))
schema_v2 = avro.schema.parse(json.dumps(schema_v2_json))
schema_v3 = avro.schema.parse(json.dumps(schema_v3_json))

def serialize_data(data, schema):
    """Serializuj dane z daną schema"""
    writer = avro.io.DatumWriter(schema)
    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    writer.write(data, encoder)
    return bytes_writer.getvalue()

def deserialize_data(binary_data, writer_schema, reader_schema):
    """Deserializuj dane z możliwością schema evolution"""
    bytes_reader = io.BytesIO(binary_data)
    decoder = avro.io.BinaryDecoder(bytes_reader)
    reader = avro.io.DatumReader(writer_schema, reader_schema)
    return reader.read(decoder)

# Test schema evolution
user_data_v1 = {
    "id": 1,
    "name": "John Doe", 
    "age": 30
}

# Serializuj z schema v1
binary_data = serialize_data(user_data_v1, schema_v1)
print(f"Serialized data size: {len(binary_data)} bytes")

# Deserializuj z schema v2 (dodano email)
user_v2 = deserialize_data(binary_data, schema_v1, schema_v2)
print(f"V1 data read with V2 schema: {user_v2}")
# Output: {'id': 1, 'name': 'John Doe', 'age': 30, 'email': ''}

# Deserializuj z schema v3 (usunięto age, dodano timestamp)
user_v3 = deserialize_data(binary_data, schema_v1, schema_v3)
print(f"V1 data read with V3 schema: {user_v3}")
# Output: {'id': 1, 'name': 'John Doe', 'email': '', 'created_at': 0}
```

#### Avro Schema Registry:
```python
from confluent_kafka import Producer
from confluent_kafka.avro import AvroProducer, AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

# Konfiguracja Schema Registry
avro_producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'schema.registry.url': 'http://localhost:8081'
}

# Producer z automatycznym schema registry
avro_producer = AvroProducer(
    avro_producer_config,
    default_value_schema=schema_v1
)

# Wyślij dane
user_data = {"id": 1, "name": "John", "age": 25}
avro_producer.produce(topic='users', value=user_data)
avro_producer.flush()

# Consumer może używać nowszej schema
avro_consumer = AvroConsumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'test-group',
    'schema.registry.url': 'http://localhost:8081'
})

avro_consumer.subscribe(['users'])

# Automatyczna schema evolution podczas consumption
msg = avro_consumer.poll(10)
if msg:
    user = msg.value()  # Automatycznie ewoluuje schema
    print(f"Consumed: {user}")
```

### 2. **Delta Lake Schema Evolution**

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType
from delta import *

# Setup Spark z Delta
builder = SparkSession.builder \
    .appName("SchemaEvolution") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtensions") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Schema v1
schema_v1 = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])

# Początkowe dane
data_v1 = [
    (1, "John Doe", 30),
    (2, "Jane Smith", 25),
    (3, "Bob Johnson", 35)
]

df_v1 = spark.createDataFrame(data_v1, schema_v1)

# Zapisz jako Delta table
delta_path = "/tmp/delta_evolution_test"
df_v1.write.format("delta").save(delta_path)

print("=== Original Data (Schema v1) ===")
spark.read.format("delta").load(delta_path).show()

# Schema Evolution - dodaj nową kolumnę
data_v2_new_column = [
    (4, "Alice Brown", 28, "alice@example.com"),  # Nowa kolumna email
    (5, "Charlie Wilson", 42, "charlie@example.com")
]

# Schema v2
schema_v2 = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True), 
    StructField("age", IntegerType(), True),
    StructField("email", StringType(), True)  # Nowa kolumna
])

df_v2 = spark.createDataFrame(data_v2_new_column, schema_v2)

# Append z automatyczną schema evolution
df_v2.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save(delta_path)

print("=== After Adding Email Column (Schema v2) ===")
delta_df = spark.read.format("delta").load(delta_path)
delta_df.show()
delta_df.printSchema()

# Schema Evolution - zmień typ kolumny (trzeba być ostrożnym!)
# Dodaj nową kolumnę z innym typem
data_v3 = [
    (6, "David Lee", 33, "david@example.com", True),  # Nowa kolumna: is_premium
]

schema_v3 = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True), 
    StructField("email", StringType(), True),
    StructField("is_premium", BooleanType(), True)  # Nowa kolumna boolean
])

df_v3 = spark.createDataFrame(data_v3, schema_v3)

df_v3.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save(delta_path)

print("=== After Adding is_premium Column (Schema v3) ===") 
final_df = spark.read.format("delta").load(delta_path)
final_df.show()
final_df.printSchema()

# Historia schema evolution
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, delta_path)
history = delta_table.history()

print("=== Delta Table History ===")
history.select("version", "timestamp", "operation", "operationMetrics").show(truncate=False)
```

#### Delta Lake z SQL:
```sql
-- Sprawdź aktualną schema
DESCRIBE TABLE delta.`/tmp/delta_evolution_test`

-- Dodaj kolumnę 
ALTER TABLE delta.`/tmp/delta_evolution_test` 
ADD COLUMN (phone STRING AFTER email)

-- Zmień properties kolumny
ALTER TABLE delta.`/tmp/delta_evolution_test`
ALTER COLUMN age SET NOT NULL

-- Dodaj comment do kolumny
ALTER TABLE delta.`/tmp/delta_evolution_test`
ALTER COLUMN email COMMENT 'User email address'

-- Historia schema evolution
DESCRIBE HISTORY delta.`/tmp/delta_evolution_test`
```

### 3. **Apache Iceberg Schema Evolution**

```python
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, LongType, BooleanType, TimestampType
import pandas as pd
import pyarrow as pa

# Setup Iceberg catalog
catalog = load_catalog("local",
    type="sql",
    uri="sqlite:///iceberg_evolution.db", 
    warehouse="file:///tmp/iceberg_warehouse"
)

# Początkowa schema
initial_schema = Schema(
    NestedField(field_id=1, name="id", field_type=LongType(), required=True),
    NestedField(field_id=2, name="name", field_type=StringType(), required=True),
    NestedField(field_id=3, name="age", field_type=LongType(), required=False)
)

# Utwórz tabelę
namespace = "evolution_test"
catalog.create_namespace(namespace)

table = catalog.create_table(
    identifier=f"{namespace}.users",
    schema=initial_schema
)

# Dodaj początkowe dane
initial_data = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['John', 'Jane', 'Bob'],
    'age': [30, 25, 35]
})

table.append(pa.Table.from_pandas(initial_data))

print("=== Initial Schema ===")
for field in table.schema().fields:
    print(f"  {field.field_id}: {field.name} ({field.field_type}) {'required' if field.required else 'optional'}")

# Schema Evolution 1: Dodaj email kolumnę
table = table.update_schema() \
    .add_column("email", StringType(), required=False) \
    .commit()

print("\n=== After Adding Email Column ===")
for field in table.schema().fields:
    print(f"  {field.field_id}: {field.name} ({field.field_type}) {'required' if field.required else 'optional'}")

# Dodaj dane z nową kolumną
new_data_with_email = pd.DataFrame({
    'id': [4, 5],
    'name': ['Alice', 'Charlie'], 
    'age': [28, 42],
    'email': ['alice@example.com', 'charlie@example.com']
})

table.append(pa.Table.from_pandas(new_data_with_email))

# Schema Evolution 2: Dodaj timestamp i premium flag
table = table.update_schema() \
    .add_column("created_at", TimestampType(), required=False) \
    .add_column("is_premium", BooleanType(), required=False) \
    .commit()

print("\n=== After Adding Timestamp and Premium Flag ===")
for field in table.schema().fields:
    print(f"  {field.field_id}: {field.name} ({field.field_type}) {'required' if field.required else 'optional'}")

# Dodaj dane z wszystkimi kolumnami
from datetime import datetime

latest_data = pd.DataFrame({
    'id': [6, 7],
    'name': ['David', 'Emma'],
    'age': [33, 29],
    'email': ['david@example.com', 'emma@example.com'],
    'created_at': [datetime.now(), datetime.now()],
    'is_premium': [True, False]
})

table.append(pa.Table.from_pandas(latest_data))

# Odczyt wszystkich danych - automatyczna obsługa NULL values
print("\n=== All Data with Schema Evolution ===")
for batch in table.scan().to_arrow():
    df = batch.to_pandas()
    print(df)

# Schema Evolution 3: Rename kolumny (deprecate old, add new)
table = table.update_schema() \
    .add_column("full_name", StringType(), required=False) \
    .commit()

# W praktyce przepisałbyś dane:
# UPDATE table SET full_name = name WHERE full_name IS NULL

print("\n=== Final Schema ===")
for field in table.schema().fields:
    print(f"  {field.field_id}: {field.name} ({field.field_type}) {'required' if field.required else 'optional'}")
```

### 4. **JSON Schema Evolution**

```python
import jsonschema
import json
from jsonschema import validate, ValidationError

# Schema v1
schema_v1 = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["id", "name"],
    "additionalProperties": False
}

# Schema v2 - dodano email, age optional
schema_v2 = {
    "type": "object", 
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["id", "name"],
    "additionalProperties": False
}

# Schema v3 - dodano nested address
schema_v3 = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "zipcode": {"type": "string"}
            },
            "required": ["city"]
        }
    },
    "required": ["id", "name"],
    "additionalProperties": False
}

def validate_with_evolution(data, schemas):
    """Waliduj dane z różnymi wersjami schema"""
    
    for version, schema in enumerate(schemas, 1):
        try:
            validate(instance=data, schema=schema)
            print(f"✅ Data valid with schema v{version}")
            return True, version
        except ValidationError as e:
            print(f"❌ Data invalid with schema v{version}: {e.message}")
    
    return False, None

# Test danych
test_cases = [
    # Dane v1
    {"id": 1, "name": "John", "age": 30},
    
    # Dane v2  
    {"id": 2, "name": "Jane", "age": 25, "email": "jane@example.com"},
    
    # Dane v3
    {
        "id": 3, 
        "name": "Bob", 
        "email": "bob@example.com",
        "address": {"street": "123 Main St", "city": "Boston", "zipcode": "02101"}
    }
]

schemas = [schema_v1, schema_v2, schema_v3]

for i, data in enumerate(test_cases):
    print(f"\n=== Test Case {i+1}: {data} ===")
    is_valid, version = validate_with_evolution(data, schemas)
```

## Advanced Schema Evolution Patterns

### 1. **Schema Registry Pattern**:

```python
class SchemaRegistry:
    """Centralne zarządzanie schema evolution"""
    
    def __init__(self):
        self.schemas = {}
        self.compatibility_modes = {}
    
    def register_schema(self, subject, schema, version=None):
        """Zarejestruj nową schema"""
        if subject not in self.schemas:
            self.schemas[subject] = {}
        
        if version is None:
            version = len(self.schemas[subject]) + 1
        
        # Sprawdź kompatybilność
        if version > 1:
            self._check_compatibility(subject, schema, version)
        
        self.schemas[subject][version] = schema
        print(f"Registered schema v{version} for subject '{subject}'")
        
        return version
    
    def get_schema(self, subject, version=None):
        """Pobierz schema"""
        if subject not in self.schemas:
            raise ValueError(f"Subject '{subject}' not found")
        
        if version is None:
            version = max(self.schemas[subject].keys())
        
        return self.schemas[subject][version]
    
    def get_latest_version(self, subject):
        """Pobierz najnowszą wersję"""
        if subject not in self.schemas:
            return None
        return max(self.schemas[subject].keys())
    
    def _check_compatibility(self, subject, new_schema, version):
        """Sprawdź kompatybilność z poprzednimi wersjami"""
        mode = self.compatibility_modes.get(subject, "BACKWARD")
        prev_version = version - 1
        
        if prev_version in self.schemas[subject]:
            prev_schema = self.schemas[subject][prev_version]
            
            if mode == "BACKWARD":
                self._check_backward_compatibility(prev_schema, new_schema)
            elif mode == "FORWARD":
                self._check_forward_compatibility(prev_schema, new_schema)
            elif mode == "FULL":
                self._check_backward_compatibility(prev_schema, new_schema)
                self._check_forward_compatibility(prev_schema, new_schema)
    
    def _check_backward_compatibility(self, old_schema, new_schema):
        """Sprawdź kompatybilność wstecz"""
        # Simplified - w rzeczywistości bardziej złożone
        old_fields = set(old_schema.get('required', []))
        new_fields = set(new_schema.get('required', []))
        
        if not old_fields.issubset(new_fields):
            removed_required = old_fields - new_fields
            raise ValueError(f"Backward incompatible: removed required fields {removed_required}")
    
    def _check_forward_compatibility(self, old_schema, new_schema):
        """Sprawdź kompatybilność w przód"""
        # Simplified implementation
        old_props = set(old_schema.get('properties', {}).keys())
        new_props = set(new_schema.get('properties', {}).keys())
        
        added_props = new_props - old_props
        new_required = set(new_schema.get('required', []))
        
        problematic = added_props.intersection(new_required)
        if problematic:
            raise ValueError(f"Forward incompatible: added required fields {problematic}")

# Użycie Schema Registry
registry = SchemaRegistry()

# Zarejestruj schema v1
user_schema_v1 = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"}
    },
    "required": ["id", "name"]
}

registry.register_schema("users", user_schema_v1)

# Kompatybilna ewolucja - dodaj opcjonalne pole
user_schema_v2 = {
    "type": "object", 
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string"}  # Opcjonalne
    },
    "required": ["id", "name"]
}

registry.register_schema("users", user_schema_v2)

# Niekompatybilna ewolucja - dodaj wymagane pole
user_schema_v3_incompatible = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string"}
    },
    "required": ["id", "name", "email"]  # Nowe wymagane pole!
}

try:
    registry.register_schema("users", user_schema_v3_incompatible)
except ValueError as e:
    print(f"Schema registration failed: {e}")

print(f"Latest users schema version: {registry.get_latest_version('users')}")
```

### 2. **Versioned Data Pipeline**:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd

class DataProcessor(ABC):
    """Abstract processor dla różnych wersji schema"""
    
    @abstractmethod
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_output_schema_version(self) -> int:
        pass

class UserProcessorV1(DataProcessor):
    """Processor dla user schema v1"""
    
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        # Procesuj dane zgodnie z schema v1
        result = data.copy()
        result['processed_at'] = pd.Timestamp.now()
        return result
    
    def get_output_schema_version(self) -> int:
        return 1

class UserProcessorV2(DataProcessor):
    """Processor dla user schema v2 z email"""
    
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        
        # Dodaj default email jeśli nie ma
        if 'email' not in result.columns:
            result['email'] = None
        
        # Validacja email
        if 'email' in result.columns:
            result['email_valid'] = result['email'].str.contains('@', na=False)
        
        result['processed_at'] = pd.Timestamp.now()
        return result
    
    def get_output_schema_version(self) -> int:
        return 2

class VersionedPipeline:
    """Pipeline z obsługą schema evolution"""
    
    def __init__(self):
        self.processors = {
            1: UserProcessorV1(),
            2: UserProcessorV2()
        }
        self.schema_detector = SchemaDetector()
    
    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Automatycznie detect schema i procesuj"""
        
        # Wykryj wersję schema
        schema_version = self.schema_detector.detect_version(data)
        print(f"Detected schema version: {schema_version}")
        
        # Wybierz odpowiedni processor
        if schema_version not in self.processors:
            # Użyj najnowszego dostępnego
            schema_version = max(self.processors.keys())
            print(f"Using latest processor version: {schema_version}")
        
        processor = self.processors[schema_version]
        
        # Procesuj dane
        result = processor.process(data)
        
        # Dodaj metadata
        result['source_schema_version'] = schema_version
        result['output_schema_version'] = processor.get_output_schema_version()
        
        return result

class SchemaDetector:
    """Wykrywa wersję schema na podstawie danych"""
    
    def detect_version(self, data: pd.DataFrame) -> int:
        """Wykryj wersję schema z danych"""
        
        required_v1 = {'id', 'name'}
        required_v2 = {'id', 'name', 'email'}
        
        columns = set(data.columns)
        
        if required_v2.issubset(columns):
            return 2
        elif required_v1.issubset(columns):
            return 1
        else:
            raise ValueError(f"Unknown schema version for columns: {columns}")

# Test pipeline
pipeline = VersionedPipeline()

# Test data v1
data_v1 = pd.DataFrame({
    'id': [1, 2],
    'name': ['John', 'Jane']
})

print("=== Processing V1 Data ===")
result_v1 = pipeline.process_data(data_v1)
print(result_v1)

# Test data v2
data_v2 = pd.DataFrame({
    'id': [3, 4],
    'name': ['Bob', 'Alice'],
    'email': ['bob@example.com', 'alice@example.com']
})

print("\n=== Processing V2 Data ===")
result_v2 = pipeline.process_data(data_v2)
print(result_v2)
```

## Best Practices Schema Evolution

### 1. **Złote zasady**:

```python
class SchemaEvolutionRules:
    """Best practices dla schema evolution"""
    
    @staticmethod
    def safe_changes():
        """Bezpieczne zmiany schema"""
        return [
            "✅ Dodaj opcjonalne pole",
            "✅ Dodaj pole z default value", 
            "✅ Usuń opcjonalne pole",
            "✅ Zwiększ precision liczby",
            "✅ Zmień string na union[string, null]",
            "✅ Dodaj wartość do enum (na końcu)",
            "✅ Rename field (z aliasem)"
        ]
    
    @staticmethod
    def dangerous_changes():
        """Niebezpieczne zmiany schema"""
        return [
            "❌ Usuń wymagane pole",
            "❌ Dodaj wymagane pole bez default",
            "❌ Zmień typ pola (int -> string)",
            "❌ Zmniejsz precision liczby", 
            "❌ Usuń wartość z enum",
            "❌ Rename required field bez aliasu",
            "❌ Zmień znaczenie istniejącego pola"
        ]
    
    @staticmethod
    def evolution_checklist():
        """Checklist przed zmianą schema"""
        return [
            "□ Czy zmiana jest backward compatible?",
            "□ Czy zmiana jest forward compatible?",
            "□ Czy mamy strategy migracji danych?",
            "□ Czy testy obejmują compatibility?",
            "□ Czy documentation jest updated?",
            "□ Czy monitoring alertuje na schema changes?",
            "□ Czy mamy rollback plan?"
        ]

# Wyświetl guidelines
print("=== SAFE SCHEMA CHANGES ===")
for rule in SchemaEvolutionRules.safe_changes():
    print(rule)

print("\n=== DANGEROUS SCHEMA CHANGES ===") 
for rule in SchemaEvolutionRules.dangerous_changes():
    print(rule)

print("\n=== EVOLUTION CHECKLIST ===")
for item in SchemaEvolutionRules.evolution_checklist():
    print(item)
```

### 2. **Testing Schema Evolution**:

```python
import unittest
from typing import List, Dict

class SchemaEvolutionTest(unittest.TestCase):
    """Unit testy dla schema evolution"""
    
    def setUp(self):
        self.registry = SchemaRegistry()
        
        # Register base schemas
        self.user_v1 = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
            },
            "required": ["id", "name"]
        }
        
        self.user_v2 = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"}
            },
            "required": ["id", "name"]
        }
        
        self.registry.register_schema("users", self.user_v1)
        self.registry.register_schema("users", self.user_v2)
    
    def test_backward_compatibility(self):
        """Test że nowe schema może czytać stare dane"""
        old_data = {"id": 1, "name": "John"}
        
        # Waliduj z nową schema
        try:
            jsonschema.validate(old_data, self.user_v2)
            result = True
        except:
            result = False
        
        self.assertTrue(result, "V2 schema should read V1 data")
    
    def test_forward_compatibility(self):
        """Test że stara schema może ignorować nowe pola"""
        new_data = {"id": 1, "name": "John", "email": "john@example.com"}
        
        # Remove additionalProperties: False for forward compatibility
        modified_v1 = self.user_v1.copy()
        modified_v1.pop('additionalProperties', None)
        
        try:
            jsonschema.validate(new_data, modified_v1)
            result = True
        except:
            result = False
        
        self.assertTrue(result, "V1 schema should ignore new fields")
    
    def test_schema_registry_compatibility_check(self):
        """Test że registry blokuje niekompatybilne zmiany"""
        
        # Próbuj dodać incompatible schema
        incompatible_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "email": {"type": "string"}  # Brak 'name'!
            },
            "required": ["id", "email"]
        }
        
        with self.assertRaises(ValueError):
            self.registry.register_schema("users", incompatible_schema)

# Uruchom testy
if __name__ == "__main__":
    unittest.main(argv=[''], exit=False, verbosity=2)
```

## Monitoring Schema Evolution

```python
import logging
from datetime import datetime
from typing import Optional

class SchemaEvolutionMonitor:
    """Monitor zmian schema w czasie"""
    
    def __init__(self):
        self.logger = logging.getLogger("schema_evolution")
        self.changes_log = []
    
    def log_schema_change(self, 
                         subject: str, 
                         old_version: Optional[int], 
                         new_version: int,
                         change_type: str,
                         compatibility_mode: str):
        """Loguj zmianę schema"""
        
        change_record = {
            'timestamp': datetime.now(),
            'subject': subject,
            'old_version': old_version,
            'new_version': new_version,
            'change_type': change_type,
            'compatibility_mode': compatibility_mode
        }
        
        self.changes_log.append(change_record)
        
        self.logger.info(
            f"Schema evolution: {subject} v{old_version} -> v{new_version} "
            f"({change_type}, {compatibility_mode} compatibility)"
        )
        
        # Alert jeśli breaking change
        if change_type == "BREAKING":
            self.logger.warning(
                f"⚠️  BREAKING CHANGE detected in {subject}! "
                f"Manual intervention may be required."
            )
    
    def get_evolution_stats(self) -> Dict:
        """Statystyki evolution"""
        
        if not self.changes_log:
            return {"total_changes": 0}
        
        by_subject = {}
        by_type = {}
        
        for change in self.changes_log:
            subject = change['subject']
            change_type = change['change_type']
            
            by_subject[subject] = by_subject.get(subject, 0) + 1
            by_type[change_type] = by_type.get(change_type, 0) + 1
        
        return {
            "total_changes": len(self.changes_log),
            "by_subject": by_subject,
            "by_type": by_type,
            "last_change": self.changes_log[-1]['timestamp']
        }

# Setup monitoring
monitor = SchemaEvolutionMonitor()

# Symuluj zmiany
monitor.log_schema_change("users", None, 1, "INITIAL", "N/A")
monitor.log_schema_change("users", 1, 2, "BACKWARD_COMPATIBLE", "BACKWARD")
monitor.log_schema_change("events", None, 1, "INITIAL", "N/A")

print("=== Schema Evolution Stats ===")
stats = monitor.get_evolution_stats()
for key, value in stats.items():
    print(f"{key}: {value}")
```

## Podsumowanie

### ✅ Najlepsze praktyki Schema Evolution:

1. **Zawsze rób changes backward compatible**
2. **Używaj optional fields dla nowych danych**
3. **Nigdy nie usuwaj required fields**
4. **Testuj compatibility w CI/CD**
5. **Dokumentuj wszystkie zmiany**
6. **Monitoruj schema changes**
7. **Miej rollback strategy**

### 🛠️ Narzędzia według przypadku:
- **Apache Avro** - najlepsze native schema evolution
- **Delta Lake** - schema evolution w data lakes
- **Apache Iceberg** - advanced table evolution
- **Schema Registry** - centralne zarządzanie
- **JSON Schema** - web APIs i documents

**Schema Evolution = Controlled Change Management** 🔄