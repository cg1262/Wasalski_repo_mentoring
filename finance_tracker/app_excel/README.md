# Finance Tracker Excel - Wersja bazująca na arkuszach Excel

Aplikacja webowa replikująca funkcjonalność arkuszy Excel do zarządzania finansami osobistymi z automatycznymi obliczeniami przeniesienia między miesiącami, śledzeniem leasingu i planowaniem rocznym.

## 🎯 Główne funkcje

### Excel-like Interface
- **Panel kontrolny** - główne ustawienia finansowe (jak komórki Excel)
- **Widoki miesięczne** - każdy miesiąc jako osobna karta (jak zakładki Excel)
- **Automatyczne obliczenia** - przeniesienie salda między miesiącami
- **Kolorowe kategorie** - wizualne kodowanie jak w Excel

### Zarządzanie finansami
- **Przychody z kalkulacją godzinową** - stawka × godziny + VAT
- **Wydatki kategoryzowane** - z możliwością powtarzania
- **Leasing** - automatyczne śledzenie rat z postępem
- **Planowane wydatki roczne** - rozkład na odpowiednie miesiące
- **Konto oszczędnościowe** - wpłaty/wypłaty z historią

### Automatyzacja
- **Carryover** - automatyczne przenoszenie salda między miesiącami
- **Integracja leasingu** - raty automatycznie w budżecie miesięcznym
- **Planowanie roczne** - wydatki pojawiają się w docelowych miesiącach

## 🚀 Instalacja i uruchomienie

### Wymagania
- Python 3.7+
- Flask 2.3.3

### Kroki instalacji
```bash
# Przejdź do folderu aplikacji
cd app_excel

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom aplikację
python app.py
```

Aplikacja będzie dostępna pod adresem: `http://localhost:9877`

## 📊 Struktura aplikacji

### Główne moduły
- **Panel główny** (`/`) - przegląd finansów w stylu Excel
- **Panel kontrolny** (`/control_panel`) - ustawienia podstawowe
- **Miesiące** (`/month/rok/miesiąc`) - szczegółowe widoki miesięczne
- **Leasing** (`/leasing`) - zarządzanie ratami
- **Planowane roczne** (`/yearly_planned`) - wydatki planowane
- **Oszczędności** (`/savings`) - konto oszczędnościowe

### Baza danych (SQLite)

#### Tabele główne:
- `control_panel` - ustawienia podstawowe (przychód, stawka, VAT)
- `monthly_data` - dane miesięczne z przenoszeniem
- `monthly_expenses` - wydatki miesięczne z kategoriami

#### Tabele planowania:
- `leasing` - śledzenie rat leasingowych
- `yearly_planned_expenses` - planowane wydatki roczne
- `savings_transactions` - transakcje oszczędnościowe
- `expense_categories` - kategorie z kolorami

## 🎨 Excel-like Features

### Wygląd i zachowanie
- **Kolory kategorii**: Czerwony (leasing), Pomarańczowy (wydatki), Żółty (VAT)
- **Tabele z ramkami** - jak komórki Excel
- **Podgląd obliczeń** - formuly widoczne dla użytkownika
- **Skróty klawiszowe** - Ctrl+N, Ctrl+S, Escape, F1

### Obliczenia automatyczne
```
Zostaje na następny = Przeniesienie + Przychód - Wydatki
Przychód brutto = Godziny × Stawka
VAT = Przychód brutto × 23%
```

### Funkcje Excel-like
- **Auto-save** - automatyczny zapis szkiców
- **Real-time calculations** - obliczenia na bieżąco
- **Progress tracking** - postęp spłat jak paski postępu
- **Color coding** - kategoryzacja kolorami

## ⌨️ Skróty klawiszowe

- `Ctrl + N` - Nowy wydatek/transakcja
- `Ctrl + S` - Zapisz formularz
- `Escape` - Powrót do poprzedniego widoku
- `F1` - Pomoc/wyświetl formuły
- `Tab` - Przejście do następnego pola
- `Enter` - Zatwierdź formularz

## 📈 Logika finansowa

### Przeniesienie między miesiącami
Jak w Excel - każdy miesiąc automatycznie otrzymuje resztę z poprzedniego miesiąca:
```
Miesiąc N: Zostaje = Przychód + Przeniesienie - Wydatki
Miesiąc N+1: Przeniesienie = Zostaje z miesiąca N
```

### Automatyczna integracja wydatków
- **Leasing**: Raty automatycznie pojawiają się w miesięcznych budżetach
- **Planowane roczne**: Wydatki dodawane do odpowiednich miesięcy
- **Kategorie**: Automatyczne kolorowanie i grupowanie

### Kalkulacje w czasie rzeczywistym
- Podgląd obliczeń podczas wprowadzania danych
- Automatyczne aktualizacje sum i sald
- Formuły widoczne dla przejrzystości

## 🔧 Konfiguracja

### Panel kontrolny
- **Przychód miesięczny netto** - docelowy przychód po podatkach
- **Godziny miesięczne** - planowana liczba godzin pracy
- **Stawka godzinowa** - stawka brutto za godzinę
- **VAT** - stawka VAT (domyślnie 23%)

### Kategorie wydatków
- **Leasing** (czerwony) - raty i zobowiązania
- **Żywność/Transport/Rozrywka** (pomarańczowy) - wydatki stałe
- **VAT** (żółty) - podatki i opłaty
- **Inne** (szary) - pozostałe wydatki

## 📱 Responsywność

Aplikacja jest responsywna i działa na:
- **Desktop** - pełna funkcjonalność Excel-like
- **Tablet** - adaptowane tabele i formularze
- **Mobile** - uproszczony interfejs z zachowaniem funkcji

## 🔒 Bezpieczeństwo

- **Single-user** - aplikacja dla jednego użytkownika (jak Excel)
- **Local database** - dane przechowywane lokalnie w SQLite
- **Form validation** - walidacja danych po stronie klienta i serwera
- **No external dependencies** - brak połączeń z zewnętrznymi API

## 📝 Przykłady użycia

### 1. Ustawienie podstawowych parametrów
1. Przejdź do Panel kontrolny
2. Ustaw przychód miesięczny netto (np. 10000 zł)
3. Ustaw liczbę godzin (np. 160h)
4. Ustaw stawkę godzinową (np. 80 zł/h)

### 2. Dodanie leasingu samochodu
1. Przejdź do Leasing
2. Dodaj nowy leasing (np. Toyota, 1200 zł/miesiąc, 36 rat)
3. Rata automatycznie pojawi się we wszystkich miesięcznych budżetach

### 3. Planowanie wydatku rocznego
1. Przejdź do Planowane roczne
2. Dodaj wydatek (np. Ubezpieczenie, 2400 zł, Marzec 2025)
3. Wydatek automatycznie pojawi się w budżecie marcowym

### 4. Śledzenie miesięczne
1. Przejdź do konkretnego miesiąca
2. Dodawaj rzeczywiste wydatki w kategoriach
3. Obserwuj automatyczne przeliczanie salda

## 🛠️ Rozwój i customizacja

### Dodawanie nowych kategorii
Edytuj tabelę `expense_categories` w bazie danych:
```sql
INSERT INTO expense_categories (name, color_code, sort_order) 
VALUES ('Nowa kategoria', 'blue', 10);
```

### Zmiana kolorów
Modyfikuj zmienne CSS w `templates/base.html`:
```css
--excel-green: #107c41;
--excel-orange: #ff6b35;
--excel-red: #c5504b;
```

### Dodawanie nowych obliczeń
Rozszerz funkcję `update_monthly_totals()` w `app.py`.

## 📞 Wsparcie

W przypadku problemów:
1. Sprawdź logi aplikacji w konsoli
2. Usuń bazę danych (`finance_tracker_excel.db`) dla świeżego startu
3. Sprawdź czy port 9877 nie jest zajęty

## 📄 Licencja

Aplikacja stworzona dla użytku osobistego. Bazuje na opensource Flask i Bootstrap.