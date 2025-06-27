# PostgreSQL vs SQLite vs CosmosDB - porównanie i wybór

## Przegląd baz danych

### PostgreSQL
**Zaawansowana, open-source relacyjna baza danych**

### SQLite  
**Lekka, wbudowana relacyjna baza danych**

### CosmosDB
**Globally distributed, multi-model baza chmurowa Microsoft**

## Szczegółowe porównanie

### 1. **Architektura i deployment**

#### PostgreSQL:
```sql
-- Serwer bazy danych - wymaga instalacji i konfiguracji
-- Połączenie przez TCP/IP
psql -h localhost -p 5432 -U username -d database_name
```
- 🏗️ **Client-server** - wymaga serwera bazy danych
- 🔧 **Wymaga instalacji** i konfiguracji
- 🌐 **Sieciowy dostęp** - TCP/IP
- 👥 **Multi-user** - obsługuje wielu użytkowników jednocześnie

#### SQLite:
```python
import sqlite3
# Cała baza to jeden plik!
conn = sqlite3.connect('database.db')
```
- 📁 **File-based** - baza to jeden plik
- 🚫 **Zero-configuration** - nie wymaga instalacji serwera
- 🔗 **Bezpośrednie połączenie** - aplikacja łączy się z plikiem
- 👤 **Single-user** - jeden writer naraz

#### CosmosDB:
```python
from azure.cosmos import CosmosClient
# Chmurowa - zawsze dostępna
client = CosmosClient(url, credential)
```
- ☁️ **Fully managed** - Microsoft zarządza infrastrukturą
- 🌍 **Global distribution** - dane replikowane globalnie
- 📈 **Auto-scaling** - automatycznie skaluje wydajność
- 💳 **Pay-per-use** - płacisz za zużycie

### 2. **Wydajność i skalowanie**

| Aspekt | PostgreSQL | SQLite | CosmosDB |
|--------|------------|--------|----------|
| **Concurrent reads** | ✅ Bardzo dobre | ⚠️ Dobre | ✅ Bardzo dobre |
| **Concurrent writes** | ✅ Bardzo dobre | ❌ Jeden writer | ✅ Bardzo dobre |
| **Rozmiar DB** | 🔥 32TB+ | ⚠️ 281TB (ale praktycznie <1GB) | 🔥 Unlimited |
| **Transactions/sec** | 🔥 Dziesiątki tysięcy | ⚠️ Tysiące | 🔥 Miliony |
| **Vertical scaling** | ✅ Tak | ❌ Ograniczone | ✅ Automatyczne |
| **Horizontal scaling** | ⚠️ Partycjonowanie | ❌ Nie | ✅ Natywne |

### 3. **Funkcjonalność**

#### PostgreSQL - wszystko co potrzebujesz:
```sql
-- Zaawansowane typy danych
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    properties JSONB,           -- JSON z indeksowaniem
    location POINT,             -- Geometria
    tags TEXT[],                -- Tablice
    price NUMERIC(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Zaawansowane zapytania
SELECT name, properties->'color' as color
FROM products 
WHERE properties @> '{"category": "electronics"}'
AND location <-> POINT(52.2297, 21.0122) < 1000;  -- W promieniu 1km od Warszawy

-- Funkcje okna
SELECT name, price,
       ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) as rank
FROM products;

-- CTE (Common Table Expressions)
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 1 as level
    FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree;
```

#### SQLite - podstawy, ale solidnie:
```sql
-- Podstawowe typy (TEXT, INTEGER, REAL, BLOB)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    data TEXT,  -- JSON jako tekst
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- JSON obsługa (od wersji 3.45)
SELECT json_extract(data, '$.age') FROM users;

-- Ograniczone typy danych
-- Brak BOOLEAN (używaj INTEGER 0/1)
-- Brak DATE/TIME (używaj TEXT lub INTEGER)
```

#### CosmosDB - multi-model:
```python
# SQL API (DocumentDB)
{
    "id": "1",
    "name": "Jan Kowalski",
    "address": {
        "city": "Warszawa",
        "country": "Poland"
    },
    "orders": [
        {"id": "order1", "total": 299.99}
    ]
}

# MongoDB API
db.users.find({"address.city": "Warszawa"})

# Gremlin API (Graph)
g.V().hasLabel('person').has('name', 'Jan').out('knows').values('name')

# Table API (Key-Value)
# Cassandra API
```

### 4. **Koszty**

#### PostgreSQL:
- ✅ **Free** - licencja open source
- 💰 **Koszty infrastruktury** - serwery, administracja
- 👨‍💻 **Koszty zespołu** - DBA, DevOps

#### SQLite:
- ✅ **Free** - public domain
- ✅ **Zero operational costs** - brak infrastruktury
- ⚠️ **Koszty skalowania** - gdy trzeba przenosić na inne rozwiązanie

#### CosmosDB:
- 💸 **Expensive** - od $0.008/100 RU/hour
- 💳 **Pay-as-you-go** - płacisz za zużycie
- ⚠️ **Surprise bills** - łatwo przekroczyć budżet

```python
# Przykładowe koszty CosmosDB (2024):
# 1000 RU/s provisioned: ~$58/miesiąc
# 1 milion operacji odczytu: ~$0.40
# 1 GB storage: ~$0.25/miesiąc
# Global replication: dodatkowe koszty
```

### 5. **Przypadki użycia**

#### ✅ Używaj **PostgreSQL** gdy:
```sql
-- Zaawansowane aplikacje biznesowe
-- E-commerce, CRM, ERP
-- Analytics i reporting
-- Aplikacje wymagające ACID
-- Zespół zna SQL
-- Potrzebujesz zaawansowanych funkcji

-- Przykład: E-commerce
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    status order_status_enum DEFAULT 'pending',
    items JSONB,
    total NUMERIC(10,2) CHECK (total >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### ✅ Używaj **SQLite** gdy:
```python
# Aplikacje desktop/mobile
# Prototypy i małe projekty
# Cache lokalny
# Embedded systems
# Testing
# Gdy nie potrzebujesz concurrent writes

# Przykład: Aplikacja mobilna
import sqlite3
conn = sqlite3.connect('app_data.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
''')

cursor.execute("INSERT INTO settings VALUES ('theme', 'dark')")
conn.commit()
```

#### ✅ Używaj **CosmosDB** gdy:
```python
# Aplikacje globalne
# Wysokie wymagania SLA (99.999%)
# Potrzebujesz różnych modeli danych
# Microsoft Azure ecosystem
# Automatic scaling
# Unlimited scale

# Przykład: IoT sensors
{
    "id": "sensor_123",
    "deviceType": "temperature",
    "location": "Warsaw",
    "readings": [
        {"timestamp": "2024-01-01T10:00:00Z", "value": 22.5},
        {"timestamp": "2024-01-01T10:01:00Z", "value": 22.7}
    ],
    "metadata": {
        "firmware": "1.2.3",
        "battery": 85
    }
}
```

## Migracja między bazami

### SQLite → PostgreSQL:
```bash
# Export z SQLite
sqlite3 mydb.db .dump > dump.sql

# Import do PostgreSQL (po drobnych modyfikacjach)
psql -U user -d database -f dump.sql
```

### PostgreSQL → CosmosDB:
```python
# ETL proces
import psycopg2
from azure.cosmos import CosmosClient

# Export z PostgreSQL
conn = psycopg2.connect("postgresql://...")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")

# Import do CosmosDB
cosmos_client = CosmosClient(url, credential)
container = cosmos_client.get_database("db").get_container("users")

for row in cursor.fetchall():
    document = {
        "id": str(row[0]),
        "name": row[1],
        "email": row[2]
    }
    container.create_item(document)
```

## Benchmark praktyczny

```python
# Test wydajności - 100,000 insertów
import time

# SQLite
start = time.time()
conn = sqlite3.connect('test.db')
cursor = conn.cursor()
cursor.execute('BEGIN TRANSACTION')
for i in range(100000):
    cursor.execute("INSERT INTO users VALUES (?, ?)", (i, f"user{i}"))
cursor.execute('COMMIT')
sqlite_time = time.time() - start
# Wynik: ~2-5 sekund

# PostgreSQL  
start = time.time()
conn = psycopg2.connect("postgresql://...")
cursor = conn.cursor()
cursor.execute('BEGIN')
cursor.executemany(
    "INSERT INTO users VALUES (%s, %s)",
    [(i, f"user{i}") for i in range(100000)]
)
cursor.execute('COMMIT')
postgres_time = time.time() - start
# Wynik: ~1-3 sekundy

# CosmosDB
# Wynik: ~10-30 sekund (network latency)
# Ale może obsłużyć miliony concurrent operations
```

## Podsumowanie - kiedy co wybrać?

### 🚀 **Startup/MVP**:
```
SQLite → PostgreSQL → CosmosDB
(według wzrostu wymagań)
```

### 🏢 **Enterprise**:
```
PostgreSQL (on-premise)
lub
CosmosDB (cloud-first)
```

### 📱 **Mobile/Desktop**:
```
SQLite (zawsze pierwsza opcja)
```

### 🌍 **Global scale**:
```
CosmosDB lub PostgreSQL + sharding
```

### 💰 **Ograniczony budżet**:
```
SQLite → PostgreSQL
(unikaj CosmosDB dopóki nie musisz)
```

| Cecha | SQLite | PostgreSQL | CosmosDB |
|-------|--------|------------|----------|
| **Łatwość** | 🟢🟢🟢 | 🟡🟡 | 🟡 |
| **Wydajność** | 🟢🟢 | 🟢🟢🟢 | 🟢🟢🟢 |
| **Skalowalność** | 🔴 | 🟢🟢 | 🟢🟢🟢 |
| **Funkcjonalność** | 🟡 | 🟢🟢🟢 | 🟢🟢 |
| **Koszt** | 🟢🟢🟢 | 🟢🟢 | 🔴 |
| **Niezawodność** | 🟢🟢 | 🟢🟢🟢 | 🟢🟢🟢 |