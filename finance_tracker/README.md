# Finance Tracker

Aplikacja webowa do śledzenia wydatków i przychodów napisana w Pythonie z Flask.

## Funkcjonalności

- ✅ **Dodawanie wydatków** - możliwość wpisania przyszłych wydatków
- ✅ **Wydatki powtarzalne** - możliwość zaznaczenia przez ile miesięcy wydatek będzie powtarzany
- ✅ **Dodawanie przychodów** - możliwość wpisania przyszłych przychodów
- ✅ **Kalkulacja godzinowa** - obliczanie przychodów na podstawie godzin × stawka + VAT
- ✅ **Obliczanie podatków** - automatyczne wyliczanie 12% podatku z przychodów
- ✅ **Podsumowanie finansowe** - szczegółowe zestawienie przychodów, wydatków i salda
- ✅ **Responsywny interfejs** - działa na komputerach i urządzeniach mobilnych

## Instalacja

1. Zainstaluj wymagane biblioteki:
```bash
pip install -r requirements.txt
```

2. Uruchom aplikację:
```bash
python app.py
```

3. Otwórz przeglądarkę i przejdź do `http://localhost:5000`

## Użycie na serwerze NAS

Aplikacja została zaprojektowana tak, aby działać z jednego folderu. Wszystkie pliki (kod HTML, baza danych SQLite, pliki CSS/JS) znajdują się w tym samym katalogu.

Aby uruchomić na serwerze NAS:

1. Skopiuj cały folder `finance_tracker` na serwer NAS
2. Zainstaluj Python i Flask na serwerze
3. Uruchom: `python app.py`
4. Aplikacja będzie dostępna pod adresem `http://[IP_SERWERA]:5000`

## Struktura bazy danych

Aplikacja używa SQLite z trzema tabelami:

- **expenses** - wydatki (zwykłe i powtarzalne)
- **income** - przychody (z możliwością kalkulacji godzinowej)
- **recurring_transactions** - przyszłe transakcje powtarzalne

## Bezpieczeństwo

- Zmień `secret_key` w pliku `app.py` na własny
- Dla produkcji rozważ użycie bardziej zaawansowanej bazy danych
- Dodaj uwierzytelnianie użytkowników jeśli potrzebne

## Funkcje specjalne

### Kalkulacja godzinowa
Możliwość obliczania przychodów według wzoru:
```
Kwota brutto = godziny × stawka
VAT = kwota brutto × 23%
Kwota z VAT = kwota brutto + VAT
Podatek = kwota brutto × 12%
Kwota netto = kwota brutto - podatek
```

### Wydatki powtarzalne
System automatycznie tworzy wpisy dla kolejnych miesięcy na podstawie ustawionej liczby powtórzeń.

### Podsumowanie finansowe
Szczegółowe zestawienie z:
- Wskaźnikami finansowymi
- Obliczeniami podatków
- Saldem końcowym
- Wykresami progress bar