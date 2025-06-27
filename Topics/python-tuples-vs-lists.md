# Tuple vs Lista w Pythonie - szybkość i zagnieżdżanie

## Czy tuple są szybsze od list?

### TAK - tuple są szybsze w większości przypadków:

#### 1. **Tworzenie**
```python
import timeit

# Tuple - szybsze tworzenie
timeit.timeit("(1, 2, 3, 4, 5)", number=1000000)
# ~0.02 sekundy

# Lista - wolniejsze tworzenie
timeit.timeit("[1, 2, 3, 4, 5]", number=1000000)
# ~0.15 sekundy
```

#### 2. **Dostęp do elementów**
```python
tuple_data = (1, 2, 3, 4, 5)
list_data = [1, 2, 3, 4, 5]

# Tuple - szybszy dostęp
timeit.timeit("tuple_data[2]", globals=globals(), number=1000000)

# Lista - wolniejszy dostęp
timeit.timeit("list_data[2]", globals=globals(), number=1000000)
```

#### 3. **Iteracja**
```python
# Tuple - szybsza iteracja
for item in tuple_data:
    pass

# Lista - wolniejsza iteracja
for item in list_data:
    pass
```

### Dlaczego tuple są szybsze?
- **Immutable**: Nie można ich modyfikować, więc Python może je zoptymalizować
- **Mniej overhead**: Mniejsze zużycie pamięci
- **Hashable**: Mogą być kluczami w słownikach
- **Stała wielkość**: Python wie, ile pamięci przydzielić

## Czy tuple mogą być zagnieżdżone?

### TAK - tuple mogą być zagnieżdżone:

```python
# Zagnieżdżone tuple
nested_tuple = ((1, 2), (3, 4), (5, 6))
print(nested_tuple[0])        # (1, 2)
print(nested_tuple[0][1])     # 2

# Mieszane zagnieżdzanie
mixed_tuple = (1, [2, 3], (4, 5), {"key": "value"})
print(mixed_tuple[1])         # [2, 3]
print(mixed_tuple[2])         # (4, 5)

# Głębokie zagnieżdzanie
deep_tuple = (((1, 2), (3, 4)), ((5, 6), (7, 8)))
print(deep_tuple[0][1][0])    # 3
```

### Ważne uwagi o zagnieżdżonych tuple:
```python
# Tuple jest immutable, ale jego elementy mogą być mutable
tuple_with_list = ([1, 2], [3, 4])
tuple_with_list[0].append(5)  # To działa!
print(tuple_with_list)        # ([1, 2, 5], [3, 4])

# Ale nie można zmienić samego tuple
# tuple_with_list[0] = [9, 9]  # TypeError!
```

## Kiedy używać tuple, a kiedy list?

### Używaj **tuple** gdy:
- ✅ Dane są niezmienne (np. współrzędne, konfiguracja)
- ✅ Potrzebujesz klucza do słownika
- ✅ Zwracasz wiele wartości z funkcji
- ✅ Wydajność jest kluczowa
- ✅ Dane mają stałą strukturę

```python
# Dobre przykłady użycia tuple
coordinates = (10.5, 20.3)
rgb_color = (255, 128, 0)
database_record = ("Jan", "Kowalski", 30, "Warszawa")
return name, age, city  # Multiple return values
```

### Używaj **list** gdy:
- ✅ Musisz dodawać/usuwać elementy
- ✅ Kolejność może się zmieniać
- ✅ Potrzebujesz metod jak append(), remove()
- ✅ Rozmiar kolekcji jest dynamiczny

```python
# Dobre przykłady użycia list
shopping_list = ["mleko", "chleb", "masło"]
shopping_list.append("jajka")

numbers = [1, 2, 3]
numbers.extend([4, 5, 6])
```

## Podsumowanie wydajności:
| Operacja | Tuple | Lista | Zwycięzca |
|----------|-------|-------|-----------|
| Tworzenie | Szybkie | Wolne | Tuple |
| Dostęp | Szybki | Średni | Tuple |
| Iteracja | Szybka | Średnia | Tuple |
| Dodawanie | Niemożliwe | Szybkie | Lista |
| Usuwanie | Niemożliwe | Szybkie | Lista |
| Pamięć | Mniej | Więcej | Tuple |