# Finance Tracker - Historia Zmian

## Przegląd
Ten dokument opisuje kompletną historię rozwoju aplikacji Finance Tracker od podstawowej wersji do zaawansowanego systemu planowania finansowego z funkcjami miesiącowego śledzenia, leasingu i oszczędności.

## Wersja 1.0 - Podstawowa funkcjonalność
**Data:** Początkowa implementacja

### Funkcje
- Podstawowe dodawanie wydatków i przychodów
- Prosta tabela wydatków z kategoryzacją
- Podstawowe podsumowanie finansowe
- Obsługa powtarzalnych transakcji
- Kalkulacja podatków dla przychodów

### Struktura bazy danych
- `expenses` - podstawowe wydatki
- `income` - przychody z opcjonalną kalkulacją godzinową
- `recurring_transactions` - powtarzalne transakcje

---

## Wersja 2.0 - System planowania Excel-like
**Data:** Pierwsza duża aktualizacja

### Nowe funkcje
#### 1. Zarządzanie leasingiem
- Dodanie tabeli `leases` do śledzenia rat leasingowych
- Automatyczne obliczanie pozostałych rat
- Śledzenie dat płatności i automatyczne aktualizacje
- Integracja z miesięcznymi projekcjami

#### 2. Planowane wydatki roczne
- Tabela `yearly_planned` dla zaplanowanych wydatków
- Możliwość oznaczania jako opłacone
- Automatyczne przenoszenie do wydatków rzeczywistych
- Integracja z kalkulacjami miesięcznymi

#### 3. Projekcje miesięczne z przenoszeniem salda
- Tabela `monthly_projections` z automatycznym przenoszeniem
- Kalkulacja przeniesienia z poprzedniego miesiąca
- Automatyczne uwzględnianie rat leasingowych i wydatków planowanych
- System oszczędności z transferami

#### 4. Konto oszczędnościowe
- Tabela `savings_account` do śledzenia oszczędności
- Obsługa wpłat i wypłat
- Integracja z projekcjami miesięcznymi

### Nowe strony
- `/leases` - zarządzanie ratami leasingowymi
- `/yearly_planned` - planowane wydatki roczne
- `/projections` - projekcje miesięczne z przenoszeniem salda
- `/savings` - konto oszczędnościowe

### Algorytmy
- **Automatyczne kalkulacje leasingu:** System sprawdza aktywne leasingi dla każdego miesiąca projekcji
- **Przenoszenie salda:** Automatyczne obliczanie przeniesienia między miesiącami
- **Integracja planowanych wydatków:** Automatyczne uwzględnianie w projekcjach

---

## Wersja 3.0 - Szczegółowe widoki miesięczne
**Data:** Druga duża aktualizacja

### Nowe funkcje
#### 1. Strony szczegółów miesięcy
- Nowa strona `/month/<year>/<month>` dla każdego miesiąca
- Szczegółowe tabele przychodów i wydatków w stylu Excel
- Oddzielne sekcje dla rzeczywistych i planowanych transakcji

#### 2. Zaawansowane wyświetlanie wydatków
- Rzeczywiste wydatki (kolor zielony - opłacone)
- Planowane raty leasingowe (kolor żółty - do opłacenia)
- Planowane wydatki roczne (kolor niebieski - zaplanowane)
- Możliwość opłacania bezpośrednio z widoku miesiąca

#### 3. Nawigacja między miesiącami
- Przycisk poprzedni/następny miesiąc
- Dropdown w navbar z wszystkimi miesiącami
- Link do projekcji z każdego miesiąca

#### 4. Karty podsumowujące
- Przychody faktyczne
- Wydatki faktyczne  
- Przeniesienie z poprzedniego miesiąca
- Saldo końcowe z kolorowym kodowaniem

### Nowe endpointy
- `add_month_income(year, month)` - dodawanie przychodów z miesiąca
- `add_month_expense(year, month)` - dodawanie wydatków z miesiąca
- `pay_lease_from_month()` - opłacanie raty z widoku miesiąca

### Ulepszona nawigacja
- Dropdown "Miesiące" w navbar
- Automatyczne przekierowania do bieżącego miesiąca
- Breadcrumb navigation między stronami

---

## Wersja 4.0 - Dark Mode
**Data:** Trzecia aktualizacja

### Nowe funkcje
#### 1. Kompletny dark mode
- CSS custom properties dla dynamicznego przełączania
- Toggle switch w navbar z ikonami słońca/księżyca
- Animowane przejścia między trybami

#### 2. Inteligentne zarządzanie motywem
- LocalStorage do zapamiętywania preferencji
- Automatyczne wykrywanie motywu systemowego
- Powiadomienia o zmianie motywu

#### 3. Kompleksowe style dark mode
- Wszystkie komponenty Bootstrap dostosowane
- Dropdowns, modals, formularze
- Tabele, karty, badges
- Custom scrollbar dla webkit

### Zmiany techniczne
- Nowe CSS custom properties w `:root`
- Selektor `[data-theme="dark"]` dla wszystkich komponentów
- JavaScript do zarządzania stanem motywu
- Animacje i notyfikacje

---

## Wersja 5.0 - Unifikacja kalkulacji godzinowych
**Data:** Najnowsza aktualizacja

### Problem
Użytkownik zauważył brak opcji kalkulacji godzinowej w formularzach miesięcznych w porównaniu do głównego formularza dodawania przychodów.

### Rozwiązanie
#### 1. Rozszerzenie formularza miesięcznego przychodu
- Dodanie radio buttonów: "Stała kwota" vs "Oblicz na podstawie godzin i stawki"
- Pełna sekcja kalkulacji godzinowej z polami:
  - Liczba godzin
  - Stawka za godzinę
  - Stawka VAT (domyślnie 23%)
  - Podatek (domyślnie 12%)

#### 2. Podgląd kalkulacji w czasie rzeczywistym
- Karta z podglądem obliczeń:
  - Kwota brutto (godziny × stawka)
  - VAT (kwota brutto × stawka VAT)
  - Kwota z VAT (brutto + VAT)
  - Podatek (brutto × stawka podatku)
  - Kwota netto (brutto - podatek)

#### 3. Walidacja formularza
- Sprawdzanie wymaganych pól w zależności od trybu
- Alerty przy brakujących danych
- Automatyczne przełączanie między trybami

#### 4. Zgodność z backendem
- Route `add_month_income` obsługuje oba tryby
- Identyczne obliczenia jak w głównym formularzu
- Zachowanie szczegółów godzinowych w bazie danych

#### 5. Wyświetlanie w tabeli miesiąca
- Tooltips z pełnym breakdown kalkulacji
- Badge indicators dla różnych typów przychodów
- Wyświetlanie stawek VAT i podatku

### Rezultat
**Pełna paryteta funkcjonalna** między głównym formularzem dodawania przychodów a formularzami miesięcznymi. Użytkownicy mogą teraz używać wszystkich funkcji kalkulacji godzinowej bezpośrednio z widoków miesięcznych.

---

## Struktura końcowa bazy danych

### Tabele główne
- `expenses` - wydatki rzeczywiste
- `income` - przychody z opcjonalną kalkulacją godzinową
- `recurring_transactions` - powtarzalne transakcje

### Tabele planowania
- `leases` - raty leasingowe z automatycznym śledzeniem
- `yearly_planned` - planowane wydatki roczne
- `monthly_projections` - projekcje miesięczne z przenoszeniem
- `savings_account` - konto oszczędnościowe

### Kluczowe pola
- **Income:** `hours`, `hourly_rate`, `vat_rate`, `tax_rate` dla kalkulacji godzinowych
- **Leases:** `total_installments`, `installments_paid`, `next_payment_date`
- **Monthly projections:** `carryover_from_previous`, `savings_transfer`
- **Yearly planned:** `is_paid`, `planned_date`

---

## Funkcje kluczowe aplikacji

### 1. Automatyczne kalkulacje
- **Przenoszenie salda:** Automatyczne obliczanie przeniesienia między miesiącami
- **Raty leasingowe:** Automatyczne uwzględnianie aktywnych leasingów w projekcjach
- **Wydatki planowane:** Automatyczne dodawanie do odpowiednich miesięcy

### 2. Zaawansowane UI/UX
- **Dark mode** z pełną obsługą wszystkich komponentów
- **Responsywny design** z Bootstrap 5
- **Intuicyjna nawigacja** z dropdowns i breadcrumbs
- **Real-time calculations** w formularzach

### 3. Integracja danych
- **Excel-like experience** z szczegółowymi tabelami miesięcznymi
- **Comprehensive reporting** z kartami podsumowującymi
- **Flexible income entry** z opcjami godzinowymi i stałymi kwotami

### 4. System planowania
- **Long-term lease tracking** z automatycznymi obliczeniami
- **Yearly expense planning** z integracją miesięczną
- **Savings management** z transferami i śledzeniem salda

---

## Wnioski techniczne

### Architektura
- **Flask** backend z SQLite bazą danych
- **Bootstrap 5** frontend z custom CSS
- **JavaScript** do dynamicznych interakcji
- **SQLAlchemy-style** raw SQL queries

### Najlepsze praktyki
- **CSS Custom Properties** dla łatwego theming
- **LocalStorage** do persistent user preferences  
- **Form validation** na frontend i backend
- **Responsive design** dla wszystkich urządzeń

### Skalowalność
- **Modular route structure** łatwa do rozszerzania
- **Flexible database schema** z miejscem na nowe funkcje
- **Component-based CSS** z reusable styles
- **API-ready calculations** z JSON endpoints

---

*Dokument utworzony: Lipiec 2025*
*Ostatnia aktualizacja: Po implementacji kalkulacji godzinowych w formularzach miesięcznych*