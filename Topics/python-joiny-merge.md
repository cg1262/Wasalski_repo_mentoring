# Joiny i Merge w Pythonie - Pandas, SQLAlchemy, DuckDB

## Joins w Pandas

### Podstawowe typy joinów

```python
import pandas as pd

# Przykładowe dane
df1 = pd.DataFrame({
    'id': [1, 2, 3, 4],
    'name': ['Anna', 'Jan', 'Maria', 'Piotr'],
    'department': ['IT', 'HR', 'IT', 'Finance']
})

df2 = pd.DataFrame({
    'id': [1, 2, 5, 6],
    'salary': [5000, 6000, 4500, 5500],
    'bonus': [500, 600, 450, 550]
})

print("DataFrame 1:")
print(df1)
print("\nDataFrame 2:")
print(df2)
```

### 1. **Inner Join - tylko wspólne rekordy**

```python
# Inner join - tylko rekordy gdzie klucz istnieje w obu DataFrame
inner_result = df1.merge(df2, on='id', how='inner')
print("Inner Join:")
print(inner_result)
# Wynik: tylko id 1 i 2 (wspólne dla obu DataFrame)

# 💡 TIP: Sprawdź ile rekordów zostało
print(f"Original df1: {len(df1)}, df2: {len(df2)}, merged: {len(inner_result)}")
```

### 2. **Left Join - wszystkie z lewego DataFrame**

```python
# Left join - wszystkie rekordy z df1, dopasowane z df2
left_result = df1.merge(df2, on='id', how='left')
print("Left Join:")
print(left_result)
# Wynik: wszystkie z df1, NaN dla id 3 i 4 w kolumnach z df2

# 💡 TIP: Sprawdź które rekordy nie zostały dopasowane
unmatched = left_result[left_result['salary'].isna()]
print(f"Unmatched records: {len(unmatched)}")
```

### 3. **Right Join - wszystkie z prawego DataFrame**

```python
# Right join - wszystkie rekordy z df2, dopasowane z df1
right_result = df1.merge(df2, on='id', how='right')
print("Right Join:")
print(right_result)
# Wynik: wszystkie z df2, NaN dla id 5 i 6 w kolumnach z df1
```

### 4. **Outer Join - wszystkie rekordy**

```python
# Outer join - wszystkie rekordy z obu DataFrame
outer_result = df1.merge(df2, on='id', how='outer')
print("Outer Join:")
print(outer_result)
# Wynik: wszystkie rekordy, NaN gdzie brak dopasowania

# 💡 TIP: Identyfikuj źródło rekordów
outer_result = df1.merge(df2, on='id', how='outer', indicator=True)
print("\nZ indicator:")
print(outer_result)
# _merge kolumna pokazuje: left_only, right_only, both
```

## Zaawansowane joiny w Pandas

### 5. **Join na różnych nazwach kolumn**

```python
# Różne nazwy kolumn kluczy
df3 = pd.DataFrame({
    'user_id': [1, 2, 3],
    'age': [25, 30, 35]
})

# Join z różnymi nazwami kolumn
result = df1.merge(df3, left_on='id', right_on='user_id')
print("Join na różnych kolumnach:")
print(result)

# 💡 TIP: Usuń zbędną kolumnę po join
result = df1.merge(df3, left_on='id', right_on='user_id').drop('user_id', axis=1)
```

### 6. **Multi-column joins**

```python
# Join na kilku kolumnach
df4 = pd.DataFrame({
    'name': ['Anna', 'Jan', 'Maria'],
    'department': ['IT', 'HR', 'IT'],
    'level': ['Senior', 'Junior', 'Mid']
})

# Join na name i department
multi_result = df1.merge(df4, on=['name', 'department'])
print("Multi-column join:")
print(multi_result)

# 💡 TIP: Partial match - znajdź rekordy z częściowym dopasowaniem
partial = df1.merge(df4, on=['name'], how='left', suffixes=('', '_right'))
print("Partial match:")
print(partial[partial['department_right'].isna()])
```

### 7. **Join z indeksem**

```python
# Join używając indeksu
df1_indexed = df1.set_index('id')
df2_indexed = df2.set_index('id')

# Join na indeksie
index_result = df1_indexed.join(df2_indexed, how='inner')
print("Join na indeksie:")
print(index_result)

# 💡 TIP: Join DataFrame z Series
series_data = pd.Series([100, 200, 300], index=[1, 2, 3], name='extra_bonus')
result_with_series = df1_indexed.join(series_data, how='left')
print("Join z Series:")
print(result_with_series)
```

### 8. **Sufiksy i prefiksy dla kolumn**

```python
# Gdy kolumny mają te same nazwy (oprócz klucza)
df5 = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Company A', 'Company B', 'Company C']  # Konflikt z 'name' w df1
})

# Join z suffiksami
suffix_result = df1.merge(df5, on='id', suffixes=('_person', '_company'))
print("Join z suffiksami:")
print(suffix_result)

# 💡 TIP: Customowe sufiksy
custom_result = df1.merge(df5, on='id', suffixes=('_employee', '_employer'))
```

## Concatenation vs Join

### 9. **pd.concat() - łączenie wierszy/kolumn**

```python
# Concat wierszy (vertical)
df6 = pd.DataFrame({
    'id': [5, 6],
    'name': ['Ewa', 'Tomek'],
    'department': ['Marketing', 'Sales']
})

# Łączenie wierszy
concat_rows = pd.concat([df1, df6], ignore_index=True)
print("Concat wierszy:")
print(concat_rows)

# Łączenie kolumn (horizontal)
concat_cols = pd.concat([df1, df2], axis=1)
print("Concat kolumn:")
print(concat_cols)

# 💡 TIP: Concat z keys do identyfikacji źródła
concat_with_keys = pd.concat([df1, df6], keys=['original', 'new'])
print("Concat z keys:")
print(concat_with_keys)
```

### 10. **Concat vs Merge - kiedy używać**

```python
# CONCAT - gdy:
# 1. Łączysz podobne struktury danych
# 2. Dodajesz nowe wiersze/kolumny
# 3. Nie potrzebujesz złożonego dopasowywania

# MERGE - gdy:
# 1. Łączysz różne struktury danych
# 2. Potrzebujesz dopasować rekordy po kluczu
# 3. Chcesz kontrolować typ join (inner, left, etc.)

# Przykład: dodawanie nowych miesięcy danych (concat)
jan_data = pd.DataFrame({'sales': [100, 200], 'month': ['Jan', 'Jan']})
feb_data = pd.DataFrame({'sales': [150, 250], 'month': ['Feb', 'Feb']})
monthly_data = pd.concat([jan_data, feb_data], ignore_index=True)

# Przykład: łączenie z metadanymi (merge)
metadata = pd.DataFrame({'month': ['Jan', 'Feb'], 'quarter': ['Q1', 'Q1']})
enriched_data = monthly_data.merge(metadata, on='month')
```

## SQL-style joins z pandas

### 11. **Query-style operations**

```python
# SQL-like thinking w pandas
employees = pd.DataFrame({
    'emp_id': [1, 2, 3, 4, 5],
    'name': ['Anna', 'Jan', 'Maria', 'Piotr', 'Ewa'],
    'dept_id': [1, 2, 1, 3, 2]
})

departments = pd.DataFrame({
    'dept_id': [1, 2, 3],
    'dept_name': ['IT', 'HR', 'Finance'],
    'manager': ['Smith', 'Johnson', 'Brown']
})

# Equivalent of: SELECT * FROM employees e INNER JOIN departments d ON e.dept_id = d.dept_id
sql_like = employees.merge(departments, on='dept_id')
print("SQL-style inner join:")
print(sql_like)

# Equivalent of: SELECT name, dept_name FROM employees e LEFT JOIN departments d ON e.dept_id = d.dept_id
selected_columns = employees[['name', 'dept_id']].merge(
    departments[['dept_id', 'dept_name']], 
    on='dept_id', 
    how='left'
)
print("Selected columns with LEFT JOIN:")
print(selected_columns)
```

### 12. **Group by after join**

```python
# JOIN + GROUP BY pattern
joined_data = employees.merge(departments, on='dept_id')

# Policz pracowników w każdym dziale
dept_counts = joined_data.groupby('dept_name').size().reset_index(name='employee_count')
print("Employees per department:")
print(dept_counts)

# Aggregate functions after join
dept_stats = joined_data.groupby('dept_name').agg({
    'emp_id': 'count',
    'name': lambda x: ', '.join(x)
}).reset_index()
dept_stats.columns = ['department', 'employee_count', 'employee_names']
print("Department statistics:")
print(dept_stats)
```

## Joins z SQLAlchemy

### 13. **SQLAlchemy ORM joins**

```python
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Setup
Base = declarative_base()
engine = create_engine('sqlite:///example.db')

# Models
class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    employees = relationship("Employee", back_populates="department")

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    department = relationship("Department", back_populates="employees")

# Create tables
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Query z join
employees_with_dept = session.query(Employee, Department).join(Department).all()

# Do pandas
data = [(emp.name, dept.name) for emp, dept in employees_with_dept]
df_from_sql = pd.DataFrame(data, columns=['employee_name', 'department_name'])

# 💡 TIP: Direct to pandas z SQLAlchemy
query = session.query(Employee.name, Department.name).join(Department)
df_direct = pd.read_sql(query.statement, engine)
```

### 14. **Raw SQL joins z pandas**

```python
# Bezpośrednie SQL z pandas
engine = create_engine('sqlite:///example.db')

# SQL JOIN query
sql_query = """
SELECT 
    e.name as employee_name,
    d.name as department_name,
    COUNT(*) OVER (PARTITION BY d.id) as dept_size
FROM employees e
INNER JOIN departments d ON e.department_id = d.id
ORDER BY d.name, e.name
"""

df_from_sql = pd.read_sql(sql_query, engine)
print("Results from SQL:")
print(df_from_sql)

# 💡 TIP: Parametrized queries
sql_with_params = """
SELECT * FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE d.name = %(dept_name)s
"""

df_filtered = pd.read_sql(sql_with_params, engine, params={'dept_name': 'IT'})
```

## DuckDB joins

### 15. **DuckDB z pandas integration**

```python
import duckdb

# Create connection
conn = duckdb.connect()

# Register pandas DataFrames jako tables
conn.register('employees_df', employees)
conn.register('departments_df', departments)

# SQL queries na pandas DataFrames
result = conn.execute("""
    SELECT 
        e.name,
        d.dept_name,
        d.manager
    FROM employees_df e
    LEFT JOIN departments_df d ON e.dept_id = d.dept_id
""").fetchdf()

print("DuckDB query result:")
print(result)

# 💡 TIP: Complex analytics z DuckDB
analytics_query = """
SELECT 
    d.dept_name,
    COUNT(*) as employee_count,
    STRING_AGG(e.name, ', ') as employees
FROM employees_df e
RIGHT JOIN departments_df d ON e.dept_id = d.dept_id
GROUP BY d.dept_name, d.dept_id
ORDER BY employee_count DESC
"""

analytics_result = conn.execute(analytics_query).fetchdf()
print("Analytics with DuckDB:")
print(analytics_result)
```

## Performance i optimization

### 16. **Performance tips dla joins**

```python
import time

# Przykład z większymi danymi
large_df1 = pd.DataFrame({
    'id': range(100000),
    'value1': range(100000)
})

large_df2 = pd.DataFrame({
    'id': range(50000, 150000),
    'value2': range(100000)
})

# Timing różnych podejść
def time_operation(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start

# 1. Standard merge
result1, time1 = time_operation(large_df1.merge, large_df2, on='id')
print(f"Standard merge: {time1:.4f} seconds")

# 2. Index-based join (faster dla większych danych)
large_df1_indexed = large_df1.set_index('id')
large_df2_indexed = large_df2.set_index('id')
result2, time2 = time_operation(large_df1_indexed.join, large_df2_indexed)
print(f"Index-based join: {time2:.4f} seconds")

# 💡 TIP: Pre-sort data dla lepszej performance
sorted_df1 = large_df1.sort_values('id')
sorted_df2 = large_df2.sort_values('id')
result3, time3 = time_operation(sorted_df1.merge, sorted_df2, on='id')
print(f"Sorted merge: {time3:.4f} seconds")
```

### 17. **Memory optimization**

```python
# Chunked processing dla bardzo dużych danych
def chunked_merge(df1, df2, chunk_size=10000, **merge_kwargs):
    """Merge dużych DataFrame po kawałkach"""
    results = []
    
    for i in range(0, len(df1), chunk_size):
        chunk = df1.iloc[i:i+chunk_size]
        merged_chunk = chunk.merge(df2, **merge_kwargs)
        results.append(merged_chunk)
    
    return pd.concat(results, ignore_index=True)

# Użycie
large_result = chunked_merge(large_df1, large_df2, on='id', how='inner', chunk_size=5000)

# 💡 TIP: Sprawdź memory usage
print(f"Memory usage: {large_result.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Optymalizacja typów danych
optimized_result = large_result.copy()
for col in optimized_result.select_dtypes(['int64']).columns:
    optimized_result[col] = pd.to_numeric(optimized_result[col], downcast='integer')

print(f"Optimized memory: {optimized_result.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
```

## Debugging joins

### 18. **Diagnozowanie problemów z joins**

```python
def diagnose_join(df1, df2, key_col):
    """Diagnozuj potencjalne problemy z join"""
    print(f"Join diagnosis for column: {key_col}")
    print("=" * 50)
    
    # 1. Sprawdź duplicates w key columns
    df1_dups = df1[key_col].duplicated().sum()
    df2_dups = df2[key_col].duplicated().sum()
    print(f"Duplicates in df1[{key_col}]: {df1_dups}")
    print(f"Duplicates in df2[{key_col}]: {df2_dups}")
    
    # 2. Sprawdź null values
    df1_nulls = df1[key_col].isnull().sum()
    df2_nulls = df2[key_col].isnull().sum()
    print(f"Null values in df1[{key_col}]: {df1_nulls}")
    print(f"Null values in df2[{key_col}]: {df2_nulls}")
    
    # 3. Sprawdź overlapping values
    df1_values = set(df1[key_col].dropna())
    df2_values = set(df2[key_col].dropna())
    overlap = df1_values & df2_values
    print(f"Overlapping values: {len(overlap)} out of {len(df1_values)} and {len(df2_values)}")
    
    # 4. Values only in df1 or df2
    only_df1 = df1_values - df2_values
    only_df2 = df2_values - df1_values
    print(f"Only in df1: {len(only_df1)}")
    print(f"Only in df2: {len(only_df2)}")
    
    if len(only_df1) > 0 and len(only_df1) <= 10:
        print(f"Examples only in df1: {list(only_df1)[:5]}")
    if len(only_df2) > 0 and len(only_df2) <= 10:
        print(f"Examples only in df2: {list(only_df2)[:5]}")
    
    # 5. Data types
    print(f"df1[{key_col}] dtype: {df1[key_col].dtype}")
    print(f"df2[{key_col}] dtype: {df2[key_col].dtype}")

# Przykład użycia
diagnose_join(df1, df2, 'id')
```

### 19. **Validate join results**

```python
def validate_join(original_df1, original_df2, joined_df, join_type='inner'):
    """Waliduj wyniki join operacji"""
    print(f"Join validation ({join_type}):")
    print("=" * 30)
    
    # Expected vs actual record count
    if join_type == 'inner':
        # Dla inner join, result nie może być większy niż mniejszy z DataFrame
        max_expected = min(len(original_df1), len(original_df2))
        print(f"Max expected records (inner): {max_expected}")
    elif join_type == 'left':
        print(f"Expected records (left): {len(original_df1)}")
    elif join_type == 'right':
        print(f"Expected records (right): {len(original_df2)}")
    elif join_type == 'outer':
        print(f"Max expected records (outer): {len(original_df1) + len(original_df2)}")
    
    print(f"Actual records: {len(joined_df)}")
    
    # Check for unexpected nulls
    null_counts = joined_df.isnull().sum()
    if null_counts.sum() > 0:
        print("Null values in result:")
        print(null_counts[null_counts > 0])
    
    # Check for data integrity
    total_columns = len(original_df1.columns) + len(original_df2.columns)
    actual_columns = len(joined_df.columns)
    print(f"Expected columns: {total_columns} (minus duplicated keys)")
    print(f"Actual columns: {actual_columns}")

# Test validation
test_join = df1.merge(df2, on='id', how='left')
validate_join(df1, df2, test_join, 'left')
```

## Zaawansowane patterns

### 20. **Fuzzy matching joins**

```python
from difflib import SequenceMatcher

def fuzzy_merge(df1, df2, left_col, right_col, threshold=0.8):
    """Join z fuzzy matching dla podobnych stringów"""
    results = []
    
    for i, row1 in df1.iterrows():
        best_match = None
        best_score = 0
        
        for j, row2 in df2.iterrows():
            score = SequenceMatcher(None, 
                                  str(row1[left_col]).lower(), 
                                  str(row2[right_col]).lower()).ratio()
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = j
        
        if best_match is not None:
            combined_row = pd.concat([row1, df2.iloc[best_match]])
            combined_row['match_score'] = best_score
            results.append(combined_row)
    
    return pd.DataFrame(results)

# Przykład z podobnymi nazwami
df_fuzzy1 = pd.DataFrame({
    'company': ['Apple Inc.', 'Microsoft Corp', 'Google LLC'],
    'revenue': [100, 200, 150]
})

df_fuzzy2 = pd.DataFrame({
    'name': ['Apple Inc', 'Microsoft Corporation', 'Alphabet Inc.'],
    'employees': [150000, 180000, 140000]
})

fuzzy_result = fuzzy_merge(df_fuzzy1, df_fuzzy2, 'company', 'name', threshold=0.6)
print("Fuzzy matching result:")
print(fuzzy_result)
```

### 21. **Rolling joins (temporal)**

```python
# Join z tolerancją czasową
dates1 = pd.date_range('2023-01-01', periods=5, freq='D')
dates2 = pd.date_range('2023-01-01 12:00:00', periods=5, freq='D')

df_time1 = pd.DataFrame({
    'date': dates1,
    'price': [100, 102, 98, 105, 103]
})

df_time2 = pd.DataFrame({
    'date': dates2,
    'volume': [1000, 1200, 800, 1500, 900]
})

# Merge_asof dla temporal joins
temporal_join = pd.merge_asof(
    df_time1.sort_values('date'),
    df_time2.sort_values('date'),
    on='date',
    direction='nearest'  # lub 'backward', 'forward'
)

print("Temporal join result:")
print(temporal_join)

# 💡 TIP: Join z tolerance window
tolerance_join = pd.merge_asof(
    df_time1.sort_values('date'),
    df_time2.sort_values('date'),
    on='date',
    tolerance=pd.Timedelta('6 hours')
)
```

Joins i merge to fundamentalne operacje w analizie danych - te przykłady pokrywają większość scenariuszy! 🔗