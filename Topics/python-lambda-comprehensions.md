# Lambda, Dict i List Comprehension w Pythonie

## Lambda - funkcje anonimowe

### Co to jest lambda?
Lambda to sposób na tworzenie małych, jednolinijkowych funkcji bez użycia słowa kluczowego `def`.

### Składnia:
```python
lambda argumenty: wyrażenie
```

### Przykłady podstawowe:
```python
# Zwykła funkcja
def square(x):
    return x ** 2

# Ta sama funkcja jako lambda
square_lambda = lambda x: x ** 2

print(square_lambda(5))  # 25

# Lambda z wieloma argumentami
add = lambda x, y: x + y
print(add(3, 4))  # 7

# Lambda z warunkiem
max_val = lambda x, y: x if x > y else y
print(max_val(10, 5))  # 10
```

### Lambda z funkcjami wbudowanymi:
```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# map() - aplikuje funkcję do każdego elementu
squares = list(map(lambda x: x**2, numbers))
print(squares)  # [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# filter() - filtruje elementy
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4, 6, 8, 10]

# sorted() - sortowanie z kluczem
students = [('Anna', 85), ('Jan', 90), ('Maria', 78)]
sorted_by_grade = sorted(students, key=lambda student: student[1])
print(sorted_by_grade)  # [('Maria', 78), ('Anna', 85), ('Jan', 90)]
```

## List Comprehension - tworzenie list

### Składnia podstawowa:
```python
[wyrażenie for element in iterable]
[wyrażenie for element in iterable if warunek]
```

### Przykłady:
```python
# Podstawowa list comprehension
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers]
print(squares)  # [1, 4, 9, 16, 25]

# Z warunkiem
evens = [x for x in numbers if x % 2 == 0]
print(evens)  # [2, 4]

# Z transformacją i warunkiem
even_squares = [x**2 for x in numbers if x % 2 == 0]
print(even_squares)  # [4, 16]

# Zagnieżdżone pętle
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [num for row in matrix for num in row]
print(flattened)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Z funkcjami
words = ['hello', 'world', 'python']
lengths = [len(word) for word in words]
print(lengths)  # [5, 5, 6]
```

### Porównanie z tradycyjnym kodem:
```python
# Tradycyjny sposób
result = []
for x in range(10):
    if x % 2 == 0:
        result.append(x**2)

# List comprehension - krócej i czytelniej
result = [x**2 for x in range(10) if x % 2 == 0]
```

## Dict Comprehension - tworzenie słowników

### Składnia:
```python
{klucz: wartość for element in iterable}
{klucz: wartość for element in iterable if warunek}
```

### Przykłady:
```python
# Podstawowa dict comprehension
numbers = [1, 2, 3, 4, 5]
squares_dict = {x: x**2 for x in numbers}
print(squares_dict)  # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Z warunkiem
even_squares = {x: x**2 for x in numbers if x % 2 == 0}
print(even_squares)  # {2: 4, 4: 16}

# Z dwóch list
names = ['Anna', 'Jan', 'Maria']
ages = [25, 30, 28]
people = {name: age for name, age in zip(names, ages)}
print(people)  # {'Anna': 25, 'Jan': 30, 'Maria': 28}

# Odwracanie słownika
original = {'a': 1, 'b': 2, 'c': 3}
reversed_dict = {value: key for key, value in original.items()}
print(reversed_dict)  # {1: 'a', 2: 'b', 3: 'c'}

# Z funkcjami wbudowanymi
text = "hello world"
char_count = {char: text.count(char) for char in set(text) if char != ' '}
print(char_count)  # {'e': 1, 'h': 1, 'l': 3, 'o': 2, 'r': 1, 'd': 1, 'w': 1}
```

## Set Comprehension - bonus

```python
# Set comprehension - unikalne wartości
numbers = [1, 2, 2, 3, 3, 4, 5, 5]
unique_squares = {x**2 for x in numbers}
print(unique_squares)  # {1, 4, 9, 16, 25}
```

## Zagnieżdżone comprehensions

```python
# Lista list
matrix = [[i*j for j in range(1, 4)] for i in range(1, 4)]
print(matrix)  # [[1, 2, 3], [2, 4, 6], [3, 6, 9]]

# Dict z list comprehension jako wartości
groups = {
    'evens': [x for x in range(10) if x % 2 == 0],
    'odds': [x for x in range(10) if x % 2 == 1]
}
print(groups)  # {'evens': [0, 2, 4, 6, 8], 'odds': [1, 3, 5, 7, 9]}
```

## Kiedy używać której metody?

### Lambda - użyj gdy:
- ✅ Potrzebujesz prostej, jednolinijkowej funkcji
- ✅ Używasz map(), filter(), sorted()
- ✅ Funkcja jest używana tylko raz
- ❌ Unikaj dla skomplikowanej logiki

### List Comprehension - użyj gdy:
- ✅ Tworzysz nową listę na podstawie istniejącej
- ✅ Kod jest czytelny i nie za długi
- ✅ Potrzebujesz filtrowania lub transformacji
- ❌ Unikaj dla bardzo skomplikowanych operacji

### Dict Comprehension - użyj gdy:
- ✅ Tworzysz słownik z iterables
- ✅ Transformujesz istniejący słownik
- ✅ Łączysz klucze i wartości

## Przykłady praktyczne:

```python
# Analiza tekstu
text = "Python jest super"
analysis = {
    'words': text.split(),
    'word_lengths': [len(word) for word in text.split()],
    'char_freq': {char: text.lower().count(char) 
                  for char in set(text.lower()) if char.isalpha()}
}

# Przetwarzanie danych
data = [
    {'name': 'Anna', 'score': 85, 'subject': 'math'},
    {'name': 'Jan', 'score': 92, 'subject': 'math'},
    {'name': 'Maria', 'score': 78, 'subject': 'physics'}
]

# Filtrowanie i grupowanie
high_scores = [student for student in data if student['score'] > 80]
subjects = {student['subject'] for student in data}
avg_by_subject = {
    subject: sum(s['score'] for s in data if s['subject'] == subject) / 
             len([s for s in data if s['subject'] == subject])
    for subject in subjects
}
```