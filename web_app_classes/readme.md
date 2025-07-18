# Endpoint Data Explorer - Instrukcje konfiguracji

## Struktura projektu

```
endpoint_data_explorer/
├── app.py                 # Główna aplikacja Flask
├── requirements.txt       # Zależności Python
├── templates/
│   └── index.html        # Szablon HTML
└── endpoint_files/       # Folder z plikami endpointów
    ├── jira.py
    ├── sonarcloud.py
    ├── mend.py
    └── github.py
```

## Instalacja i konfiguracja

### 1. Przygotowanie środowiska

```bash
# Utwórz nowe środowisko wirtualne
python -m venv venv

# Aktywuj środowisko wirtualne
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt
```

### 2. Struktura plików endpointów

Każdy plik w folderze `endpoint_files` powinien zawierać:

```python
import pandas as pd
import requests  # jeśli używasz API calls

class NazwaEndpoint:
    """Opis klasy endpointu"""
    
    def __init__(self):
        # Konfiguracja połączenia (URL, tokeny, etc.)
        self.base_url = "https://api.example.com"
        self.token = "your-token"
    
    def nazwa_metody(self):
        """
        Opis metody - co robi
        """
        try:
            # Twoja logika pobierania danych
            data = {
                'kolumna1': ['wartość1', 'wartość2'],
                'kolumna2': ['wartość3', 'wartość4']
            }
            
            # WAŻNE: Zawsze zwracaj pandas DataFrame
            return pd.DataFrame(data)
            
        except Exception as e:
            # W przypadku błędu zwróć DataFrame z informacją o błędzie
            return pd.DataFrame({'error': [f'Błąd: {str(e)}']})
```

### 3. Wymagania dla metod

- **Każda metoda musi zwracać `pd.DataFrame`**
- Nie używaj parametrów w metodach (aplikacja ich nie obsługuje)
- Obsługuj błędy i zwracaj DataFrame z informacją o błędzie
- Unikaj metod prywatnych (zaczynających się od `_`)

### 4. Konfiguracja bezpieczeństwa

⚠️ **Ważne**: Nigdy nie umieszczaj tokenów API bezpośrednio w kodzie!

```python
import os
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe
load_dotenv()

class JiraEndpoint:
    def __init__(self):
        # Używaj zmiennych środowiskowych
        self.base_url = os.getenv('JIRA_BASE_URL')
        self.token = os.getenv('JIRA_API_TOKEN')
        self.username = os.getenv('JIRA_USERNAME')
```

Utwórz plik `.env` w głównym folderze:

```bash
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_API_TOKEN=your-api-token
JIRA_USERNAME=your-email@company.com

SONAR_BASE_URL=https://sonarcloud.io/api
SONAR_TOKEN=your-sonar-token

MEND_BASE_URL=https://saas.whitesourcesoftware.com/api
MEND_API_KEY=your-mend-api-key
MEND_USER_KEY=your-user-key
```

## Uruchomienie aplikacji

### 1. Podstawowe uruchomienie

```bash
python app.py
```

Aplikacja będzie dostępna pod adresem: `http://localhost:6789`

### 2. Konfiguracja dla produkcji

```bash
# Ustaw zmienne środowiskowe
export FLASK_ENV=production
export FLASK_DEBUG=False

# Uruchom z Gunicorn (zalecane dla produkcji)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Funkcjonalności aplikacji

### 1. Dynamiczne wczytywanie endpointów

- Aplikacja automatycznie skanuje folder `endpoint_files`
- Wykrywa klasy i metody w każdym pliku `.py`
- Tworzy listę rozwijaną z wszystkimi dostępnymi metodami

### 2. Wykonywanie metod

- Wybierz metodę z listy rozwijanej
- Kliknij "Check for Data"
- Aplikacja wykona metodę i wyświetli wyniki

### 3. Wyświetlanie wyników

- **DataFrame**: Wyświetlany jako tabela HTML z informacją o rozmiarze
- **Inne typy**: Wyświetlane jako tekst
- **Błędy**: Wyświetlane z pełnym traceback

### 4. Eksport danych

- Pobierz dane jako CSV
- Wyświetl dane w formacie JSON
- Skopiuj dane do schowka

### 5. Zarządzanie

- Przeładuj endpointy bez restartu aplikacji
- Statystyki użycia
- Monitorowanie błędów

## Troubleshooting

### Błąd: "Nie znaleziono metod"

1. Sprawdź czy folder `endpoint_files` istnieje
2. Upewnij się, że pliki `.py` zawierają klasy
3. Sprawdź czy metody nie są prywatne (nie zaczynają się od `_`)

### Błąd: "Moduł nie może być załadowany"

1. Sprawdź składnię Python w plikach endpointów
2. Upewnij się, że wszystkie importy są dostępne
3. Sprawdź logi w konsoli

### Błąd: "Metoda nie zwraca DataFrame"

1. Upewnij się, że metoda zwraca `pd.DataFrame`
2. Sprawdź czy nie ma błędów w logice metody
3. Dodaj obsługę błędów w metodzie

### Błąd połączenia z API

1. Sprawdź konfigurację tokenów API
2. Upewnij się, że tokeny są aktualne
3. Sprawdź połączenie internetowe
4. Sprawdź limity API

## Rozszerzanie funkcjonalności

### Dodanie nowego endpointu

1. Utwórz nowy plik w folderze `endpoint_files`
2. Zdefiniuj klasę z metodami
3. Uruchom aplikację - nowy endpoint pojawi się automatycznie

### Dodanie parametrów do metod

Jeśli potrzebujesz parametrów, możesz je dodać w konstruktorze klasy:

```python
class JiraEndpoint:
    def __init__(self, project_key=None):
        self.project_key = project_key or "DEFAULT"
    
    def get_issues(self):
        # Użyj self.project_key w metodzie
        pass
```

### Dodanie cache'owania

```python
import functools
import time

class JiraEndpoint:
    @functools.lru_cache(maxsize=128)
    def get_projects(self):
        # Metoda z cache'owaniem
        pass
```

## Bezpieczeństwo

### Środowisko produkcyjne

1. Użyj HTTPS
2. Skonfiguruj firewall
3. Ogranicz dostęp do aplikacji
4. Regularnie aktualizuj zależności

### Ochrona danych

1. Nie loguj wrażliwych danych
2. Używaj zmiennych środowiskowych dla konfiguracji
3. Zaszyfruj komunikację z API
4. Regularnie rotuj tokeny API

## Monitorowanie

### Logi aplikacji

```bash
# Uruchom z logowaniem
python app.py > app.log 2>&1

# Monitoruj logi w czasie rzeczywistym
tail -f app.log
```

### Metryki

Aplikacja zapisuje podstawowe metryki:
- Liczba wykonanych metod
- Liczba błędów
- Czas wykonania metod

## Wsparcie

W przypadku problemów:

1. Sprawdź logi aplikacji
2. Sprawdź konfigurację tokenów API
3. Upewnij się, że wszystkie zależności są zainstalowane
4. Sprawdź składnię plików endpointów

## Przykłady użycia

### Monitorowanie jakości kodu

```python
# sonarcloud.py
def get_quality_metrics(self):
    # Pobierz metryki z SonarCloud
    return pd.DataFrame(quality_data)
```

### Śledzenie problemów

```python
# jira.py
def get_open_bugs(self):
    # Pobierz otwarte bugi z Jira
    return pd.DataFrame(bugs_data)
```

### Analiza bezpieczeństwa

```python
# mend.py
def get_security_vulnerabilities(self):
    # Pobierz podatności z Mend
    return pd.DataFrame(vulnerabilities_data)
```