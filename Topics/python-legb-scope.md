# LEGB - Rodzaje zmiennych i zasięg w Pythonie

## Co to jest LEGB?

LEGB to akronim opisujący kolejność, w jakiej Python szuka zmiennych:
- **L** - Local (lokalne)
- **E** - Enclosing (zawierające)
- **G** - Global (globalne)
- **B** - Built-in (wbudowane)

Python szuka zmiennych w tej dokładnie kolejności!

## 1. Local (L) - Zasięg lokalny

Zmienne zdefiniowane wewnątrz funkcji:

```python
def my_function():
    x = 10  # Zmienna lokalna
    print(x)

my_function()  # 10
# print(x)  # NameError! x nie istnieje poza funkcją
```

```python
def example():
    local_var = "Jestem lokalna"
    
    def inner():
        inner_local = "Jestem jeszcze bardziej lokalna"
        print(local_var)      # Dostęp do zmiennej z wyższego poziomu
        print(inner_local)    # Dostęp do własnej zmiennej lokalnej
    
    inner()
    # print(inner_local)  # NameError! Nie ma dostępu

example()
```

## 2. Enclosing (E) - Zasięg zawierający

Zmienne z funkcji zewnętrznej (dla zagnieżdżonych funkcji):

```python
def outer_function():
    x = "outer"  # Enclosing scope dla inner_function
    
    def inner_function():
        print(x)  # Dostęp do zmiennej z enclosing scope
    
    inner_function()

outer_function()  # "outer"
```

### nonlocal - modyfikowanie zmiennych enclosing:

```python
def outer():
    count = 0  # Enclosing variable
    
    def inner():
        nonlocal count  # Bez tego byłby błąd przy count += 1
        count += 1
        print(f"Count: {count}")
    
    return inner

counter = outer()
counter()  # Count: 1
counter()  # Count: 2
counter()  # Count: 3
```

## 3. Global (G) - Zasięg globalny

Zmienne zdefiniowane na poziomie modułu:

```python
global_var = "Jestem globalna"  # Global scope

def function():
    print(global_var)  # Dostęp do zmiennej globalnej

function()  # "Jestem globalna"

def another_function():
    global_var = "Jestem lokalna"  # To jest NOWA zmienna lokalna!
    print(global_var)

another_function()  # "Jestem lokalna"
print(global_var)   # "Jestem globalna" - oryginał niezmieniony
```

### global - modyfikowanie zmiennych globalnych:

```python
counter = 0  # Global variable

def increment():
    global counter  # Bez tego byłby błąd
    counter += 1

def get_counter():
    return counter  # Odczyt bez 'global' działa

print(get_counter())  # 0
increment()
print(get_counter())  # 1
increment()
print(get_counter())  # 2
```

## 4. Built-in (B) - Zasięg wbudowany

Nazwy wbudowane w Python (funkcje, wyjątki, stałe):

```python
print(len([1, 2, 3]))    # len jest wbudowane
print(max([1, 2, 3]))    # max jest wbudowane
print(__name__)          # __name__ jest wbudowane

# Można je "przesłonić" (ale nie rób tego!):
len = 5
# print(len([1, 2, 3]))  # TypeError! len nie jest już funkcją

# Przywracanie:
del len
print(len([1, 2, 3]))    # Znów działa - 3
```

## Przykłady pokazujące LEGB w akcji:

### Przykład 1 - Wszystkie poziomy:
```python
x = "global"  # Global

def outer():
    x = "enclosing"  # Enclosing
    
    def inner():
        x = "local"  # Local
        print(f"Local: {x}")
        
        # Dostęp do różnych poziomów:
        def show_all():
            print(f"Built-in len: {len}")  # Built-in
            # Nie ma bezpośredniego dostępu do enclosing/global
            # gdy mamy lokalną zmienną o tej samej nazwie
        
        show_all()
    
    inner()
    print(f"Enclosing: {x}")

outer()
print(f"Global: {x}")

# Wynik:
# Local: local
# Built-in len: <built-in function len>
# Enclosing: enclosing
# Global: global
```

### Przykład 2 - Kolejność wyszukiwania:
```python
def demo():
    # Python szuka w kolejności L-E-G-B
    print(abs)    # Built-in function abs
    print(max)    # Built-in function max
    
    # Jeśli zdefiniujemy lokalnie:
    abs = "moja funkcja abs"
    print(abs)    # "moja funkcja abs" - Local przesłania Built-in

demo()
```

### Przykład 3 - Praktyczny przypadek:
```python
database_url = "prod://database"  # Global config

def create_connection():
    timeout = 30  # Local
    
    def connect_with_retry():
        retries = 3  # Local (w zagnieżdżonej funkcji)
        
        def attempt_connection():
            print(f"Łączenie z {database_url}")  # Global
            print(f"Timeout: {timeout}")         # Enclosing
            print(f"Próby: {retries}")          # Enclosing
            print(f"Używam len: {len}")         # Built-in
        
        for i in range(retries):
            attempt_connection()
    
    connect_with_retry()

create_connection()
```

## Częste pułapki i błędy:

### 1. Niechciane przesłanianie:
```python
# Złe - przesłaniamy wbudowaną funkcję
def bad_example():
    list = [1, 2, 3]  # Przesłaniamy built-in 'list'
    # list() nie działa już jako konstruktor!

# Dobre
def good_example():
    my_list = [1, 2, 3]  # Własna nazwa
    empty_list = list()  # list() nadal działa
```

### 2. Problem z pętlami i lambda:
```python
# Problem - wszystkie lambda używają tej samej zmiennej
functions = []
for i in range(3):
    functions.append(lambda: i)  # i jest z enclosing scope

for f in functions:
    print(f())  # 2, 2, 2 - wszystkie pokazują ostatnią wartość i

# Rozwiązanie - domyślny argument
functions = []
for i in range(3):
    functions.append(lambda x=i: x)  # x=i kopiuje wartość

for f in functions:
    print(f())  # 0, 1, 2 - poprawnie
```

### 3. Modyfikowanie w nieprawidłowy sposób:
```python
count = 0

def increment_wrong():
    count += 1  # UnboundLocalError!

def increment_right():
    global count
    count += 1

# increment_wrong()  # Błąd
increment_right()   # Działa
```

## Podsumowanie LEGB:

| Poziom | Opis | Słowo kluczowe | Przykład |
|--------|------|----------------|----------|
| **Local** | Wewnątrz funkcji | - | `def f(): x = 1` |
| **Enclosing** | Funkcja zewnętrzna | `nonlocal` | Zagnieżdżone funkcje |
| **Global** | Poziom modułu | `global` | `x = 1` na początku pliku |
| **Built-in** | Wbudowane w Python | - | `len`, `print`, `max` |

**Pamiętaj**: Python zawsze szuka w kolejności L → E → G → B i zatrzymuje się na pierwszym znalezieniu!