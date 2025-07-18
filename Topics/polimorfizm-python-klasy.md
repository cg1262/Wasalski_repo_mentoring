# Polimorfizm w Pythonowych Klasach

## Co to jest polimorfizm?

**Polimorfizm** (z gr. "wiele form") to zdolność obiektów różnych klas do reagowania na te same operacje w różny sposób. W Pythonie polimorfizm oznacza, że możemy używać tej samej metody na różnych obiektach, a każdy z nich wykona ją po swojemu.

### Główne cechy polimorfizmu:
- 🔄 **Ta sama nazwa metody** - różne implementacje
- 🎭 **Różne zachowania** - w zależności od klasy
- 🔗 **Wspólny interfejs** - łatwość użycia
- 🚀 **Elastyczność** - łatwe dodawanie nowych typów

## Typy polimorfizmu w Pythonie

### 1. **Polimorfizm poprzez dziedziczenie**

```python
# Klasa bazowa
class Animal:
    def __init__(self, name):
        self.name = name
    
    def make_sound(self):
        pass  # Metoda będzie nadpisana w klasach pochodnych
    
    def info(self):
        return f"{self.name} is an animal"

# Klasy pochodne
class Dog(Animal):
    def make_sound(self):
        return f"{self.name} says Woof!"
    
    def fetch(self):
        return f"{self.name} is fetching a ball"

class Cat(Animal):
    def make_sound(self):
        return f"{self.name} says Meow!"
    
    def climb(self):
        return f"{self.name} is climbing a tree"

class Cow(Animal):
    def make_sound(self):
        return f"{self.name} says Moo!"

# Użycie polimorfizmu
animals = [
    Dog("Burek"),
    Cat("Mruczek"),
    Cow("Krówka")
]

# Ta sama metoda - różne zachowania
for animal in animals:
    print(animal.make_sound())
    print(animal.info())
    print("---")

# Wynik:
# Burek says Woof!
# Burek is an animal
# ---
# Mruczek says Meow!
# Mruczek is an animal
# ---
# Krówka says Moo!
# Krówka is an animal
```

### 2. **Duck Typing - "jeśli chodzi jak kaczka..."**

```python
# Różne klasy bez wspólnej klasy bazowej
class Duck:
    def fly(self):
        return "Duck flying high"
    
    def swim(self):
        return "Duck swimming in pond"

class Airplane:
    def fly(self):
        return "Airplane flying at 30,000 feet"

class Fish:
    def swim(self):
        return "Fish swimming in ocean"

class Submarine:
    def swim(self):
        return "Submarine diving deep"

# Funkcje korzystające z duck typing
def make_it_fly(flying_object):
    try:
        return flying_object.fly()
    except AttributeError:
        return f"{type(flying_object).__name__} can't fly"

def make_it_swim(swimming_object):
    try:
        return swimming_object.swim()
    except AttributeError:
        return f"{type(swimming_object).__name__} can't swim"

# Testowanie
objects = [Duck(), Airplane(), Fish(), Submarine()]

print("Flying test:")
for obj in objects:
    print(make_it_fly(obj))

print("\nSwimming test:")
for obj in objects:
    print(make_it_swim(obj))
```

### 3. **Polimorfizm z Abstract Base Classes (ABC)**

```python
from abc import ABC, abstractmethod

# Abstrakcyjna klasa bazowa
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass
    
    @abstractmethod
    def perimeter(self):
        pass
    
    def description(self):
        return f"I am a {self.__class__.__name__} with area {self.area():.2f}"

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14159 * self.radius ** 2
    
    def perimeter(self):
        return 2 * 3.14159 * self.radius

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
    
    def area(self):
        # Wzór Herona
        s = (self.a + self.b + self.c) / 2
        return (s * (s - self.a) * (s - self.b) * (s - self.c)) ** 0.5
    
    def perimeter(self):
        return self.a + self.b + self.c

# Funkcja wykorzystująca polimorfizm
def analyze_shapes(shapes):
    total_area = 0
    total_perimeter = 0
    
    print("Shape Analysis:")
    print("-" * 50)
    
    for shape in shapes:
        area = shape.area()
        perimeter = shape.perimeter()
        total_area += area
        total_perimeter += perimeter
        
        print(f"{shape.__class__.__name__}:")
        print(f"  Area: {area:.2f}")
        print(f"  Perimeter: {perimeter:.2f}")
        print(f"  Description: {shape.description()}")
        print()
    
    print(f"Total area: {total_area:.2f}")
    print(f"Total perimeter: {total_perimeter:.2f}")

# Testowanie
shapes = [
    Rectangle(5, 3),
    Circle(4),
    Triangle(3, 4, 5)
]

analyze_shapes(shapes)
```

## Polimorfizm z operatorami

### Magic Methods (Dunder Methods):

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        elif isinstance(other, (int, float)):
            return Vector(self.x + other, self.y + other)
        else:
            raise TypeError(f"Cannot add Vector and {type(other)}")
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other)
        elif isinstance(other, Vector):
            # Iloczyn skalarny
            return self.x * other.x + self.y * other.y
        else:
            raise TypeError(f"Cannot multiply Vector and {type(other)}")
    
    def __str__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __len__(self):
        return int((self.x ** 2 + self.y ** 2) ** 0.5)
    
    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return False

class Matrix:
    def __init__(self, data):
        self.data = data
    
    def __add__(self, other):
        if isinstance(other, Matrix):
            result = []
            for i in range(len(self.data)):
                row = []
                for j in range(len(self.data[i])):
                    row.append(self.data[i][j] + other.data[i][j])
                result.append(row)
            return Matrix(result)
        elif isinstance(other, (int, float)):
            result = []
            for row in self.data:
                new_row = [x + other for x in row]
                result.append(new_row)
            return Matrix(result)
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            result = []
            for row in self.data:
                new_row = [x * other for x in row]
                result.append(new_row)
            return Matrix(result)
    
    def __str__(self):
        return '\n'.join([' '.join(map(str, row)) for row in self.data])

# Polimorficzne operacje
def demonstrate_operations(obj1, obj2, scalar):
    print(f"Object 1: {obj1}")
    print(f"Object 2: {obj2}")
    print(f"Scalar: {scalar}")
    print()
    
    try:
        result_add = obj1 + obj2
        print(f"obj1 + obj2 = {result_add}")
    except:
        print("Addition with another object not supported")
    
    try:
        result_scalar_add = obj1 + scalar
        print(f"obj1 + scalar = {result_scalar_add}")
    except:
        print("Addition with scalar not supported")
    
    try:
        result_mul = obj1 * scalar
        print(f"obj1 * scalar = {result_mul}")
    except:
        print("Multiplication with scalar not supported")
    
    print("-" * 40)

# Testowanie
v1 = Vector(3, 4)
v2 = Vector(1, 2)
m1 = Matrix([[1, 2], [3, 4]])
m2 = Matrix([[5, 6], [7, 8]])

demonstrate_operations(v1, v2, 2)
demonstrate_operations(m1, m2, 3)
```

## Polimorfizm w kontekście interfejsów

### Przykład z różnymi źródłami danych:

```python
# Interfejs dla źródeł danych
class DataSource:
    def read_data(self):
        raise NotImplementedError("Subclass must implement read_data")
    
    def get_info(self):
        return f"Data source: {self.__class__.__name__}"

class FileDataSource(DataSource):
    def __init__(self, filename):
        self.filename = filename
    
    def read_data(self):
        return f"Reading data from file: {self.filename}"

class DatabaseDataSource(DataSource):
    def __init__(self, connection_string):
        self.connection_string = connection_string
    
    def read_data(self):
        return f"Reading data from database: {self.connection_string}"

class APIDataSource(DataSource):
    def __init__(self, url):
        self.url = url
    
    def read_data(self):
        return f"Reading data from API: {self.url}"

class CacheDataSource(DataSource):
    def __init__(self, cache_key):
        self.cache_key = cache_key
    
    def read_data(self):
        return f"Reading data from cache: {self.cache_key}"

# Processor korzystający z polimorfizmu
class DataProcessor:
    def __init__(self, data_sources):
        self.data_sources = data_sources
    
    def process_all_data(self):
        results = []
        
        print("Processing data from multiple sources:")
        print("=" * 50)
        
        for i, source in enumerate(self.data_sources, 1):
            print(f"{i}. {source.get_info()}")
            data = source.read_data()
            print(f"   {data}")
            results.append(data)
            print()
        
        return results
    
    def add_source(self, source):
        self.data_sources.append(source)

# Użycie
sources = [
    FileDataSource("data.csv"),
    DatabaseDataSource("postgresql://localhost:5432/mydb"),
    APIDataSource("https://api.example.com/data"),
    CacheDataSource("user_data_cache")
]

processor = DataProcessor(sources)
results = processor.process_all_data()

# Dodanie nowego źródła
processor.add_source(FileDataSource("backup.json"))
```

## Praktyczne przykłady zastosowań

### 1. **System płatności**:

```python
class PaymentProcessor:
    def process_payment(self, amount):
        raise NotImplementedError

class CreditCardProcessor(PaymentProcessor):
    def __init__(self, card_number):
        self.card_number = card_number
    
    def process_payment(self, amount):
        return f"Processing ${amount} via Credit Card ending in {self.card_number[-4:]}"

class PayPalProcessor(PaymentProcessor):
    def __init__(self, email):
        self.email = email
    
    def process_payment(self, amount):
        return f"Processing ${amount} via PayPal account {self.email}"

class BankTransferProcessor(PaymentProcessor):
    def __init__(self, account_number):
        self.account_number = account_number
    
    def process_payment(self, amount):
        return f"Processing ${amount} via Bank Transfer to {self.account_number}"

class OnlineStore:
    def checkout(self, payment_processor, amount):
        print("Processing your order...")
        result = payment_processor.process_payment(amount)
        print(result)
        print("Order completed successfully!")
        return True

# Użycie
store = OnlineStore()

# Różne metody płatności - ten sam interfejs
payment_methods = [
    CreditCardProcessor("1234-5678-9012-3456"),
    PayPalProcessor("user@example.com"),
    BankTransferProcessor("PL12345678901234567890")
]

amount = 99.99
for method in payment_methods:
    store.checkout(method, amount)
    print("-" * 40)
```

### 2. **System logowania**:

```python
import datetime

class Logger:
    def log(self, message, level="INFO"):
        raise NotImplementedError

class ConsoleLogger(Logger):
    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

class FileLogger(Logger):
    def __init__(self, filename):
        self.filename = filename
    
    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        # W rzeczywistości zapisywałoby do pliku
        print(f"Writing to {self.filename}: {log_entry.strip()}")

class DatabaseLogger(Logger):
    def __init__(self, table_name):
        self.table_name = table_name
    
    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # W rzeczywistości zapisywałoby do bazy danych
        print(f"INSERT INTO {self.table_name} (timestamp, level, message) "
              f"VALUES ('{timestamp}', '{level}', '{message}')")

class Application:
    def __init__(self, loggers):
        self.loggers = loggers
    
    def log_event(self, message, level="INFO"):
        for logger in self.loggers:
            logger.log(message, level)
    
    def run(self):
        self.log_event("Application started", "INFO")
        self.log_event("Processing user request", "DEBUG")
        self.log_event("Error occurred", "ERROR")
        self.log_event("Application finished", "INFO")

# Użycie
loggers = [
    ConsoleLogger(),
    FileLogger("app.log"),
    DatabaseLogger("logs")
]

app = Application(loggers)
app.run()
```

## Zalety i wady polimorfizmu

### ✅ **Zalety**:
- **Elastyczność** - łatwe dodawanie nowych typów
- **Czytelność** - jednolity interfejs
- **Maintainability** - łatwiejsze utrzymanie kodu
- **Reusability** - kod wielokrotnego użytku
- **Testability** - łatwiejsze testowanie

### ❌ **Wady**:
- **Complexity** - może skomplikować kod
- **Performance** - niewielki narzut wydajnościowy
- **Debugging** - trudniejsze debugowanie
- **Learning curve** - wymaga zrozumienia konceptów

## Najlepsze praktyki

### 1. **Używaj ABC gdy to możliwe**:
```python
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self):
        pass
```

### 2. **Implementuj \_\_str\_\_ i \_\_repr\_\_**:
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"
    
    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"
```

### 3. **Używaj type hints**:
```python
from typing import List, Protocol

class Drawable(Protocol):
    def draw(self) -> str:
        ...

def draw_all(shapes: List[Drawable]) -> None:
    for shape in shapes:
        print(shape.draw())
```

### 4. **Sprawdzaj typy gdy potrzeba**:
```python
def process_data(processor):
    if hasattr(processor, 'process') and callable(processor.process):
        return processor.process()
    else:
        raise TypeError("Object must have a callable 'process' method")
```

Polimorfizm to jedna z podstawowych zasad programowania obiektowego, która sprawia, że kod staje się bardziej elastyczny i łatwiejszy w utrzymaniu! 🚀

---

# 🇬🇧 ENGLISH VERSION

# Polymorphism in Python Classes

## What is polymorphism?

**Polymorphism** (from Greek "many forms") is the ability of objects from different classes to respond to the same operations in different ways. In Python, polymorphism means we can use the same method on different objects, and each will execute it in its own way.

### Main features of polymorphism:
- 🔄 **Same method name** - different implementations
- 🎭 **Different behaviors** - depending on the class
- 🔗 **Common interface** - ease of use
- 🚀 **Flexibility** - easy to add new types

## Types of polymorphism in Python

### 1. **Polymorphism through inheritance**

```python
# Base class
class Animal:
    def __init__(self, name):
        self.name = name
    
    def make_sound(self):
        pass  # Method will be overridden in derived classes
    
    def info(self):
        return f"{self.name} is an animal"

# Derived classes
class Dog(Animal):
    def make_sound(self):
        return f"{self.name} says Woof!"
    
    def fetch(self):
        return f"{self.name} is fetching a ball"

class Cat(Animal):
    def make_sound(self):
        return f"{self.name} says Meow!"
    
    def climb(self):
        return f"{self.name} is climbing a tree"

class Cow(Animal):
    def make_sound(self):
        return f"{self.name} says Moo!"

# Using polymorphism
animals = [
    Dog("Burek"),
    Cat("Mruczek"),
    Cow("Krówka")
]

# Same method - different behaviors
for animal in animals:
    print(animal.make_sound())
    print(animal.info())
    print("---")

# Output:
# Burek says Woof!
# Burek is an animal
# ---
# Mruczek says Meow!
# Mruczek is an animal
# ---
# Krówka says Moo!
# Krówka is an animal
```

### 2. **Duck Typing - "if it walks like a duck..."**

```python
# Different classes without common base class
class Duck:
    def fly(self):
        return "Duck flying high"
    
    def swim(self):
        return "Duck swimming in pond"

class Airplane:
    def fly(self):
        return "Airplane flying at 30,000 feet"

class Fish:
    def swim(self):
        return "Fish swimming in ocean"

class Submarine:
    def swim(self):
        return "Submarine diving deep"

# Functions using duck typing
def make_it_fly(flying_object):
    try:
        return flying_object.fly()
    except AttributeError:
        return f"{type(flying_object).__name__} can't fly"

def make_it_swim(swimming_object):
    try:
        return swimming_object.swim()
    except AttributeError:
        return f"{type(swimming_object).__name__} can't swim"

# Testing
objects = [Duck(), Airplane(), Fish(), Submarine()]

print("Flying test:")
for obj in objects:
    print(make_it_fly(obj))

print("\nSwimming test:")
for obj in objects:
    print(make_it_swim(obj))
```

### 3. **Polymorphism with Abstract Base Classes (ABC)**

```python
from abc import ABC, abstractmethod

# Abstract base class
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass
    
    @abstractmethod
    def perimeter(self):
        pass
    
    def description(self):
        return f"I am a {self.__class__.__name__} with area {self.area():.2f}"

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14159 * self.radius ** 2
    
    def perimeter(self):
        return 2 * 3.14159 * self.radius

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
    
    def area(self):
        # Heron's formula
        s = (self.a + self.b + self.c) / 2
        return (s * (s - self.a) * (s - self.b) * (s - self.c)) ** 0.5
    
    def perimeter(self):
        return self.a + self.b + self.c

# Function using polymorphism
def analyze_shapes(shapes):
    total_area = 0
    total_perimeter = 0
    
    print("Shape Analysis:")
    print("-" * 50)
    
    for shape in shapes:
        area = shape.area()
        perimeter = shape.perimeter()
        total_area += area
        total_perimeter += perimeter
        
        print(f"{shape.__class__.__name__}:")
        print(f"  Area: {area:.2f}")
        print(f"  Perimeter: {perimeter:.2f}")
        print(f"  Description: {shape.description()}")
        print()
    
    print(f"Total area: {total_area:.2f}")
    print(f"Total perimeter: {total_perimeter:.2f}")

# Testing
shapes = [
    Rectangle(5, 3),
    Circle(4),
    Triangle(3, 4, 5)
]

analyze_shapes(shapes)
```

## Polymorphism with operators

### Magic Methods (Dunder Methods):

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        elif isinstance(other, (int, float)):
            return Vector(self.x + other, self.y + other)
        else:
            raise TypeError(f"Cannot add Vector and {type(other)}")
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other)
        elif isinstance(other, Vector):
            # Dot product
            return self.x * other.x + self.y * other.y
        else:
            raise TypeError(f"Cannot multiply Vector and {type(other)}")
    
    def __str__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __len__(self):
        return int((self.x ** 2 + self.y ** 2) ** 0.5)
    
    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        return False

class Matrix:
    def __init__(self, data):
        self.data = data
    
    def __add__(self, other):
        if isinstance(other, Matrix):
            result = []
            for i in range(len(self.data)):
                row = []
                for j in range(len(self.data[i])):
                    row.append(self.data[i][j] + other.data[i][j])
                result.append(row)
            return Matrix(result)
        elif isinstance(other, (int, float)):
            result = []
            for row in self.data:
                new_row = [x + other for x in row]
                result.append(new_row)
            return Matrix(result)
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            result = []
            for row in self.data:
                new_row = [x * other for x in row]
                result.append(new_row)
            return Matrix(result)
    
    def __str__(self):
        return '\n'.join([' '.join(map(str, row)) for row in self.data])

# Polymorphic operations
def demonstrate_operations(obj1, obj2, scalar):
    print(f"Object 1: {obj1}")
    print(f"Object 2: {obj2}")
    print(f"Scalar: {scalar}")
    print()
    
    try:
        result_add = obj1 + obj2
        print(f"obj1 + obj2 = {result_add}")
    except:
        print("Addition with another object not supported")
    
    try:
        result_scalar_add = obj1 + scalar
        print(f"obj1 + scalar = {result_scalar_add}")
    except:
        print("Addition with scalar not supported")
    
    try:
        result_mul = obj1 * scalar
        print(f"obj1 * scalar = {result_mul}")
    except:
        print("Multiplication with scalar not supported")
    
    print("-" * 40)

# Testing
v1 = Vector(3, 4)
v2 = Vector(1, 2)
m1 = Matrix([[1, 2], [3, 4]])
m2 = Matrix([[5, 6], [7, 8]])

demonstrate_operations(v1, v2, 2)
demonstrate_operations(m1, m2, 3)
```

## Polymorphism in interface context

### Example with different data sources:

```python
# Interface for data sources
class DataSource:
    def read_data(self):
        raise NotImplementedError("Subclass must implement read_data")
    
    def get_info(self):
        return f"Data source: {self.__class__.__name__}"

class FileDataSource(DataSource):
    def __init__(self, filename):
        self.filename = filename
    
    def read_data(self):
        return f"Reading data from file: {self.filename}"

class DatabaseDataSource(DataSource):
    def __init__(self, connection_string):
        self.connection_string = connection_string
    
    def read_data(self):
        return f"Reading data from database: {self.connection_string}"

class APIDataSource(DataSource):
    def __init__(self, url):
        self.url = url
    
    def read_data(self):
        return f"Reading data from API: {self.url}"

class CacheDataSource(DataSource):
    def __init__(self, cache_key):
        self.cache_key = cache_key
    
    def read_data(self):
        return f"Reading data from cache: {self.cache_key}"

# Processor using polymorphism
class DataProcessor:
    def __init__(self, data_sources):
        self.data_sources = data_sources
    
    def process_all_data(self):
        results = []
        
        print("Processing data from multiple sources:")
        print("=" * 50)
        
        for i, source in enumerate(self.data_sources, 1):
            print(f"{i}. {source.get_info()}")
            data = source.read_data()
            print(f"   {data}")
            results.append(data)
            print()
        
        return results
    
    def add_source(self, source):
        self.data_sources.append(source)

# Usage
sources = [
    FileDataSource("data.csv"),
    DatabaseDataSource("postgresql://localhost:5432/mydb"),
    APIDataSource("https://api.example.com/data"),
    CacheDataSource("user_data_cache")
]

processor = DataProcessor(sources)
results = processor.process_all_data()

# Adding new source
processor.add_source(FileDataSource("backup.json"))
```

## Practical application examples

### 1. **Payment system**:

```python
class PaymentProcessor:
    def process_payment(self, amount):
        raise NotImplementedError

class CreditCardProcessor(PaymentProcessor):
    def __init__(self, card_number):
        self.card_number = card_number
    
    def process_payment(self, amount):
        return f"Processing ${amount} via Credit Card ending in {self.card_number[-4:]}"

class PayPalProcessor(PaymentProcessor):
    def __init__(self, email):
        self.email = email
    
    def process_payment(self, amount):
        return f"Processing ${amount} via PayPal account {self.email}"

class BankTransferProcessor(PaymentProcessor):
    def __init__(self, account_number):
        self.account_number = account_number
    
    def process_payment(self, amount):
        return f"Processing ${amount} via Bank Transfer to {self.account_number}"

class OnlineStore:
    def checkout(self, payment_processor, amount):
        print("Processing your order...")
        result = payment_processor.process_payment(amount)
        print(result)
        print("Order completed successfully!")
        return True

# Usage
store = OnlineStore()

# Different payment methods - same interface
payment_methods = [
    CreditCardProcessor("1234-5678-9012-3456"),
    PayPalProcessor("user@example.com"),
    BankTransferProcessor("PL12345678901234567890")
]

amount = 99.99
for method in payment_methods:
    store.checkout(method, amount)
    print("-" * 40)
```

### 2. **Logging system**:

```python
import datetime

class Logger:
    def log(self, message, level="INFO"):
        raise NotImplementedError

class ConsoleLogger(Logger):
    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

class FileLogger(Logger):
    def __init__(self, filename):
        self.filename = filename
    
    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        # In reality would write to file
        print(f"Writing to {self.filename}: {log_entry.strip()}")

class DatabaseLogger(Logger):
    def __init__(self, table_name):
        self.table_name = table_name
    
    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # In reality would write to database
        print(f"INSERT INTO {self.table_name} (timestamp, level, message) "
              f"VALUES ('{timestamp}', '{level}', '{message}')")

class Application:
    def __init__(self, loggers):
        self.loggers = loggers
    
    def log_event(self, message, level="INFO"):
        for logger in self.loggers:
            logger.log(message, level)
    
    def run(self):
        self.log_event("Application started", "INFO")
        self.log_event("Processing user request", "DEBUG")
        self.log_event("Error occurred", "ERROR")
        self.log_event("Application finished", "INFO")

# Usage
loggers = [
    ConsoleLogger(),
    FileLogger("app.log"),
    DatabaseLogger("logs")
]

app = Application(loggers)
app.run()
```

## Advantages and disadvantages of polymorphism

### ✅ **Advantages**:
- **Flexibility** - easy to add new types
- **Readability** - uniform interface
- **Maintainability** - easier code maintenance
- **Reusability** - reusable code
- **Testability** - easier testing

### ❌ **Disadvantages**:
- **Complexity** - can complicate code
- **Performance** - slight performance overhead
- **Debugging** - harder debugging
- **Learning curve** - requires understanding concepts

## Best practices

### 1. **Use ABC when possible**:
```python
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self):
        pass
```

### 2. **Implement \_\_str\_\_ and \_\_repr\_\_**:
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"
    
    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"
```

### 3. **Use type hints**:
```python
from typing import List, Protocol

class Drawable(Protocol):
    def draw(self) -> str:
        ...

def draw_all(shapes: List[Drawable]) -> None:
    for shape in shapes:
        print(shape.draw())
```

### 4. **Check types when needed**:
```python
def process_data(processor):
    if hasattr(processor, 'process') and callable(processor.process):
        return processor.process()
    else:
        raise TypeError("Object must have a callable 'process' method")
```

Polymorphism is one of the fundamental principles of object-oriented programming that makes code more flexible and easier to maintain! 🚀