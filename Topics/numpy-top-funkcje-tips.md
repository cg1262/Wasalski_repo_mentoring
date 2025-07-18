# Top 20-30 Funkcji w NumPy + Tips and Tricks

## Podstawowe operacje na arrays

### 1. **np.array() - tworzenie tablic**
```python
import numpy as np

# Podstawowe tworzenie
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.array([[1, 2], [3, 4]])
arr3 = np.array([1, 2, 3], dtype=np.float32)

# 💡 TIP: Sprawdź właściwości array
print(f"Shape: {arr2.shape}")        # (2, 2)
print(f"Dtype: {arr2.dtype}")        # int64
print(f"Size: {arr2.size}")          # 4
print(f"Ndim: {arr2.ndim}")          # 2
print(f"Memory usage: {arr2.nbytes} bytes")
```

### 2. **np.zeros(), np.ones(), np.full(), np.empty()**
```python
# Tworzenie tablic o określonych wartościach
zeros = np.zeros((3, 4))              # wypełnione zerami
ones = np.ones((2, 3), dtype=int)     # wypełnione jedynkami
full = np.full((2, 2), 7)             # wypełnione wartością 7
empty = np.empty((3, 3))              # niezainicjowane (szybsze)

# 💡 TIP: _like functions - kopiuj shape z innej tablicy
arr = np.array([[1, 2], [3, 4]])
zeros_like = np.zeros_like(arr)       # zeros o tym samym shape co arr
ones_like = np.ones_like(arr)
full_like = np.full_like(arr, 9)
```

### 3. **np.arange(), np.linspace(), np.logspace()**
```python
# Tworzenie sekwencji
range_arr = np.arange(0, 10, 2)       # [0, 2, 4, 6, 8]
linear = np.linspace(0, 1, 5)         # [0, 0.25, 0.5, 0.75, 1]
log_space = np.logspace(0, 2, 3)      # [1, 10, 100] (log scale)

# 💡 TIP: arange z float może być nieprecyzyjny
# Lepsze: np.linspace(0, 1, 11) niż np.arange(0, 1.1, 0.1)
precise = np.linspace(0, 1, 11)       # dokładnie 11 punktów
imprecise = np.arange(0, 1.1, 0.1)   # może mieć błędy floating point
```

## Operacje na shape

### 4. **np.reshape(), np.ravel(), np.flatten()**
```python
arr = np.arange(12)

# Zmiana kształtu
reshaped = arr.reshape(3, 4)          # 1D → 2D
reshaped2 = arr.reshape(2, 6)         # różne kształty
auto_shape = arr.reshape(-1, 4)       # auto-oblicz jeden wymiar

# Spłaszczanie
flattened = reshaped.flatten()        # kopia 1D
raveled = reshaped.ravel()            # view (jeśli możliwe)

# 💡 TIP: reshape(-1) dla automatycznego flatten
auto_flat = reshaped.reshape(-1)      # automatycznie 1D
```

### 5. **np.transpose(), .T, np.swapaxes()**
```python
# Transpozycja
matrix = np.array([[1, 2, 3], [4, 5, 6]])
transposed = matrix.T                 # skrót
transposed2 = np.transpose(matrix)    # pełna funkcja
swapped = np.swapaxes(matrix, 0, 1)   # zamień osie 0 i 1

# Dla 3D+
arr_3d = np.random.rand(2, 3, 4)
# Zmień kolejność osi
reordered = np.transpose(arr_3d, (2, 0, 1))  # (4, 2, 3)

# 💡 TIP: moveaxis dla bardziej czytelnych operacji
moved = np.moveaxis(arr_3d, 0, -1)    # przenieś oś 0 na koniec
```

### 6. **np.expand_dims(), np.squeeze()**
```python
# Dodawanie/usuwanie wymiarów
arr_1d = np.array([1, 2, 3])
expanded = np.expand_dims(arr_1d, axis=0)    # (3,) → (1, 3)
expanded2 = np.expand_dims(arr_1d, axis=1)   # (3,) → (3, 1)

# Usuwanie wymiarów o rozmiarze 1
arr_with_ones = np.array([[[1], [2], [3]]])  # (1, 3, 1)
squeezed = np.squeeze(arr_with_ones)          # (3,)
squeezed_axis = np.squeeze(arr_with_ones, axis=0)  # (3, 1)

# 💡 TIP: Użyj newaxis (alias dla None)
newaxis_expand = arr_1d[:, np.newaxis]       # (3, 1)
newaxis_expand2 = arr_1d[np.newaxis, :]      # (1, 3)
```

## Indexing i slicing

### 7. **Boolean indexing**
```python
arr = np.array([1, 2, 3, 4, 5, 6])

# Boolean maski
mask = arr > 3                        # [False, False, False, True, True, True]
filtered = arr[mask]                  # [4, 5, 6]
filtered2 = arr[arr > 3]              # to samo, w jednej linii

# Złożone warunki
complex_mask = (arr > 2) & (arr < 5)  # [False, True, True, True, False, False]
result = arr[complex_mask]            # [3, 4]

# 💡 TIP: np.where dla conditional selection
conditional = np.where(arr > 3, arr, 0)  # zamień wartości ≤3 na 0
indices = np.where(arr > 3)           # zwróć indeksy gdzie True
```

### 8. **Fancy indexing**
```python
arr = np.array([10, 20, 30, 40, 50])

# Indexing z listą/array
indices = [0, 2, 4]
selected = arr[indices]               # [10, 30, 50]

# 2D fancy indexing
matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
rows = [0, 2]
cols = [1, 2]
result = matrix[rows, cols]           # [2, 9] - (0,1) i (2,2)

# 💡 TIP: Advanced indexing patterns
# Wybierz elementy po przekątnej
diag_indices = np.arange(3)
diagonal = matrix[diag_indices, diag_indices]  # [1, 5, 9]
```

### 9. **np.take(), np.put(), np.clip()**
```python
arr = np.array([10, 20, 30, 40, 50])

# Take - wybierz elementy po indeksach
taken = np.take(arr, [0, 2, 4])       # [10, 30, 50]
taken_2d = np.take(matrix, [0, 4, 8]) # flatten i wybierz

# Put - ustaw wartości po indeksach
arr_copy = arr.copy()
np.put(arr_copy, [1, 3], [99, 88])    # zmień elementy 1 i 3

# Clip - ogranicz wartości do zakresu
clipped = np.clip(arr, 20, 40)        # [20, 20, 30, 40, 40]

# 💡 TIP: Clip z percentilami
data = np.random.normal(0, 1, 1000)
p5, p95 = np.percentile(data, [5, 95])
clipped_outliers = np.clip(data, p5, p95)
```

## Operacje matematyczne

### 10. **Podstawowe operacje arytmetyczne**
```python
a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

# Element-wise operations
sum_arr = a + b                       # [11, 22, 33, 44]
diff = b - a                          # [9, 18, 27, 36]
product = a * b                       # [10, 40, 90, 160]
division = b / a                      # [10, 10, 10, 10]
power = a ** 2                        # [1, 4, 9, 16]

# Broadcasting
arr_2d = np.array([[1, 2], [3, 4]])
broadcast_sum = arr_2d + 10           # dodaj 10 do każdego elementu

# 💡 TIP: In-place operations dla oszczędności pamięci
arr_copy = a.copy()
arr_copy += 10                        # a += 10 zamiast a = a + 10
np.add(a, 10, out=arr_copy)          # jeszcze bardziej explicit
```

### 11. **np.sum(), np.mean(), np.std(), np.var()**
```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

# Agregacje
total_sum = np.sum(arr)               # 21 (wszystkie elementy)
row_sums = np.sum(arr, axis=1)        # [6, 15] (suma wierszy)
col_sums = np.sum(arr, axis=0)        # [5, 7, 9] (suma kolumn)

# Statystyki
mean_val = np.mean(arr)               # 3.5
std_val = np.std(arr)                 # odchylenie standardowe
var_val = np.var(arr)                 # wariancja

# 💡 TIP: keepdims dla zachowania wymiarów
mean_keepdims = np.mean(arr, axis=1, keepdims=True)  # shape (2, 1)
# Przydatne dla broadcasting w dalszych operacjach
normalized = arr - mean_keepdims      # broadcasting działa
```

### 12. **np.min(), np.max(), np.argmin(), np.argmax()**
```python
arr = np.array([[3, 1, 4], [1, 5, 9]])

# Min/Max wartości
min_val = np.min(arr)                 # 1
max_val = np.max(arr)                 # 9
min_per_row = np.min(arr, axis=1)     # [1, 1]
max_per_col = np.max(arr, axis=0)     # [3, 5, 9]

# Indeksy min/max
argmin_flat = np.argmin(arr)          # 1 (indeks w flattened array)
argmax_per_row = np.argmax(arr, axis=1)  # [2, 2] (indeksy w każdym wierszu)

# 💡 TIP: unravel_index dla konwersji flat index na 2D
flat_idx = np.argmax(arr)             # indeks w flattened
row, col = np.unravel_index(flat_idx, arr.shape)  # (1, 2)
```

### 13. **np.dot(), np.matmul(), @**
```python
# Mnożenie macierzy
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

# Różne sposoby mnożenia macierzy
dot_result = np.dot(a, b)             # klasyczne dot product
matmul_result = np.matmul(a, b)       # nowoczesne matrix multiplication
at_result = a @ b                     # operator @ (Python 3.5+)

# Vector operations
v1 = np.array([1, 2, 3])
v2 = np.array([4, 5, 6])
dot_product = np.dot(v1, v2)          # 32 (scalar)

# 💡 TIP: Broadcasting w matrix multiplication
batch_a = np.random.rand(5, 3, 4)    # batch of 5 matrices (3x4)
batch_b = np.random.rand(4, 2)       # single matrix (4x2)
batch_result = batch_a @ batch_b      # shape (5, 3, 2)
```

## Operacje na arrays

### 14. **np.concatenate(), np.stack(), np.hstack(), np.vstack()**
```python
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

# Concatenate - łączenie wzdłuż istniejącej osi
concat_rows = np.concatenate([a, b], axis=0)    # (4, 2)
concat_cols = np.concatenate([a, b], axis=1)    # (2, 4)

# Stack - tworzenie nowej osi
stacked = np.stack([a, b], axis=0)              # (2, 2, 2)
stacked_last = np.stack([a, b], axis=-1)        # (2, 2, 2)

# Convenience functions
vstacked = np.vstack([a, b])          # vertical stack (axis=0)
hstacked = np.hstack([a, b])          # horizontal stack (axis=1)

# 💡 TIP: dstack dla depth stacking
dstacked = np.dstack([a, b])          # depth stack (axis=2) → (2, 2, 2)
```

### 15. **np.split(), np.hsplit(), np.vsplit()**
```python
arr = np.arange(12).reshape(3, 4)

# Split na równe części
h_splits = np.hsplit(arr, 2)          # podziel na 2 części poziomo
v_splits = np.vsplit(arr, 3)          # podziel na 3 części pionowo

# Split w określonych miejscach
custom_h = np.hsplit(arr, [1, 3])     # podziel w kolumnach 1 i 3
custom_v = np.vsplit(arr, [1])        # podziel w wierszu 1

# Array split (bardziej ogólne)
splits = np.array_split(arr, 5, axis=1)  # podziel na 5 (nierównych) części

# 💡 TIP: List comprehension z split
split_arrays = np.hsplit(arr, 4)
processed = [np.sum(sub_arr) for sub_arr in split_arrays]
```

### 16. **np.unique(), np.sort(), np.argsort()**
```python
arr = np.array([3, 1, 4, 1, 5, 9, 2, 6, 5])

# Unikalne wartości
unique_vals = np.unique(arr)          # [1, 2, 3, 4, 5, 6, 9]
unique_with_counts = np.unique(arr, return_counts=True)
values, counts = unique_with_counts   # values: [1,2,3,4,5,6,9], counts: [2,1,1,1,2,1,1]

# Sortowanie
sorted_arr = np.sort(arr)             # sortuj wartości
sort_indices = np.argsort(arr)        # indeksy sortowania
reverse_sorted = np.sort(arr)[::-1]   # sortuj malejąco

# 💡 TIP: Sortowanie 2D arrays
arr_2d = np.random.randint(0, 10, (3, 4))
sorted_by_rows = np.sort(arr_2d, axis=1)    # sortuj każdy wiersz
sorted_by_cols = np.sort(arr_2d, axis=0)    # sortuj każdą kolumnę
```

## Advanced operations

### 17. **np.meshgrid(), np.mgrid, np.ogrid**
```python
# Tworzenie siatek współrzędnych
x = np.array([1, 2, 3])
y = np.array([4, 5])
X, Y = np.meshgrid(x, y)              # X: [[1,2,3],[1,2,3]], Y: [[4,4,4],[5,5,5]]

# Dense grid
xx, yy = np.mgrid[0:3, 0:2]           # to samo co meshgrid dla ranges

# Open (sparse) grid
xx_sparse, yy_sparse = np.ogrid[0:3, 0:2]  # sparse reprezentacja

# 💡 TIP: Użycie do funkcji 2D
def f(x, y):
    return x**2 + y**2

result = f(X, Y)                      # oblicz funkcję na całej siatce
```

### 18. **np.broadcast_arrays(), np.broadcast_to()**
```python
# Broadcasting arrays do wspólnego shape
a = np.array([1, 2, 3])              # (3,)
b = np.array([[1], [2]])             # (2, 1)

broadcasted_a, broadcasted_b = np.broadcast_arrays(a, b)
# a → (2, 3), b → (2, 3)

# Broadcast do określonego shape
broadcasted = np.broadcast_to(a, (4, 3))  # (3,) → (4, 3)

# 💡 TIP: Sprawdź compatibility przed broadcast
try:
    result_shape = np.broadcast_shapes(a.shape, b.shape)
    print(f"Broadcast shape: {result_shape}")
except ValueError as e:
    print(f"Broadcasting error: {e}")
```

### 19. **np.apply_along_axis(), np.vectorize()**
```python
# Apply funkcji wzdłuż osi
arr = np.array([[1, 2, 3], [4, 5, 6]])

def my_func(x):
    return np.sum(x**2)

# Aplikuj funkcję do każdego wiersza
result = np.apply_along_axis(my_func, axis=1, arr=arr)  # [14, 77]

# Vectorize - przekształć skalarną funkcję w wektorową
def scalar_func(x):
    if x < 3:
        return x**2
    else:
        return x**3

vectorized_func = np.vectorize(scalar_func)
result = vectorized_func(arr)

# 💡 TIP: ufunc często szybsze niż vectorize
# Lepiej używać wbudowanych ufunc gdy to możliwe
fast_result = np.where(arr < 3, arr**2, arr**3)  # szybsze niż vectorize
```

### 20. **np.einsum() - Einstein summation**
```python
# Potężne narzędzie do tensor operations
a = np.random.rand(3, 4)
b = np.random.rand(4, 5)

# Matrix multiplication
matmul_result = np.einsum('ij,jk->ik', a, b)    # to samo co a @ b

# Trace (ślad macierzy)
matrix = np.random.rand(4, 4)
trace = np.einsum('ii->', matrix)               # to samo co np.trace(matrix)

# Batch operations
batch_a = np.random.rand(10, 3, 4)
batch_b = np.random.rand(10, 4, 5)
batch_matmul = np.einsum('bij,bjk->bik', batch_a, batch_b)

# 💡 TIP: optimize='optimal' dla lepszej performance
optimized = np.einsum('ij,jk->ik', a, b, optimize='optimal')
```

## Working with NaN and infinity

### 21. **np.isnan(), np.isinf(), np.isfinite()**
```python
arr = np.array([1, 2, np.nan, np.inf, -np.inf, 0])

# Sprawdzanie special values
nan_mask = np.isnan(arr)              # [False, False, True, False, False, False]
inf_mask = np.isinf(arr)              # [False, False, False, True, True, False]
finite_mask = np.isfinite(arr)        # [True, True, False, False, False, True]

# Operacje z NaN
arr_with_nan = np.array([1, 2, np.nan, 4, 5])
nan_sum = np.nansum(arr_with_nan)     # 12.0 (ignoruje NaN)
nan_mean = np.nanmean(arr_with_nan)   # 3.0
nan_std = np.nanstd(arr_with_nan)     # standardowe odchylenie bez NaN

# 💡 TIP: Funkcje nan* dla robust statistics
data = np.array([[1, 2, np.nan], [4, np.nan, 6]])
nanmax = np.nanmax(data, axis=1)      # [2, 6] - max bez NaN w każdym wierszu
```

### 22. **np.nan_to_num(), np.isclose()**
```python
# Zamiana NaN/inf na liczby
arr_with_special = np.array([1, np.nan, np.inf, -np.inf])
cleaned = np.nan_to_num(arr_with_special)        # [1, 0, bardzo_duża_liczba, bardzo_mała_liczba]
custom_cleaned = np.nan_to_num(arr_with_special, nan=0, posinf=999, neginf=-999)

# Porównywanie floating point z tolerancją
a = np.array([1.0, 2.0, 3.0])
b = np.array([1.0000001, 2.0000001, 3.0000001])
close = np.isclose(a, b)              # [True, True, True] (z domyślną tolerancją)
close_strict = np.isclose(a, b, rtol=1e-10)  # [False, False, False]

# 💡 TIP: allclose dla całych arrays
arrays_close = np.allclose(a, b)      # True jeśli wszystkie elementy są close
```

## Random numbers

### 23. **np.random - generowanie liczb losowych**
```python
# Random number generation (nowy Generator API)
rng = np.random.default_rng(seed=42)  # zalecane dla nowego kodu

# Podstawowe generatory
random_floats = rng.random(size=(3, 4))      # [0, 1) uniform
random_ints = rng.integers(0, 10, size=5)    # losowe int z [0, 10)
normal_dist = rng.normal(0, 1, size=1000)    # rozkład normalny

# Stary API (nadal działa)
np.random.seed(42)
old_random = np.random.rand(3, 4)            # [0, 1) uniform
old_randint = np.random.randint(0, 10, 5)    # losowe int

# 💡 TIP: Różne rozkłady
exponential = rng.exponential(scale=2, size=100)
poisson = rng.poisson(lam=3, size=100)
choice = rng.choice(['A', 'B', 'C'], size=10, p=[0.5, 0.3, 0.2])
```

### 24. **np.random.shuffle(), np.random.permutation()**
```python
# Shuffle i permutacje
arr = np.arange(10)
arr_copy = arr.copy()

# Shuffle in-place
rng.shuffle(arr_copy)                 # modyfikuje arr_copy

# Permutation (zwraca nowy array)
permuted = rng.permutation(arr)       # nie modyfikuje arr
perm_indices = rng.permutation(len(arr))  # indeksy permutacji

# 💡 TIP: Controlled randomness dla reproducible results
rng1 = np.random.default_rng(42)
rng2 = np.random.default_rng(42)
# rng1 i rng2 generują te same liczby

sample1 = rng1.random(5)
sample2 = rng2.random(5)
print(np.array_equal(sample1, sample2))  # True
```

## Performance tips

### 25. **Memory layout i performance**
```python
# C vs Fortran order
arr_c = np.arange(1000000).reshape(1000, 1000)  # C order (row-major)
arr_f = np.array(arr_c, order='F')               # Fortran order (column-major)

# Sprawdź memory layout
print(f"C contiguous: {arr_c.flags['C_CONTIGUOUS']}")
print(f"F contiguous: {arr_f.flags['F_CONTIGUOUS']}")

# Performance różni się w zależności od operacji
import time

# Row-wise operations szybsze dla C order
start = time.time()
for row in arr_c:
    np.sum(row)
c_time = time.time() - start

start = time.time()
for row in arr_f:
    np.sum(row)
f_time = time.time() - start

print(f"C order: {c_time:.4f}s, F order: {f_time:.4f}s")
```

### 26. **Vectorization vs loops**
```python
# Porównanie wydajności
n = 1000000
a = np.random.rand(n)
b = np.random.rand(n)

# Python loop (wolny)
def python_loop(a, b):
    result = np.zeros(len(a))
    for i in range(len(a)):
        result[i] = a[i] * b[i] + a[i]**2
    return result

# NumPy vectorized (szybki)
def vectorized(a, b):
    return a * b + a**2

# Timing
import time

start = time.time()
result1 = python_loop(a[:1000], b[:1000])  # test na mniejszym zbiorze
loop_time = time.time() - start

start = time.time()
result2 = vectorized(a, b)
vec_time = time.time() - start

print(f"Loop time (1k elements): {loop_time:.4f}s")
print(f"Vectorized time (1M elements): {vec_time:.4f}s")
print(f"Speedup factor: ~{loop_time/vec_time*1000:.0f}x")
```

### 27. **Memory optimization**
```python
# Sprawdzanie użycia pamięci
arr = np.random.rand(1000, 1000)
print(f"Memory usage: {arr.nbytes / 1024**2:.2f} MB")
print(f"Dtype: {arr.dtype}")

# Optymalizacja typu danych
# Float64 → Float32 (połowa pamięci)
arr_32 = arr.astype(np.float32)
print(f"Float32 memory: {arr_32.nbytes / 1024**2:.2f} MB")

# Int64 → Int32/Int16/Int8 w zależności od zakresu
int_arr = np.random.randint(0, 100, size=10000, dtype=np.int64)
optimized_int = int_arr.astype(np.int8)  # 0-100 mieści się w int8
print(f"Original: {int_arr.nbytes} bytes, Optimized: {optimized_int.nbytes} bytes")

# 💡 TIP: Memory mapping dla bardzo dużych plików
# memmap = np.memmap('large_file.dat', dtype='float32', mode='r+', shape=(10000, 10000))
```

## Advanced tricks

### 28. **Structured arrays**
```python
# Arrays z named fields
dtype = [('name', 'U10'), ('age', 'i4'), ('weight', 'f4')]
people = np.array([
    ('Alice', 25, 55.5),
    ('Bob', 30, 70.2),
    ('Charlie', 35, 80.1)
], dtype=dtype)

print(people['name'])         # ['Alice' 'Bob' 'Charlie']
print(people['age'])          # [25 30 35]

# Sortowanie po field
sorted_by_age = np.sort(people, order='age')

# 💡 TIP: Record arrays dla dot notation
rec_array = np.rec.array(people)
print(rec_array.name)         # to samo co rec_array['name']
```

### 29. **Advanced indexing tricks**
```python
# Conditional assignment
arr = np.random.randint(0, 10, size=(5, 5))
arr[arr < 5] = 0              # zastąp wszystkie < 5 przez 0

# Multiple conditions
arr[(arr > 2) & (arr < 8)] = 99

# Index arrays dla complex selection
rows = np.array([0, 2, 4])
cols = np.array([1, 3, 0])
selected = arr[rows[:, np.newaxis], cols]  # wybierz (0,1), (0,3), (0,0), (2,1), etc.

# 💡 TIP: ix_ dla creating mesh of indices
row_idx = np.array([0, 2])
col_idx = np.array([1, 3])
mesh_row, mesh_col = np.ix_(row_idx, col_idx)
submatrix = arr[mesh_row, mesh_col]  # submacierz (2x2)
```

### 30. **Custom ufuncs**
```python
# Tworzenie własnych universal functions
def custom_func(x, y):
    return x**2 + y**2

# Vectorize (prosty sposób)
vectorized_custom = np.vectorize(custom_func)

# Frompyfunc (bardziej kontroli)
ufunc_custom = np.frompyfunc(custom_func, 2, 1)  # 2 inputs, 1 output

# Test performance
a = np.random.rand(1000)
b = np.random.rand(1000)

result1 = vectorized_custom(a, b)
result2 = ufunc_custom(a, b)

# 💡 TIP: Numba dla jeszcze większej performance
# from numba import vectorize
# @vectorize(['float64(float64, float64)'])
# def numba_func(x, y):
#     return x**2 + y**2
```

## Debugging i best practices

### Common mistakes i jak ich unikać:
```python
# 1. Views vs copies
arr = np.arange(10)
view = arr[::2]          # view
copy = arr[::2].copy()   # explicit copy

arr[0] = 999
print(view[0])           # 999 (view się zmienił!)
print(copy[0])           # 0 (copy się nie zmienił)

# 💡 TIP: Sprawdź czy to view czy copy
print(f"Shares memory: {np.shares_memory(arr, view)}")    # True
print(f"Shares memory: {np.shares_memory(arr, copy)}")    # False

# 2. Broadcasting mistakes
a = np.random.rand(3, 1)
b = np.random.rand(4)
try:
    result = a + b        # (3,1) + (4,) = (3,4) - czy tego chcieliśmy?
except ValueError as e:
    print(f"Broadcasting error: {e}")

# 3. Dtype pitfalls
int_arr = np.array([1, 2, 3], dtype=int)
float_division = int_arr / 2  # wynik: float array
int_division = int_arr // 2   # wynik: int array

# 💡 TIP: Explicit dtype conversions
safe_division = int_arr.astype(float) / 2
```

NumPy to fundament data science w Pythonie - te funkcje i triki pokrywają większość przypadków użycia! 🔢