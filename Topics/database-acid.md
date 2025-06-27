# ACID - Właściwości transakcji w bazach danych

## Co to jest ACID?

ACID to akronim opisujący cztery kluczowe właściwości transakcji w bazach danych:
- **A** - Atomicity (Atomowość)
- **C** - Consistency (Spójność)
- **I** - Isolation (Izolacja)
- **D** - Durability (Trwałość)

Te właściwości gwarantują niezawodność i integralność danych podczas operacji na bazie danych.

## A - Atomicity (Atomowość)

### Definicja:
Transakcja jest **niepodzielna** - albo wykonuje się w całości, albo wcale.

### Przykład:
```sql
-- Transfer pieniędzy między kontami
BEGIN TRANSACTION;
    
    -- Krok 1: Odejmij z konta A
    UPDATE accounts SET balance = balance - 1000 WHERE account_id = 'A123';
    
    -- Krok 2: Dodaj do konta B
    UPDATE accounts SET balance = balance + 1000 WHERE account_id = 'B456';
    
    -- Jeśli cokolwiek się nie powiedzie, wszystko zostanie cofnięte
COMMIT;
```

### Co się dzieje gdy coś pójdzie nie tak:
```sql
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 1000 WHERE account_id = 'A123'; -- ✅ OK
    UPDATE accounts SET balance = balance + 1000 WHERE account_id = 'BŁĘDNE_ID'; -- ❌ BŁĄD
    -- Cała transakcja zostanie cofnięta (ROLLBACK)
    -- Konto A nadal ma pierwotną kwotę
```

### W praktyce:
- ✅ **Wszystkie operacje się udają** → COMMIT
- ❌ **Jakakolwiek operacja się nie udaje** → ROLLBACK
- 🚫 **Nie ma stanu pośredniego** - nie można wykonać "połowy" transakcji

## C - Consistency (Spójność)

### Definicja:
Baza danych przechodzi z jednego **poprawnego stanu** do drugiego **poprawnego stanu**.

### Przykład ograniczeń spójności:
```sql
-- Ograniczenia w bazie danych
CREATE TABLE accounts (
    account_id VARCHAR(10) PRIMARY KEY,
    balance DECIMAL(10,2) CHECK (balance >= 0), -- Saldo nie może być ujemne
    account_type VARCHAR(20) NOT NULL
);

-- Ta transakcja zostanie odrzucona:
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 2000 
    WHERE account_id = 'A123' AND balance = 1000; -- Saldo stałoby się -1000!
    -- Narusza CHECK constraint - transakcja zostanie cofnięta
ROLLBACK;
```

### Typy spójności:
```sql
-- 1. Ograniczenia domenowe
balance DECIMAL(10,2) CHECK (balance >= 0)

-- 2. Klucze obce
FOREIGN KEY (customer_id) REFERENCES customers(customer_id)

-- 3. Klucze unikalne
UNIQUE (email)

-- 4. Logika biznesowa
-- Np. suma wszystkich kont klienta musi być dodatnia
```

## I - Isolation (Izolacja)

### Definicja:
Równoczesne transakcje **nie wpływają na siebie wzajemnie** - każda działa jakby była jedyna.

### Problemy bez izolacji:

#### 1. **Dirty Read** (Brudny odczyt):
```sql
-- Transakcja 1:
BEGIN TRANSACTION;
UPDATE accounts SET balance = 5000 WHERE account_id = 'A123';
-- Nie ma jeszcze COMMIT!

-- Transakcja 2 (w tym samym czasie):
SELECT balance FROM accounts WHERE account_id = 'A123'; 
-- Może zobaczyć 5000 (uncommitted data) zamiast oryginalnej wartości

-- Transakcja 1:
ROLLBACK; -- Zmiany zostają cofnięte!
-- Transakcja 2 przeczytała dane, które nigdy nie były "prawdziwe"
```

#### 2. **Non-repeatable Read**:
```sql
-- Transakcja 1:
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE account_id = 'A123'; -- Wynik: 1000

-- Transakcja 2:
UPDATE accounts SET balance = 2000 WHERE account_id = 'A123';
COMMIT;

-- Transakcja 1 (kontynuacja):
SELECT balance FROM accounts WHERE account_id = 'A123'; -- Wynik: 2000
-- Ten sam SELECT dał inny wynik!
```

#### 3. **Phantom Read**:
```sql
-- Transakcja 1:
SELECT COUNT(*) FROM accounts WHERE balance > 1000; -- Wynik: 5

-- Transakcja 2:
INSERT INTO accounts VALUES ('C789', 1500);
COMMIT;

-- Transakcja 1:
SELECT COUNT(*) FROM accounts WHERE balance > 1000; -- Wynik: 6
-- "Pojawił się" nowy rekord!
```

### Poziomy izolacji:
```sql
-- 1. READ UNCOMMITTED - najsłabszy
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- 2. READ COMMITTED - standardowy
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 3. REPEATABLE READ - silniejszy
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- 4. SERIALIZABLE - najsilniejszy
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

## D - Durability (Trwałość)

### Definicja:
Po **COMMIT** dane są **permanentnie zapisane** i przetrwają awarie systemu.

### Jak baza danych zapewnia trwałość:

#### 1. **Write-Ahead Logging (WAL)**:
```
1. Zmiana zapisywana do logu transakcji (na dysku)
2. Dopiero potem zmiana w głównych plikach danych
3. Jeśli system padnie - odtworzenie z logu
```

#### 2. **Przykład odtwarzania**:
```sql
-- Log transakcji:
-- [START TRANSACTION T1]
-- [T1: UPDATE accounts SET balance=2000 WHERE id='A123']
-- [T1: UPDATE accounts SET balance=3000 WHERE id='B456']
-- [COMMIT T1]
-- [SYSTEM CRASH] ← System pada tutaj

-- Po restarcie baza danych:
-- 1. Czyta log transakcji
-- 2. Odtwarza wszystkie zatwierdzone transakcje
-- 3. Cofa wszystkie niezatwierdzone transakcje
```

## ACID w różnych bazach danych

### Pełne ACID (RDBMS):
- **PostgreSQL** ✅ Pełne ACID
- **MySQL (InnoDB)** ✅ Pełne ACID  
- **SQL Server** ✅ Pełne ACID
- **Oracle** ✅ Pełne ACID

### Ograniczone ACID (NoSQL):
- **MongoDB** ⚠️ ACID na poziomie dokumentu
- **Cassandra** ❌ Eventual consistency
- **Redis** ⚠️ ACID z pewnymi ograniczeniami

## Praktyczne przykłady

### E-commerce - składanie zamówienia:
```sql
BEGIN TRANSACTION;
    -- 1. Utwórz zamówienie
    INSERT INTO orders (order_id, customer_id, total) 
    VALUES (12345, 'CUST001', 299.99);
    
    -- 2. Dodaj pozycje
    INSERT INTO order_items (order_id, product_id, quantity, price)
    VALUES (12345, 'PROD001', 2, 149.99);
    
    -- 3. Zaktualizuj stan magazynowy
    UPDATE inventory SET quantity = quantity - 2 
    WHERE product_id = 'PROD001';
    
    -- 4. Sprawdź czy jest wystarczająco towaru
    SELECT quantity FROM inventory WHERE product_id = 'PROD001';
    -- Jeśli quantity < 0, to ROLLBACK
    
COMMIT;
-- Wszystkie kroki muszą się udać, inaczej zamówienie nie zostanie złożone
```

### System bankowy - przelew:
```sql
BEGIN TRANSACTION;
    -- Sprawdź saldo
    SELECT balance FROM accounts WHERE account_id = 'FROM_ACCOUNT' FOR UPDATE;
    
    -- Jeśli saldo wystarczające:
    UPDATE accounts SET balance = balance - 1000.00 
    WHERE account_id = 'FROM_ACCOUNT';
    
    UPDATE accounts SET balance = balance + 1000.00 
    WHERE account_id = 'TO_ACCOUNT';
    
    -- Zapisz historię
    INSERT INTO transactions (from_account, to_account, amount, timestamp)
    VALUES ('FROM_ACCOUNT', 'TO_ACCOUNT', 1000.00, NOW());
    
COMMIT;
```

## Kompromisy ACID

### Zalety:
- ✅ **Gwarancja integralności** danych
- ✅ **Przewidywalność** - wiesz co się dzieje
- ✅ **Niezawodność** - dane są bezpieczne
- ✅ **Zgodność** z logiką biznesową

### Wady:
- ❌ **Wydajność** - dodatkowe operacje zabezpieczające
- ❌ **Skalowanie** - trudniejsze w systemach rozproszonych
- ❌ **Blokowanie** - transakcje mogą się wzajemnie blokować
- ❌ **Złożoność** - więcej do zarządzania

## Podsumowanie

| Właściwość | Co gwarantuje | Przykład |
|------------|---------------|----------|
| **Atomicity** | Wszystko albo nic | Przelew: odejm + dodaj razem |
| **Consistency** | Spójne reguły biznesowe | Saldo >= 0 |
| **Isolation** | Transakcje nie kolidują | Równoczesne przelewy |
| **Durability** | Dane przetrwają awarie | Restart serwera |

**ACID = niezawodność kosztem wydajności**
**NoSQL = wydajność kosztem niezawodności**

Wybierz zgodnie z potrzebami swojej aplikacji!