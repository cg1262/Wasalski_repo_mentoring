# Normalizacja baz danych - 1NF, 2NF, 3NF

## Co to jest normalizacja?

Normalizacja to proces organizowania danych w bazie danych w celu:
- **Eliminacji redundancji** (powtarzających się danych)
- **Zapewnienia spójności** danych
- **Ułatwienia aktualizacji** bez anomalii
- **Oszczędności przestrzeni** dyskowej

## 1NF - Pierwsza Forma Normalna

### Zasady 1NF:
1. **Każda kolumna zawiera wartości atomowe** (niepodzielne)
2. **Każda kolumna zawiera wartości tego samego typu**
3. **Każda kolumna ma unikalną nazwę**
4. **Kolejność wierszy nie ma znaczenia**

### Przykład PRZED 1NF (źle):
```sql
CREATE TABLE Students_BAD (
    student_id INT,
    name VARCHAR(100),
    subjects VARCHAR(200)  -- Wiele wartości w jednej kolumnie!
);

-- Dane:
-- 1, 'Jan Kowalski', 'Matematyka, Fizyka, Chemia'
-- 2, 'Anna Nowak', 'Historia, Geografia'
```

### Przykład PO 1NF (dobrze):
```sql
CREATE TABLE Students (
    student_id INT,
    name VARCHAR(100),
    subject VARCHAR(100)
);

-- Dane:
-- 1, 'Jan Kowalski', 'Matematyka'
-- 1, 'Jan Kowalski', 'Fizyka'
-- 1, 'Jan Kowalski', 'Chemia'
-- 2, 'Anna Nowak', 'Historia'
-- 2, 'Anna Nowak', 'Geografia'
```

## 2NF - Druga Forma Normalna

### Zasady 2NF:
1. **Musi być w 1NF**
2. **Wszystkie kolumny nie-kluczowe muszą być całkowicie zależne od całego klucza głównego**
3. **Eliminuje częściowe zależności**

### Przykład PRZED 2NF (źle):
```sql
CREATE TABLE Student_Subjects_BAD (
    student_id INT,
    subject_id INT,
    subject_name VARCHAR(100),    -- Zależy tylko od subject_id!
    teacher_name VARCHAR(100),    -- Zależy tylko od subject_id!
    grade INT,
    PRIMARY KEY (student_id, subject_id)
);

-- Problem: subject_name i teacher_name zależą tylko od subject_id,
-- nie od całego klucza (student_id, subject_id)
```

### Przykład PO 2NF (dobrze):
```sql
-- Tabela z przedmiotami
CREATE TABLE Subjects (
    subject_id INT PRIMARY KEY,
    subject_name VARCHAR(100),
    teacher_name VARCHAR(100)
);

-- Tabela z ocenami
CREATE TABLE Student_Grades (
    student_id INT,
    subject_id INT,
    grade INT,
    PRIMARY KEY (student_id, subject_id),
    FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id)
);
```

## 3NF - Trzecia Forma Normalna

### Zasady 3NF:
1. **Musi być w 2NF**
2. **Żadna kolumna nie-kluczowa nie może zależeć od innej kolumny nie-kluczowej**
3. **Eliminuje zależności przechodnie**

### Przykład PRZED 3NF (źle):
```sql
CREATE TABLE Students_BAD (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    department_name VARCHAR(100),  -- Zależy od department_id!
    department_head VARCHAR(100)   -- Zależy od department_id!
);

-- Problem: department_name i department_head zależą od department_id,
-- nie bezpośrednio od student_id (zależność przechodnia)
```

### Przykład PO 3NF (dobrze):
```sql
-- Tabela z wydziałami
CREATE TABLE Departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100),
    department_head VARCHAR(100)
);

-- Tabela ze studentami
CREATE TABLE Students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
);
```

## Praktyczny przykład - ewolucja schematu

### Krok 0 - Nienormalizowana tabela:
```sql
CREATE TABLE Orders_Unnormalized (
    order_id INT,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    customer_city VARCHAR(100),
    product_names VARCHAR(500),  -- 'Laptop, Mysz, Klawiatura'
    product_prices VARCHAR(200), -- '2500, 50, 150'
    order_total DECIMAL(10,2)
);
```

### Krok 1 - 1NF:
```sql
CREATE TABLE Orders_1NF (
    order_id INT,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    customer_city VARCHAR(100),
    product_name VARCHAR(100),
    product_price DECIMAL(10,2),
    order_total DECIMAL(10,2)
);
```

### Krok 2 - 2NF:
```sql
-- Tabela zamówień (informacje o kliencie)
CREATE TABLE Orders_2NF (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    customer_city VARCHAR(100),
    order_total DECIMAL(10,2)
);

-- Tabela pozycji zamówienia
CREATE TABLE Order_Items_2NF (
    order_id INT,
    product_name VARCHAR(100),
    product_price DECIMAL(10,2),
    PRIMARY KEY (order_id, product_name)
);
```

### Krok 3 - 3NF:
```sql
-- Tabela klientów
CREATE TABLE Customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    customer_city VARCHAR(100)
);

-- Tabela produktów
CREATE TABLE Products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    product_price DECIMAL(10,2)
);

-- Tabela zamówień
CREATE TABLE Orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    order_total DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

-- Tabela pozycji zamówienia
CREATE TABLE Order_Items (
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
```

## Zalety i wady normalizacji

### Zalety:
- ✅ **Eliminacja redundancji** - dane nie powtarzają się
- ✅ **Spójność danych** - łatwiej utrzymać integralność
- ✅ **Łatwiejsze aktualizacje** - zmiana w jednym miejscu
- ✅ **Oszczędność miejsca** - mniej powtarzających się danych
- ✅ **Elastyczność** - łatwiej dodawać nowe funkcje

### Wady:
- ❌ **Więcej tabel** - bardziej skomplikowana struktura
- ❌ **Więcej JOIN-ów** - zapytania mogą być wolniejsze
- ❌ **Skomplikowane zapytania** - trzeba łączyć wiele tabel

## Kiedy nie normalizować (denormalizacja)?

Czasami warto świadomie złamać zasady normalizacji dla:

### 1. **Wydajności**:
```sql
-- Denormalizacja dla szybszych raportów
CREATE TABLE Sales_Report (
    sale_id INT,
    product_name VARCHAR(100),  -- Powtarzalne, ale szybkie
    category_name VARCHAR(100), -- Powtarzalne, ale szybkie
    sale_amount DECIMAL(10,2),
    sale_date DATE
);
```

### 2. **Analityki**:
```sql
-- Tabela dla analiz - świadomie denormalizowana
CREATE TABLE Customer_Analytics (
    customer_id INT,
    customer_name VARCHAR(100),
    total_orders INT,
    total_spent DECIMAL(10,2),
    last_order_date DATE,
    favorite_category VARCHAR(100)
);
```

## Podsumowanie

| Forma | Eliminuje | Główna zasada |
|-------|-----------|---------------|
| **1NF** | Wartości nie-atomowe | Każda kolumna = jedna wartość |
| **2NF** | Częściowe zależności | Wszystko zależy od całego klucza |
| **3NF** | Zależności przechodnie | Kolumny nie zależą od siebie |

**Złota zasada**: Normalizuj do 3NF, a potem denormalizuj tylko tam, gdzie to naprawdę potrzebne dla wydajności!