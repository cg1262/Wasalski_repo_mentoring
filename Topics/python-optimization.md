# Python/SQL - techniki optymalizacji skryptów

## Optymalizacja kodu Python

### 1. **Algorytmy i struktury danych**

#### Wybór właściwej struktury danych:
```python
import time
from collections import deque, defaultdict, Counter

# ❌ Wolno - list dla częstych wyszukiwań
data = [1, 2, 3, 4, 5] * 1000
start = time.time()
for i in range(1000):
    if 2500 in data:  # O(n) każde wyszukiwanie
        pass
print(f"List search: {time.time() - start:.4f}s")

# ✅ Szybko - set dla wyszukiwań
data_set = set(data)
start = time.time()
for i in range(1000):
    if 2500 in data_set:  # O(1) każde wyszukiwanie
        pass
print(f"Set search: {time.time() - start:.4f}s")

# ✅ Dict dla mapping
# Zamiast:
def get_grade_slow(score):
    if score >= 90: return 'A'
    elif score >= 80: return 'B'
    elif score >= 70: return 'C'
    else: return 'F'

# Użyj:
grade_map = {range(90, 101): 'A', range(80, 90): 'B', 
             range(70, 80): 'C', range(0, 70): 'F'}

def get_grade_fast(score):
    for score_range, grade in grade_map.items():
        if score in score_range:
            return grade

# ✅ Deque dla operacji na końcach
queue = deque()
queue.append(1)      # O(1)
queue.appendleft(0)  # O(1)
queue.pop()          # O(1)
queue.popleft()      # O(1)

# ✅ Counter dla zliczania
text = "hello world hello"
word_count = Counter(text.split())
print(word_count)  # Counter({'hello': 2, 'world': 1})
```

#### List/Dict comprehensions vs loops:
```python
import timeit

# ❌ Wolno - tradycyjna pętla
def traditional_loop():
    result = []
    for i in range(1000):
        if i % 2 == 0:
            result.append(i ** 2)
    return result

# ✅ Szybko - list comprehension
def list_comp():
    return [i ** 2 for i in range(1000) if i % 2 == 0]

# ✅ Najszybciej - generator expression
def generator_exp():
    return (i ** 2 for i in range(1000) if i % 2 == 0)

# Pomiar czasu
print(f"Traditional: {timeit.timeit(traditional_loop, number=1000):.4f}s")
print(f"List comp: {timeit.timeit(list_comp, number=1000):.4f}s")
print(f"Generator: {timeit.timeit(lambda: list(generator_exp()), number=1000):.4f}s")
```

### 2. **Wykorzystanie bibliotek NumPy i Pandas**

#### NumPy - wektoryzacja:
```python
import numpy as np
import time

# ❌ Wolno - Python loops
def python_sum(arr):
    result = 0
    for x in arr:
        result += x ** 2
    return result

# ✅ Szybko - NumPy wektoryzacja
def numpy_sum(arr):
    return np.sum(arr ** 2)

# Test
data = list(range(1_000_000))
np_data = np.array(data)

start = time.time()
python_result = python_sum(data)
python_time = time.time() - start

start = time.time()
numpy_result = numpy_sum(np_data)
numpy_time = time.time() - start

print(f"Python: {python_time:.4f}s")
print(f"NumPy: {numpy_time:.4f}s")
print(f"Speedup: {python_time/numpy_time:.1f}x")
```

#### Pandas - efektywne operacje:
```python
import pandas as pd

# Przykładowe dane
df = pd.DataFrame({
    'A': np.random.randn(1_000_000),
    'B': np.random.randn(1_000_000),
    'C': np.random.choice(['X', 'Y', 'Z'], 1_000_000)
})

# ❌ Wolno - iterrows()
start = time.time()
result = []
for index, row in df.iterrows():
    if row['A'] > 0:
        result.append(row['A'] * row['B'])
iterrows_time = time.time() - start

# ✅ Szybko - wektoryzacja
start = time.time()
mask = df['A'] > 0
result = df.loc[mask, 'A'] * df.loc[mask, 'B']
vectorized_time = time.time() - start

# ✅ Najszybciej - NumPy where
start = time.time()
result = np.where(df['A'] > 0, df['A'] * df['B'], 0)
numpy_where_time = time.time() - start

print(f"iterrows: {iterrows_time:.4f}s")
print(f"vectorized: {vectorized_time:.4f}s") 
print(f"numpy where: {numpy_where_time:.4f}s")
```

### 3. **Multiprocessing i Multithreading**

#### CPU-intensive tasks - multiprocessing:
```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import time

def cpu_intensive_task(n):
    """Symulacja CPU-intensive task"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result

def run_sequential(tasks):
    return [cpu_intensive_task(task) for task in tasks]

def run_multiprocessing(tasks):
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        return list(executor.map(cpu_intensive_task, tasks))

# Test
tasks = [100_000] * 8

start = time.time()
sequential_result = run_sequential(tasks)
sequential_time = time.time() - start

start = time.time()
parallel_result = run_multiprocessing(tasks)
parallel_time = time.time() - start

print(f"Sequential: {sequential_time:.2f}s")
print(f"Parallel: {parallel_time:.2f}s")
print(f"Speedup: {sequential_time/parallel_time:.1f}x")
```

#### I/O-intensive tasks - multithreading:
```python
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
import time

def fetch_url(url):
    """Symulacja I/O task"""
    try:
        response = requests.get(url, timeout=5)
        return len(response.content)
    except:
        return 0

def run_sequential_io(urls):
    return [fetch_url(url) for url in urls]

def run_multithreading(urls):
    with ThreadPoolExecutor(max_workers=10) as executor:
        return list(executor.map(fetch_url, urls))

# Test URLs
urls = ['https://httpbin.org/delay/1'] * 5

start = time.time()
sequential_result = run_sequential_io(urls)
sequential_time = time.time() - start

start = time.time()
parallel_result = run_multithreading(urls)
parallel_time = time.time() - start

print(f"Sequential I/O: {sequential_time:.2f}s")
print(f"Parallel I/O: {parallel_time:.2f}s")
print(f"Speedup: {sequential_time/parallel_time:.1f}x")
```

### 4. **Memory optimization**

#### Generatory vs listy:
```python
import sys

# ❌ Memory hungry - lista
def create_list(n):
    return [i ** 2 for i in range(n)]

# ✅ Memory efficient - generator
def create_generator(n):
    return (i ** 2 for i in range(n))

n = 1_000_000

# Porównanie zużycia pamięci
list_data = create_list(n)
gen_data = create_generator(n)

print(f"List memory: {sys.getsizeof(list_data)} bytes")
print(f"Generator memory: {sys.getsizeof(gen_data)} bytes")

# Generator można używać tylko raz
print(f"List sum: {sum(list_data)}")
print(f"Generator sum: {sum(gen_data)}")
# print(f"Generator sum again: {sum(gen_data)}")  # 0 - już wyczerpany!
```

#### Słabe referencje i zarządzanie pamięcią:
```python
import weakref
import gc

class DataProcessor:
    def __init__(self, data):
        self.data = data
        self.cache = {}
    
    def process(self):
        # Operacje na danych
        pass

# ❌ Strong reference - może powodować memory leaks
processors = []
for i in range(1000):
    proc = DataProcessor(list(range(1000)))
    processors.append(proc)

# ✅ Weak reference - automatic cleanup
weak_processors = []
for i in range(1000):
    proc = DataProcessor(list(range(1000)))
    weak_processors.append(weakref.ref(proc))

# Manual garbage collection
gc.collect()
```

## Optymalizacja SQL

### 1. **Indeksy i query optimization**

#### Prawidłowe używanie indeksów:
```sql
-- ❌ Brak indeksu na często używanej kolumnie
SELECT * FROM orders WHERE customer_id = 12345;

-- ✅ Indeks na customer_id
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- ✅ Composite index dla wielu kolumn
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- ✅ Partial index dla częstych warunków
CREATE INDEX idx_active_orders ON orders(customer_id) WHERE status = 'active';

-- ❌ Funkcje w WHERE unieważniają indeks
SELECT * FROM orders WHERE UPPER(status) = 'ACTIVE';

-- ✅ Indeks funkcyjny
CREATE INDEX idx_status_upper ON orders(UPPER(status));
-- Lub lepiej:
SELECT * FROM orders WHERE status = 'ACTIVE';  -- bez funkcji
```

#### Query rewriting dla wydajności:
```sql
-- ❌ Wolne - korelowane subquery
SELECT c.customer_id, c.name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.customer_id 
    AND o.order_date > '2024-01-01'
);

-- ✅ Szybsze - JOIN
SELECT DISTINCT c.customer_id, c.name
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date > '2024-01-01';

-- ❌ Wolne - OR conditions
SELECT * FROM products 
WHERE category = 'Electronics' OR category = 'Books';

-- ✅ Szybsze - IN operator
SELECT * FROM products 
WHERE category IN ('Electronics', 'Books');

-- ❌ Wolne - LIKE z wildcard na początku
SELECT * FROM customers WHERE name LIKE '%kowal%';

-- ✅ Szybsze - full text search lub trigram
SELECT * FROM customers WHERE name % 'kowal';  -- PostgreSQL similarity
```

### 2. **Batch processing i pagination**

#### Efektywne przetwarzanie dużych zbiorów:
```sql
-- ❌ Wolne - processing wszystkich rekordów naraz
UPDATE large_table SET processed = true WHERE processed = false;

-- ✅ Szybsze - batch processing
DO $$
DECLARE
    batch_size INTEGER := 10000;
    processed_count INTEGER := 0;
BEGIN
    LOOP
        UPDATE large_table 
        SET processed = true 
        WHERE id IN (
            SELECT id FROM large_table 
            WHERE processed = false 
            LIMIT batch_size
        );
        
        GET DIAGNOSTICS processed_count = ROW_COUNT;
        EXIT WHEN processed_count = 0;
        
        COMMIT;  -- Commit każdego batcha
    END LOOP;
END $$;
```

#### Wydajna paginacja:
```sql
-- ❌ Wolne - OFFSET dla dużych liczb
SELECT * FROM orders 
ORDER BY order_date 
LIMIT 20 OFFSET 100000;  -- Bardzo wolne dla dużych OFFSET

-- ✅ Szybsze - cursor-based pagination
SELECT * FROM orders 
WHERE order_date > '2024-01-15 10:30:00'  -- ostatnia wartość z poprzedniej strony
ORDER BY order_date 
LIMIT 20;

-- ✅ Keyset pagination
SELECT * FROM orders 
WHERE (order_date, id) > ('2024-01-15 10:30:00', 12345)
ORDER BY order_date, id 
LIMIT 20;
```

### 3. **Analyzing query performance**

#### PostgreSQL - EXPLAIN ANALYZE:
```sql
-- Plan wykonania
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT c.name, COUNT(o.id) as order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE c.created_at > '2024-01-01'
GROUP BY c.id, c.name
HAVING COUNT(o.id) > 5
ORDER BY order_count DESC;

-- Monitoring długo działających zapytań
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

### 4. **Connection pooling i caching**

#### Python - connection pooling:
```python
import psycopg2
from psycopg2 import pool
import threading

class DatabaseManager:
    def __init__(self, connection_string, min_conn=1, max_conn=20):
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            min_conn, max_conn, connection_string
        )
        self.lock = threading.Lock()
    
    def get_connection(self):
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        self.connection_pool.putconn(conn)
    
    def execute_query(self, query, params=None):
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        finally:
            if conn:
                self.return_connection(conn)

# Użycie
db_manager = DatabaseManager("postgresql://user:pass@localhost/db")

def worker_thread(thread_id):
    for i in range(100):
        result = db_manager.execute_query(
            "SELECT * FROM orders WHERE customer_id = %s", 
            (thread_id,)
        )
        print(f"Thread {thread_id}: {len(result)} results")

# Uruchom wiele wątków
threads = []
for i in range(10):
    t = threading.Thread(target=worker_thread, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

#### Redis caching:
```python
import redis
import json
import hashlib

class CachedDatabase:
    def __init__(self, db_manager):
        self.db = db_manager
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_ttl = 3600  # 1 hour
    
    def _get_cache_key(self, query, params):
        # Utwórz unikalny klucz dla query + parametry
        query_hash = hashlib.md5(
            f"{query}{str(params)}".encode()
        ).hexdigest()
        return f"query_cache:{query_hash}"
    
    def execute_cached_query(self, query, params=None):
        cache_key = self._get_cache_key(query, params)
        
        # Sprawdź cache
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Jeśli nie ma w cache, wykonaj query
        result = self.db.execute_query(query, params)
        
        # Zapisz w cache
        self.redis_client.setex(
            cache_key, 
            self.cache_ttl, 
            json.dumps(result, default=str)
        )
        
        return result
    
    def invalidate_cache_pattern(self, pattern):
        """Usuń cache pasujący do wzorca"""
        keys = self.redis_client.keys(f"query_cache:*{pattern}*")
        if keys:
            self.redis_client.delete(*keys)

# Użycie
cached_db = CachedDatabase(db_manager)

# Pierwsze wywołanie - z bazy danych
result1 = cached_db.execute_cached_query(
    "SELECT * FROM products WHERE category = %s", 
    ("Electronics",)
)

# Drugie wywołanie - z cache
result2 = cached_db.execute_cached_query(
    "SELECT * FROM products WHERE category = %s", 
    ("Electronics",)
)
```

## Monitoring i profiling

### 1. **Python profiling**

#### cProfile - podstawowe profilowanie:
```python
import cProfile
import pstats

def slow_function():
    total = 0
    for i in range(1000000):
        total += i ** 2
    return total

def fast_function():
    import numpy as np
    arr = np.arange(1000000)
    return np.sum(arr ** 2)

# Profilowanie
profiler = cProfile.Profile()
profiler.enable()

# Testowany kod
result1 = slow_function()
result2 = fast_function()

profiler.disable()

# Analiza wyników
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 funkcji
```

#### line_profiler - profilowanie linia po linii:
```python
# Zainstaluj: pip install line_profiler

@profile  # Decorator dla line_profiler
def analyze_this_function():
    # Wolna operacja
    data = []
    for i in range(100000):
        data.append(i ** 2)
    
    # Szybsza operacja
    import numpy as np
    np_data = np.arange(100000) ** 2
    
    return data, np_data

# Uruchom: kernprof -l -v script.py
```

#### memory_profiler - monitoring pamięci:
```python
# pip install memory_profiler

from memory_profiler import profile

@profile
def memory_intensive_function():
    # Tworzenie dużej listy
    big_list = [i for i in range(1000000)]
    
    # Operacje na liście
    squared = [x ** 2 for x in big_list]
    
    # Usuwanie referencji
    del big_list
    
    return squared

# Uruchom: python -m memory_profiler script.py
```

### 2. **Database monitoring**

#### PostgreSQL - monitoring wydajności:
```sql
-- Top 10 najwolniejszych zapytań
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;

-- Indeksy nieużywane
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE idx_tup_read = 0;

-- Rozmiary tabel
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

## Best practices summary

### Python optimization checklist:
- ✅ Użyj właściwych struktur danych (set, dict, deque)
- ✅ Preferuj list comprehensions nad loops
- ✅ Wykorzystuj NumPy/Pandas do operacji numerycznych
- ✅ Używaj generatorów dla dużych zbiorów danych
- ✅ Multiprocessing dla CPU-intensive tasks
- ✅ Multithreading dla I/O-intensive tasks
- ✅ Profiluj kod przed optymalizacją
- ✅ Cache często używane wyniki

### SQL optimization checklist:
- ✅ Twórz indeksy na często filtrowane kolumny
- ✅ Używaj EXPLAIN ANALYZE do analizy planów
- ✅ Przepisuj korelowane subqueries na JOINy
- ✅ Używaj batch processing dla dużych aktualizacji
- ✅ Implementuj connection pooling
- ✅ Cache wyniki czasochłonnych zapytań
- ✅ Monitoruj długo działające zapytania
- ✅ Regularnie analizuj i optymalizuj indeksy

**Pamiętaj: Measure first, optimize second!** 📊