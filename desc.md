# Architektura ETL Apify - Dokumentacja

## Przegląd architektury

Kod wykorzystuje **wzorzec Template Method** i **architekturę warstwową (Bronze-Silver-Gold)** znaną jako **Medallion Architecture** (standard w Databricks).

---

## 1. AbstractDatasourceClass.py - Klasa abstrakcyjna

**Lokalizacja:** `snowflake_to_databricks/Core/AbstractDatasourceClass.py`

### Cel
To jest **szablon** dla wszystkich źródeł danych. Definiuje kontrakt, który każde źródło danych musi spełnić.

### Definicja 3 abstrakcyjnych metod:
- `bronzeprocessing()` - warstwa surowych danych (raw data)
- `silverprocessing()` - warstwa oczyszczonych danych (cleaned data)
- `goldprocessing()` - warstwa agregowanych/biznesowych danych (aggregated/business data)

### Architektura Medallion (Bronze → Silver → Gold):
- **Bronze Layer**: Surowe dane z API, bez transformacji
- **Silver Layer**: Oczyszczone, znormalizowane dane
- **Gold Layer**: Agregacje, metryki biznesowe, dane gotowe do raportowania

```python
from abc import ABC, abstractmethod

class AbstractDatasourceClass(ABC):
    @abstractmethod
    def bronzeprocessing(self, data=None):
        """Process Bronze layer"""
        pass

    @abstractmethod
    def silverprocessing(self, data=None):
        """Process Silver layer"""
        pass

    @abstractmethod
    def goldprocessing(self, data=None):
        """Process Gold layer"""
        pass
```

---

## 2. DatasourceApifyClass.py - Konkretna implementacja

**Lokalizacja:** `snowflake_to_databricks/Core/ELTApify/DatasourceApifyClass.py`

### Cel
Klasa **dziedziczy** po `AbstractDatasourceClass` i implementuje metody dla źródła danych Apify.

### Inicjalizacja (linie 9-11)
```python
def __init__(self):
    super().__init__()
    self.bronze_service = ServiceBronze()
```
Tworzy instancję `ServiceBronze`, która jest odpowiedzialna za komunikację z API.

### Bronze Processing (linie 13-48)
Pobiera **3 zestawy danych** z Apify API:

1. **actors** - lista wszystkich aktorów (web scraperów)
   ```python
   bronze_data['actors'] = self.bronze_service.get_actors()
   ```

2. **actor_runs** - lista uruchomień aktorów
   ```python
   bronze_data['actor_runs'] = self.bronze_service.get_actor_runs()
   ```

3. **actor_runs_details** - szczegółowe informacje o każdym uruchomieniu
   ```python
   bronze_data['actor_runs_details'] = self.bronze_service.get_actor_runs_details()
   ```

**Zwraca:** Słownik zawierający 3 DataFrame'y pandas

### Silver Processing (linie 50-57)
Obecnie **puste** - tylko wypisuje komunikaty.
**To miejsce na:**
- Czyszczenie danych
- Normalizację
- Usuwanie duplikatów
- Obsługę null values
- Łączenie tabel (joins)

### Gold Processing (linie 59-66)
Obecnie **puste** - tylko wypisuje komunikaty.
**To miejsce na:**
- Agregacje (sumy, średnie)
- Metryki biznesowe
- Raporty
- KPI

---

## 3. ServiceApifyBronze.py - Warstwa dostępu do danych

**Lokalizacja:** `snowflake_to_databricks/Core/ELTApify/ServicesApify/ServiceApifyBronze.py`

### Cel
**Warstwa dostępu do danych** - odpowiada za komunikację z Apify REST API.

### Inicjalizacja (linie 18-30)
```python
def __init__(self):
    self.apify_secret = api_token
    self.headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {self.apify_secret}'
    }
```
Konfiguruje autentykację Bearer token dla API.

### get_actors() (linie 32-51)
```python
url = f"https://api.apify.com/v2/acts"
response = requests.get(url, headers=headers)
items = response.json().get("data", {}).get("items", [])
actors = pd.DataFrame(items)
return actors
```
**Endpoint:** `GET https://api.apify.com/v2/acts`
**Zwraca:** DataFrame ze wszystkimi aktorami

### get_actor_runs() (linie 54-74)
```python
url = f"https://api.apify.com/v2/actor-runs"
response = requests.get(url, headers=headers)
items = response.json().get('data', {}).get('items', [])
actor_runs = pd.DataFrame(items)
return actor_runs
```
**Endpoint:** `GET https://api.apify.com/v2/actor-runs`
**Zwraca:** DataFrame ze wszystkimi uruchomieniami

### get_actor_runs_details() (linie 81-109) - NAJCIEKAWSZA METODA
```python
def get_actor_runs_details(self):
    def fetch_single_run(run_id):
        url = f"https://api.apify.com/v2/actor-runs/{run_id}"
        response = requests.get(url, headers=headers)
        return response.json().get('data', {})

    with ThreadPoolExecutor(max_workers=15) as executor:
        runs_detailed_list = list(executor.map(fetch_single_run, self.get_unique_actor_runs()))

    runs_detailed_df = pd.DataFrame(runs_detailed_list)
```

**Kluczowe cechy:**
- Używa **wielowątkowości** (`ThreadPoolExecutor`) dla optymalizacji
- Pobiera szczegóły **równolegle** (15 wątków jednocześnie)
- Dla każdego `run_id` wykonuje osobne żądanie API

**Obliczane metryki wydajności:**
```python
runs_detailed_df['time_to_load_in_sec'] = (finishedAt - startedAt).total_seconds()
runs_detailed_df['time_to_load_in_min'] = time_to_load_in_sec / 60
runs_detailed_df['pages_scraped'] = usage.get('DATASET_WRITES')
runs_detailed_df['pages_scraped_per_sec'] = pages_scraped / time_to_load_in_sec
```

**Endpoint:** `GET https://api.apify.com/v2/actor-runs/{run_id}` (dla każdego run_id)
**Zwraca:** DataFrame z szczegółami + obliczonymi metrykami

---

## 4. ETLApify.py - Punkt wejścia

**Lokalizacja:** `snowflake_to_databricks/ETLApify.py`

### Cel
**Główny skrypt** orkiestrujący cały proces ETL.

```python
def main():
    datasourceApifyClass = DatasourceApifyClass()
    datasourceApifyClass.bronzeprocessing()
    datasourceApifyClass.silverprocessing()
    datasourceApifyClass.goldprocessing()

if __name__ == "__main__":
    main()
```

### Przepływ:
1. Tworzy instancję `DatasourceApifyClass`
2. Wykonuje proces Bronze (pobieranie surowych danych)
3. Wykonuje proces Silver (oczyszczanie - obecnie puste)
4. Wykonuje proces Gold (agregacje - obecnie puste)

---

## Przepływ danych - Diagram

```
┌─────────────────┐
│  ETLApify.py    │ ← Punkt wejścia
│     main()      │
└────────┬────────┘
         │
         │ tworzy instancję
         ↓
┌──────────────────────────┐
│ DatasourceApifyClass     │ ← Implementacja dla Apify
│ (dziedziczy po Abstract) │
└──────────┬───────────────┘
           │
           │ wywołuje metody
           ↓
    ┌──────────────┐
    │ Bronze Layer │
    └──────┬───────┘
           │
           │ używa
           ↓
    ┌────────────────┐
    │ ServiceBronze  │ ← Warstwa API
    └────────┬───────┘
             │
             │ wykonuje HTTP requests
             ↓
    ┌─────────────────────┐
    │   Apify REST API    │
    │ ┌─────────────────┐ │
    │ │ GET /acts       │ │ → actors
    │ │ GET /actor-runs │ │ → actor_runs
    │ │ GET /actor-runs │ │ → actor_runs_details
    │ │     /{id}       │ │   (wielowątkowo)
    │ └─────────────────┘ │
    └─────────────────────┘
             │
             │ zwraca JSON
             ↓
    ┌────────────────┐
    │ pandas DataFrame│
    └────────┬───────┘
             │
             │ przekazuje dane
             ↓
    ┌──────────────┐
    │ Silver Layer │ (obecnie puste)
    └──────┬───────┘
             │
             ↓
    ┌──────────────┐
    │  Gold Layer  │ (obecnie puste)
    └──────────────┘
```

---

## Zalety obecnego podejścia

### 1. Separacja obaw (Separation of Concerns)
Każda klasa ma jedną, jasno określoną odpowiedzialność:
- `AbstractDatasourceClass` → Definicja kontraktu
- `DatasourceApifyClass` → Logika ETL dla Apify
- `ServiceBronze` → Komunikacja z API
- `ETLApify.py` → Orkiestracja

### 2. Łatwa rozszerzalność
Można dodać nowe źródła danych bez modyfikowania istniejącego kodu:
- `DatasourceAzureDevopsClass` (już istnieje)
- `DatasourceMendClass` (już istnieje)
- `DatasourceNewrelicClass` (już istnieje)

Wszystkie implementują ten sam interfejs → ten sam sposób użycia.

### 3. Reużywalność
`AbstractDatasourceClass` jest szablonem dla wszystkich źródeł danych.
Każde źródło implementuje Bronze/Silver/Gold layers w ten sam sposób.

### 4. Medallion Architecture
Standardowy wzorzec w data engineering (szczególnie w Databricks):
- **Bronze**: Surowe dane z API (immutable)
- **Silver**: Oczyszczone, znormalizowane
- **Gold**: Agregacje, metryki biznesowe

### 5. Optymalizacja wydajności
`get_actor_runs_details()` używa **wielowątkowości**:
```python
with ThreadPoolExecutor(max_workers=15) as executor:
    runs_detailed_list = list(executor.map(fetch_single_run, run_ids))
```
Zamiast 100 sekwencyjnych żądań → 15 równoległych wątków = znacznie szybsze wykonanie.

### 6. Wzorzec Template Method
Definiuje szkielet algorytmu w klasie bazowej, a konkretne implementacje w podklasach.

---

## Co można poprawić

### 1. Silver i Gold layers są puste
**Problem:** Brakuje transformacji i agregacji danych.

**Sugestia:**
```python
def silverprocessing(self, data=None):
    # Jeśli data=None, pobierz z Bronze
    if data is None:
        data = self.bronzeprocessing()

    # Oczyszczanie
    silver_data = {}
    silver_data['actors'] = self._clean_actors(data['actors'])
    silver_data['actor_runs'] = self._clean_runs(data['actor_runs'])

    return silver_data

def goldprocessing(self, data=None):
    # Agregacje
    gold_metrics = {
        'total_runs': len(data['actor_runs']),
        'avg_duration': data['actor_runs_details']['time_to_load_in_sec'].mean(),
        'success_rate': self._calculate_success_rate(data)
    }
    return gold_metrics
```

### 2. Dane nie są przekazywane między warstwami
**Problem:** `bronzeprocessing()` zwraca dane, ale nigdzie nie są one używane.

**Sugestia:**
```python
def main():
    datasource = DatasourceApifyClass()

    bronze_data = datasource.bronzeprocessing()
    silver_data = datasource.silverprocessing(data=bronze_data)
    gold_data = datasource.goldprocessing(data=silver_data)

    return gold_data
```

### 3. Brak obsługi błędów
**Problem:** Brak try/except w żądaniach HTTP.

**Sugestia:**
```python
def get_actors(self):
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return pd.DataFrame(response.json().get("data", {}).get("items", []))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching actors: {e}")
        return pd.DataFrame()  # Pusty DataFrame
```

### 4. Hardcoded credentials
**Problem:** `from config import apify_secret` (wspominane w komentarzu linia 9-10).

**Sugestia:**
- Użyj zmiennych środowiskowych (`os.environ.get('APIFY_TOKEN')`)
- Databricks Secrets w produkcji
- Nigdy nie commituj `config.py` do repo

### 5. Brak logowania
**Problem:** Używane są `print()` statements.

**Sugestia:**
```python
import logging

logger = logging.getLogger(__name__)

logger.info("Starting actors - 1 of 3 datasets")
logger.error(f"Failed to fetch actors: {e}")
```

### 6. Brak paginacji
**Problem:** API może zwracać tylko pierwsze N wyników.

**Sugestia:**
```python
def get_all_actors(self):
    all_actors = []
    offset = 0
    limit = 100

    while True:
        url = f"https://api.apify.com/v2/acts?offset={offset}&limit={limit}"
        response = requests.get(url, headers=self.headers)
        items = response.json().get("data", {}).get("items", [])

        if not items:
            break

        all_actors.extend(items)
        offset += limit

    return pd.DataFrame(all_actors)
```

### 7. Brak persistence
**Problem:** Dane są tylko w pamięci (DataFrame).

**Sugestia:**
```python
def bronzeprocessing(self, data=None):
    bronze_data = self._fetch_bronze_data()

    # Zapisz do Databricks Delta Lake
    for name, df in bronze_data.items():
        df.write.format("delta").mode("overwrite").saveAsTable(f"bronze.apify_{name}")

    return bronze_data
```

---

## Przykład użycia

```python
# Uruchomienie ETL
python ETLApify.py

# Output:
==========
Apify bronze layer
===============

Starting actors - 1 of 3 datasets
Output: 45 rows

Starting actor runs - 2 of 3 datasets
Output: 230 rows

Starting detailed actor runs - 3 of 3 datasets
Output: 230 rows

===============
Done: Apify bronze layer
==========

===============
Silver layer data:
==========

==========
Done: Apify silver layer
===============

===============
Gold layer data:
==========

==========
Done: Apify gold layer
===============
```

---

## Podsumowanie

Kod prezentuje **solidne podstawy** architektury ETL z wykorzystaniem wzorców projektowych i best practices z data engineeringu. Główne obszary do rozwoju to:

1. Implementacja logiki Silver/Gold layers
2. Dodanie obsługi błędów i logowania
3. Persistence danych (Delta Lake, Parquet)
4. Bezpieczne zarządzanie credentials
5. Paginacja dla dużych zbiorów danych

Architektura jest **skalowalna** i **łatwa do rozszerzenia** o nowe źródła danych dzięki zastosowaniu abstrakcji i wzorca Template Method.
