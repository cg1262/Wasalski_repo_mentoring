# Top 20-30 Funkcji w Pandas + Tips and Tricks

## Podstawowe operacje na DataFrame

### 1. **pd.read_csv() / pd.read_excel()**
```python
import pandas as pd

# Podstawowe czytanie
df = pd.read_csv('data.csv')

# Z dodatkowymi parametrami
df = pd.read_csv(
    'data.csv',
    sep=';',                    # separator
    encoding='utf-8',           # kodowanie
    index_col=0,               # kolumna jako indeks
    parse_dates=['date'],      # parsowanie dat
    na_values=['N/A', 'NULL'], # wartości NA
    skiprows=1,                # pomiń pierwszą linię
    nrows=1000                 # czytaj tylko 1000 wierszy
)

# 💡 TIP: Użyj chunksize dla dużych plików
for chunk in pd.read_csv('huge_file.csv', chunksize=10000):
    process_chunk(chunk)
```

### 2. **df.head() / df.tail() / df.sample()**
```python
# Podstawowe podglądy
df.head(10)        # pierwsze 10 wierszy
df.tail(5)         # ostatnie 5 wierszy
df.sample(100)     # losowe 100 wierszy

# 💡 TIP: sample() z random_state dla reprodukowalności
df.sample(n=100, random_state=42)
df.sample(frac=0.1, random_state=42)  # 10% danych
```

### 3. **df.info() / df.describe() / df.shape**
```python
# Informacje o DataFrame
df.info()          # typy kolumn, pamięć, null values
df.describe()      # statystyki opisowe
df.shape           # (rows, columns)
df.dtypes          # typy danych

# 💡 TIP: describe() dla wszystkich typów
df.describe(include='all')           # wszystkie kolumny
df.describe(include=['object'])      # tylko tekstowe
df.describe(include=['number'])      # tylko numeryczne
```

## Operacje na kolumnach

### 4. **Wybieranie kolumn**
```python
# Różne sposoby wybierania
df['column_name']              # jedna kolumna (Series)
df[['col1', 'col2']]          # kilka kolumn (DataFrame)
df.loc[:, 'col1':'col3']      # zakres kolumn

# 💡 TIP: Dynamiczne wybieranie kolumn
numeric_cols = df.select_dtypes(include=['number']).columns
text_cols = df.select_dtypes(include=['object']).columns
date_cols = df.select_dtypes(include=['datetime']).columns

# Kolumny zawierające określony tekst
sales_cols = df.columns[df.columns.str.contains('sales', case=False)]
```

### 5. **df.rename()**
```python
# Różne sposoby zmiany nazw
df.rename(columns={'old_name': 'new_name'})

# Funkcja dla wszystkich kolumn
df.rename(columns=str.lower)              # małe litery
df.rename(columns=lambda x: x.replace(' ', '_'))  # spacje na _

# 💡 TIP: Czyszczenie nazw kolumn
df.columns = df.columns.str.strip()      # usuń spacje
df.columns = df.columns.str.replace(' ', '_')  # spacje na _
df.columns = df.columns.str.lower()      # małe litery
```

### 6. **df.drop()**
```python
# Usuwanie kolumn i wierszy
df.drop('column_name', axis=1)           # usuń kolumnę
df.drop(['col1', 'col2'], axis=1)        # usuń kilka kolumn
df.drop([0, 1, 2], axis=0)               # usuń wiersze po indeksie

# 💡 TIP: Usuwanie z warunkami
df.drop(df[df['age'] < 0].index)         # usuń wiersze gdzie age < 0
df.drop(columns=df.columns[df.isnull().sum() > 100])  # usuń kolumny z >100 NaN
```

## Filtrowanie i selekcja

### 7. **Boolean indexing**
```python
# Podstawowe filtrowanie
df[df['age'] > 30]
df[df['city'] == 'Warsaw']
df[(df['age'] > 30) & (df['city'] == 'Warsaw')]
df[(df['age'] > 30) | (df['income'] > 50000)]

# 💡 TIP: Używaj query() dla czytelności
df.query('age > 30 and city == "Warsaw"')
df.query('age > 30 or income > 50000')
df.query('city in ["Warsaw", "Krakow"]')
```

### 8. **df.loc[] / df.iloc[]**
```python
# Loc - po etykietach
df.loc[0:5, 'name':'age']               # wiersze 0-5, kolumny name-age
df.loc[df['age'] > 30, ['name', 'city']]  # filtrowanie + kolumny

# Iloc - po pozycjach
df.iloc[0:5, 1:4]                       # pierwsze 5 wierszy, kolumny 1-3
df.iloc[:, -3:]                         # wszystkie wiersze, ostatnie 3 kolumny

# 💡 TIP: Kombinacje loc/iloc
df.loc[df['score'].idxmax(), :]         # wiersz z maksymalnym score
df.iloc[df['score'].argmax(), :]        # to samo, ale przez iloc
```

### 9. **df.isin() / df.between()**
```python
# Sprawdzanie wartości
df[df['city'].isin(['Warsaw', 'Krakow'])]
df[df['age'].between(25, 65)]

# 💡 TIP: Negacja i kombinacje
df[~df['city'].isin(['Warsaw'])]        # NOT IN
df[df['date'].dt.year.isin([2022, 2023])]  # lata z dat
```

## Sortowanie i grupowanie

### 10. **df.sort_values() / df.sort_index()**
```python
# Sortowanie
df.sort_values('age')                              # rosnąco
df.sort_values('age', ascending=False)             # malejąco
df.sort_values(['city', 'age'])                    # po kilku kolumnach
df.sort_values(['city', 'age'], ascending=[True, False])

# 💡 TIP: Sortowanie z NaN
df.sort_values('column', na_position='first')     # NaN na początku
df.sort_values('column', na_position='last')      # NaN na końcu
```

### 11. **df.groupby()**
```python
# Podstawowe grupowanie
df.groupby('city').mean()
df.groupby('city')['salary'].sum()
df.groupby(['city', 'department']).agg({
    'salary': ['mean', 'sum', 'count'],
    'age': 'mean'
})

# 💡 TIP: Zaawansowane grupowanie
# Grupowanie z named aggregations
df.groupby('city').agg(
    avg_salary=('salary', 'mean'),
    max_age=('age', 'max'),
    count=('id', 'size')
).reset_index()

# Grupowanie z custom funkcjami
df.groupby('city')['salary'].agg(lambda x: x.max() - x.min())
```

## Obsługa brakujących danych

### 12. **df.isna() / df.notna() / df.fillna()**
```python
# Sprawdzanie NaN
df.isna().sum()                        # ilość NaN w każdej kolumnie
df.isna().any()                        # czy są NaN w kolumnach
df.notna().all()                       # czy wszystkie wartości są nie-NaN

# Wypełnianie NaN
df.fillna(0)                           # wszystkie NaN na 0
df.fillna(df.mean())                   # średnią z kolumny
df.fillna(method='ffill')              # forward fill
df.fillna(method='bfill')              # backward fill

# 💡 TIP: Różne strategie dla różnych kolumn
fill_values = {
    'age': df['age'].median(),
    'city': 'Unknown',
    'salary': df['salary'].mean()
}
df.fillna(fill_values)
```

### 13. **df.dropna()**
```python
# Usuwanie NaN
df.dropna()                            # usuń wiersze z ANY NaN
df.dropna(how='all')                   # usuń wiersze z ALL NaN
df.dropna(subset=['important_col'])    # usuń jeśli NaN w określonej kolumnie
df.dropna(thresh=3)                    # usuń jeśli < 3 wartości nie-NaN

# 💡 TIP: Threshold jako procent
threshold = len(df) * 0.8              # 80% wartości musi być nie-NaN
df.dropna(axis=1, thresh=threshold)    # usuń kolumny
```

## Łączenie i mergowanie

### 14. **pd.concat()**
```python
# Łączenie DataFrame
pd.concat([df1, df2])                  # wiersze (vertical)
pd.concat([df1, df2], axis=1)          # kolumny (horizontal)
pd.concat([df1, df2], ignore_index=True)  # resetuj indeks

# 💡 TIP: Concat z keys
pd.concat([df1, df2], keys=['dataset1', 'dataset2'])
```

### 15. **df.merge()**
```python
# Różne typy join
df1.merge(df2, on='key')               # inner join
df1.merge(df2, on='key', how='left')   # left join
df1.merge(df2, on='key', how='outer')  # outer join
df1.merge(df2, left_on='id', right_on='user_id')  # różne nazwy kolumn

# 💡 TIP: Merge z suffiksami
df1.merge(df2, on='key', suffixes=('_left', '_right'))

# Merge z indeksem
df1.merge(df2, left_index=True, right_index=True)
```

### 16. **df.join()**
```python
# Join (głównie dla indeksów)
df1.join(df2)                          # na indeksie
df1.join(df2, how='outer')
df1.join(df2, rsuffix='_right')

# 💡 TIP: Join vs merge
# join() - szybszy dla indeksów
# merge() - bardziej elastyczny dla kolumn
```

## Transformacje danych

### 17. **df.apply() / df.map() / df.applymap()**
```python
# Apply na kolumnach/wierszach
df['new_col'] = df['old_col'].apply(lambda x: x.upper())
df.apply(lambda row: row['col1'] + row['col2'], axis=1)

# Map - tylko dla Series
df['grade'] = df['score'].map({90: 'A', 80: 'B', 70: 'C'})

# Applymap - na każdej komórce
df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# 💡 TIP: Użyj vectorized operations gdy to możliwe
# Zamiast: df['col'].apply(lambda x: x * 2)
# Użyj:    df['col'] * 2
```

### 18. **df.assign()**
```python
# Tworzenie nowych kolumn
df.assign(
    new_col1=df['col1'] * 2,
    new_col2=lambda x: x['col1'] + x['col2'],
    category=lambda x: pd.cut(x['score'], bins=[0, 60, 80, 100], 
                             labels=['Low', 'Medium', 'High'])
)

# 💡 TIP: Chain operations z assign
df.assign(
    score_normalized=lambda x: (x['score'] - x['score'].mean()) / x['score'].std()
).query('score_normalized > 1')
```

### 19. **pd.cut() / pd.qcut()**
```python
# Binning - podział na przedziały
df['age_group'] = pd.cut(df['age'], 
                        bins=[0, 25, 50, 75, 100], 
                        labels=['Young', 'Adult', 'Middle', 'Senior'])

# Quantile-based binning
df['score_quartile'] = pd.qcut(df['score'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

# 💡 TIP: Include_lowest i precision
pd.cut(df['score'], bins=5, include_lowest=True, precision=0)
```

## Operacje na strings

### 20. **df.str accessor**
```python
# String operations
df['name'].str.upper()                 # wielkie litery
df['name'].str.lower()                 # małe litery
df['name'].str.len()                   # długość stringów
df['name'].str.contains('pattern')     # czy zawiera wzorzec
df['name'].str.replace('old', 'new')   # zamiana tekstu
df['name'].str.split(' ')              # podział stringów
df['name'].str.extract(r'(\d+)')       # extract regex groups

# 💡 TIP: Chain string operations
df['clean_name'] = (df['name']
                    .str.strip()
                    .str.lower()
                    .str.replace(' ', '_'))
```

## Operacje na datach

### 21. **pd.to_datetime() / dt accessor**
```python
# Konwersja na daty
df['date'] = pd.to_datetime(df['date'])
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# Datetime operations
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['dayofweek'] = df['date'].dt.dayofweek
df['quarter'] = df['date'].dt.quarter

# 💡 TIP: Date ranges
date_range = pd.date_range('2023-01-01', '2023-12-31', freq='D')
business_days = pd.bdate_range('2023-01-01', '2023-12-31')
```

## Pivot tables i cross-tabulations

### 22. **df.pivot_table()**
```python
# Pivot table
pivot = df.pivot_table(
    values='sales',
    index='region',
    columns='quarter',
    aggfunc='sum',
    fill_value=0
)

# 💡 TIP: Multiple aggregations
pivot = df.pivot_table(
    values=['sales', 'profit'],
    index='region',
    columns='year',
    aggfunc={'sales': 'sum', 'profit': 'mean'}
)
```

### 23. **pd.crosstab()**
```python
# Cross-tabulation
ct = pd.crosstab(df['category'], df['region'])
ct_normalized = pd.crosstab(df['category'], df['region'], normalize=True)

# 💡 TIP: With margins (totals)
pd.crosstab(df['category'], df['region'], margins=True)
```

## Operacje na indeksach

### 24. **df.set_index() / df.reset_index()**
```python
# Ustawianie indeksu
df.set_index('date')                   # kolumna jako indeks
df.set_index(['region', 'city'])       # multi-index
df.reset_index()                       # indeks jako kolumna
df.reset_index(drop=True)              # usuń stary indeks

# 💡 TIP: In-place operations
df.set_index('date', inplace=True)
```

### 25. **df.reindex()**
```python
# Reindeksowanie
new_index = ['A', 'B', 'C', 'D']
df.reindex(new_index)
df.reindex(new_index, fill_value=0)

# 💡 TIP: Reindex z date range
date_index = pd.date_range('2023-01-01', '2023-12-31', freq='D')
df.reindex(date_index, method='ffill')
```

## Window functions

### 26. **df.rolling() / df.expanding()**
```python
# Rolling windows
df['moving_avg'] = df['price'].rolling(window=30).mean()
df['rolling_std'] = df['price'].rolling(window=30).std()

# Expanding windows
df['cumulative_avg'] = df['price'].expanding().mean()

# 💡 TIP: Custom window functions
df['custom_metric'] = df['price'].rolling(window=10).apply(lambda x: x.max() - x.min())
```

### 27. **df.shift() / df.diff()**
```python
# Przesunięcia
df['prev_price'] = df['price'].shift(1)        # poprzednia wartość
df['next_price'] = df['price'].shift(-1)       # następna wartość
df['price_change'] = df['price'].diff()        # różnica z poprzednią
df['pct_change'] = df['price'].pct_change()    # procentowa zmiana

# 💡 TIP: Lag features dla ML
for lag in [1, 2, 3, 7]:
    df[f'price_lag_{lag}'] = df['price'].shift(lag)
```

## Zaawansowane operacje

### 28. **df.explode()**
```python
# Rozwijanie list w kolumnach
df_exploded = df.explode('list_column')

# 💡 TIP: Multiple columns
df.explode(['col1', 'col2'])
```

### 29. **df.melt() / df.pivot()**
```python
# Wide to long format
df_melted = df.melt(
    id_vars=['id', 'name'],
    value_vars=['q1', 'q2', 'q3', 'q4'],
    var_name='quarter',
    value_name='score'
)

# Long to wide format
df_wide = df.pivot(index='id', columns='quarter', values='score')

# 💡 TIP: Multiple value columns
df.pivot(index='id', columns='quarter', values=['score', 'grade'])
```

### 30. **Performance tips**
```python
# Memory optimization
df.info(memory_usage='deep')           # sprawdź użycie pamięci

# Zmiana typów danych
df['category'] = df['category'].astype('category')  # kategorie
df['int_col'] = pd.to_numeric(df['int_col'], downcast='integer')

# 💡 TIP: Use vectorized operations
# Zamiast loop:
result = []
for idx, row in df.iterrows():
    result.append(row['a'] + row['b'])

# Użyj:
result = df['a'] + df['b']

# Avoid chained assignments
# Zamiast: df['col'][df['col'] > 0] = 1
# Użyj:    df.loc[df['col'] > 0, 'col'] = 1
```

## Debugging i performance

### Najczęstsze błędy i jak ich unikać:

```python
# 1. SettingWithCopyWarning
# ZŁE:
df[df['age'] > 30]['new_col'] = 'value'
# DOBRE:
df.loc[df['age'] > 30, 'new_col'] = 'value'

# 2. Memory issues
# Sprawdź pamięć przed operacjami
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# 3. Performance monitoring
import time
start_time = time.time()
# twoja operacja
print(f"Operation took: {time.time() - start_time:.2f} seconds")

# 4. Use method chaining
result = (df
    .query('age > 30')
    .groupby('city')
    .agg({'salary': 'mean'})
    .reset_index()
    .sort_values('salary', ascending=False)
)
```

Te funkcje i triki pokrywają większość codziennych operacji w pandas! 🐼

---

# 🇬🇧 ENGLISH VERSION

# Top 20-30 Pandas Functions + Tips and Tricks

## Basic DataFrame operations

### 1. **pd.read_csv() / pd.read_excel()**
```python
import pandas as pd

# Basic reading
df = pd.read_csv('data.csv')

# With additional parameters
df = pd.read_csv(
    'data.csv',
    sep=';',                    # separator
    encoding='utf-8',           # encoding
    index_col=0,               # column as index
    parse_dates=['date'],      # date parsing
    na_values=['N/A', 'NULL'], # NA values
    skiprows=1,                # skip first line
    nrows=1000                 # read only 1000 rows
)

# 💡 TIP: Use chunksize for large files
for chunk in pd.read_csv('huge_file.csv', chunksize=10000):
    process_chunk(chunk)
```

### 2. **df.head() / df.tail() / df.sample()**
```python
# Basic previews
df.head(10)        # first 10 rows
df.tail(5)         # last 5 rows
df.sample(100)     # random 100 rows

# 💡 TIP: sample() with random_state for reproducibility
df.sample(n=100, random_state=42)
df.sample(frac=0.1, random_state=42)  # 10% of data
```

### 3. **df.info() / df.describe() / df.shape**
```python
# DataFrame information
df.info()          # column types, memory, null values
df.describe()      # descriptive statistics
df.shape           # (rows, columns)
df.dtypes          # data types

# 💡 TIP: describe() for all types
df.describe(include='all')           # all columns
df.describe(include=['object'])      # only text columns
df.describe(include=['number'])      # only numeric columns
```

## Column operations

### 4. **Column selection**
```python
# Different ways to select
df['column_name']              # single column (Series)
df[['col1', 'col2']]          # multiple columns (DataFrame)
df.loc[:, 'col1':'col3']      # column range

# 💡 TIP: Dynamic column selection
numeric_cols = df.select_dtypes(include=['number']).columns
text_cols = df.select_dtypes(include=['object']).columns
date_cols = df.select_dtypes(include=['datetime']).columns

# Columns containing specific text
sales_cols = df.columns[df.columns.str.contains('sales', case=False)]
```

### 5. **df.rename()**
```python
# Different ways to rename
df.rename(columns={'old_name': 'new_name'})

# Function for all columns
df.rename(columns=str.lower)              # lowercase
df.rename(columns=lambda x: x.replace(' ', '_'))  # spaces to _

# 💡 TIP: Clean column names
df.columns = df.columns.str.strip()      # remove spaces
df.columns = df.columns.str.replace(' ', '_')  # spaces to _
df.columns = df.columns.str.lower()      # lowercase
```

### 6. **df.drop()**
```python
# Dropping columns and rows
df.drop('column_name', axis=1)           # drop column
df.drop(['col1', 'col2'], axis=1)        # drop multiple columns
df.drop([0, 1, 2], axis=0)               # drop rows by index

# 💡 TIP: Conditional dropping
df.drop(df[df['age'] < 0].index)         # drop rows where age < 0
df.drop(columns=df.columns[df.isnull().sum() > 100])  # drop columns with >100 NaN
```

## Filtering and selection

### 7. **Boolean indexing**
```python
# Basic filtering
df[df['age'] > 30]
df[df['city'] == 'Warsaw']
df[(df['age'] > 30) & (df['city'] == 'Warsaw')]
df[(df['age'] > 30) | (df['income'] > 50000)]

# 💡 TIP: Use query() for readability
df.query('age > 30 and city == "Warsaw"')
df.query('age > 30 or income > 50000')
df.query('city in ["Warsaw", "Krakow"]')
```

### 8. **df.loc[] / df.iloc[]**
```python
# Loc - by labels
df.loc[0:5, 'name':'age']               # rows 0-5, columns name-age
df.loc[df['age'] > 30, ['name', 'city']]  # filtering + columns

# Iloc - by positions
df.iloc[0:5, 1:4]                       # first 5 rows, columns 1-3
df.iloc[:, -3:]                         # all rows, last 3 columns

# 💡 TIP: Combining loc/iloc
df.loc[df['score'].idxmax(), :]         # row with maximum score
df.iloc[df['score'].argmax(), :]        # same, but through iloc
```

### 9. **df.isin() / df.between()**
```python
# Value checking
df[df['city'].isin(['Warsaw', 'Krakow'])]
df[df['age'].between(25, 65)]

# 💡 TIP: Negation and combinations
df[~df['city'].isin(['Warsaw'])]        # NOT IN
df[df['date'].dt.year.isin([2022, 2023])]  # years from dates
```

## Sorting and grouping

### 10. **df.sort_values() / df.sort_index()**
```python
# Sorting
df.sort_values('age')                              # ascending
df.sort_values('age', ascending=False)             # descending
df.sort_values(['city', 'age'])                    # multiple columns
df.sort_values(['city', 'age'], ascending=[True, False])

# 💡 TIP: Sorting with NaN
df.sort_values('column', na_position='first')     # NaN first
df.sort_values('column', na_position='last')      # NaN last
```

### 11. **df.groupby()**
```python
# Basic grouping
df.groupby('city').mean()
df.groupby('city')['salary'].sum()
df.groupby(['city', 'department']).agg({
    'salary': ['mean', 'sum', 'count'],
    'age': 'mean'
})

# 💡 TIP: Advanced grouping
# Grouping with named aggregations
df.groupby('city').agg(
    avg_salary=('salary', 'mean'),
    max_age=('age', 'max'),
    count=('id', 'size')
).reset_index()

# Grouping with custom functions
df.groupby('city')['salary'].agg(lambda x: x.max() - x.min())
```

## Handling missing data

### 12. **df.isna() / df.notna() / df.fillna()**
```python
# Checking NaN
df.isna().sum()                        # number of NaN in each column
df.isna().any()                        # whether there are NaN in columns
df.notna().all()                       # whether all values are non-NaN

# Filling NaN
df.fillna(0)                           # all NaN to 0
df.fillna(df.mean())                   # with column mean
df.fillna(method='ffill')              # forward fill
df.fillna(method='bfill')              # backward fill

# 💡 TIP: Different strategies for different columns
fill_values = {
    'age': df['age'].median(),
    'city': 'Unknown',
    'salary': df['salary'].mean()
}
df.fillna(fill_values)
```

### 13. **df.dropna()**
```python
# Dropping NaN
df.dropna()                            # drop rows with ANY NaN
df.dropna(how='all')                   # drop rows with ALL NaN
df.dropna(subset=['important_col'])    # drop if NaN in specific column
df.dropna(thresh=3)                    # drop if < 3 non-NaN values

# 💡 TIP: Threshold as percentage
threshold = len(df) * 0.8              # 80% values must be non-NaN
df.dropna(axis=1, thresh=threshold)    # drop columns
```

## Joining and merging

### 14. **pd.concat()**
```python
# Joining DataFrames
pd.concat([df1, df2])                  # rows (vertical)
pd.concat([df1, df2], axis=1)          # columns (horizontal)
pd.concat([df1, df2], ignore_index=True)  # reset index

# 💡 TIP: Concat with keys
pd.concat([df1, df2], keys=['dataset1', 'dataset2'])
```

### 15. **df.merge()**
```python
# Different join types
df1.merge(df2, on='key')               # inner join
df1.merge(df2, on='key', how='left')   # left join
df1.merge(df2, on='key', how='outer')  # outer join
df1.merge(df2, left_on='id', right_on='user_id')  # different column names

# 💡 TIP: Merge with suffixes
df1.merge(df2, on='key', suffixes=('_left', '_right'))

# Merge with index
df1.merge(df2, left_index=True, right_index=True)
```

### 16. **df.join()**
```python
# Join (mainly for indexes)
df1.join(df2)                          # on index
df1.join(df2, how='outer')
df1.join(df2, rsuffix='_right')

# 💡 TIP: Join vs merge
# join() - faster for indexes
# merge() - more flexible for columns
```

## Data transformations

### 17. **df.apply() / df.map() / df.applymap()**
```python
# Apply on columns/rows
df['new_col'] = df['old_col'].apply(lambda x: x.upper())
df.apply(lambda row: row['col1'] + row['col2'], axis=1)

# Map - only for Series
df['grade'] = df['score'].map({90: 'A', 80: 'B', 70: 'C'})

# Applymap - on each cell
df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# 💡 TIP: Use vectorized operations when possible
# Instead of: df['col'].apply(lambda x: x * 2)
# Use:        df['col'] * 2
```

### 18. **df.assign()**
```python
# Creating new columns
df.assign(
    new_col1=df['col1'] * 2,
    new_col2=lambda x: x['col1'] + x['col2'],
    category=lambda x: pd.cut(x['score'], bins=[0, 60, 80, 100], 
                             labels=['Low', 'Medium', 'High'])
)

# 💡 TIP: Chain operations with assign
df.assign(
    score_normalized=lambda x: (x['score'] - x['score'].mean()) / x['score'].std()
).query('score_normalized > 1')
```

### 19. **pd.cut() / pd.qcut()**
```python
# Binning - dividing into intervals
df['age_group'] = pd.cut(df['age'], 
                        bins=[0, 25, 50, 75, 100], 
                        labels=['Young', 'Adult', 'Middle', 'Senior'])

# Quantile-based binning
df['score_quartile'] = pd.qcut(df['score'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

# 💡 TIP: Include_lowest and precision
pd.cut(df['score'], bins=5, include_lowest=True, precision=0)
```

## String operations

### 20. **df.str accessor**
```python
# String operations
df['name'].str.upper()                 # uppercase
df['name'].str.lower()                 # lowercase
df['name'].str.len()                   # string length
df['name'].str.contains('pattern')     # contains pattern
df['name'].str.replace('old', 'new')   # replace text
df['name'].str.split(' ')              # split strings
df['name'].str.extract(r'(\d+)')       # extract regex groups

# 💡 TIP: Chain string operations
df['clean_name'] = (df['name']
                    .str.strip()
                    .str.lower()
                    .str.replace(' ', '_'))
```

## Date operations

### 21. **pd.to_datetime() / dt accessor**
```python
# Convert to dates
df['date'] = pd.to_datetime(df['date'])
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# Datetime operations
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['dayofweek'] = df['date'].dt.dayofweek
df['quarter'] = df['date'].dt.quarter

# 💡 TIP: Date ranges
date_range = pd.date_range('2023-01-01', '2023-12-31', freq='D')
business_days = pd.bdate_range('2023-01-01', '2023-12-31')
```

## Pivot tables and cross-tabulations

### 22. **df.pivot_table()**
```python
# Pivot table
pivot = df.pivot_table(
    values='sales',
    index='region',
    columns='quarter',
    aggfunc='sum',
    fill_value=0
)

# 💡 TIP: Multiple aggregations
pivot = df.pivot_table(
    values=['sales', 'profit'],
    index='region',
    columns='year',
    aggfunc={'sales': 'sum', 'profit': 'mean'}
)
```

### 23. **pd.crosstab()**
```python
# Cross-tabulation
ct = pd.crosstab(df['category'], df['region'])
ct_normalized = pd.crosstab(df['category'], df['region'], normalize=True)

# 💡 TIP: With margins (totals)
pd.crosstab(df['category'], df['region'], margins=True)
```

## Index operations

### 24. **df.set_index() / df.reset_index()**
```python
# Setting index
df.set_index('date')                   # column as index
df.set_index(['region', 'city'])       # multi-index
df.reset_index()                       # index as column
df.reset_index(drop=True)              # drop old index

# 💡 TIP: In-place operations
df.set_index('date', inplace=True)
```

### 25. **df.reindex()**
```python
# Reindexing
new_index = ['A', 'B', 'C', 'D']
df.reindex(new_index)
df.reindex(new_index, fill_value=0)

# 💡 TIP: Reindex with date range
date_index = pd.date_range('2023-01-01', '2023-12-31', freq='D')
df.reindex(date_index, method='ffill')
```

## Window functions

### 26. **df.rolling() / df.expanding()**
```python
# Rolling windows
df['moving_avg'] = df['price'].rolling(window=30).mean()
df['rolling_std'] = df['price'].rolling(window=30).std()

# Expanding windows
df['cumulative_avg'] = df['price'].expanding().mean()

# 💡 TIP: Custom window functions
df['custom_metric'] = df['price'].rolling(window=10).apply(lambda x: x.max() - x.min())
```

### 27. **df.shift() / df.diff()**
```python
# Shifts
df['prev_price'] = df['price'].shift(1)        # previous value
df['next_price'] = df['price'].shift(-1)       # next value
df['price_change'] = df['price'].diff()        # difference from previous
df['pct_change'] = df['price'].pct_change()    # percentage change

# 💡 TIP: Lag features for ML
for lag in [1, 2, 3, 7]:
    df[f'price_lag_{lag}'] = df['price'].shift(lag)
```

## Advanced operations

### 28. **df.explode()**
```python
# Exploding lists in columns
df_exploded = df.explode('list_column')

# 💡 TIP: Multiple columns
df.explode(['col1', 'col2'])
```

### 29. **df.melt() / df.pivot()**
```python
# Wide to long format
df_melted = df.melt(
    id_vars=['id', 'name'],
    value_vars=['q1', 'q2', 'q3', 'q4'],
    var_name='quarter',
    value_name='score'
)

# Long to wide format
df_wide = df.pivot(index='id', columns='quarter', values='score')

# 💡 TIP: Multiple value columns
df.pivot(index='id', columns='quarter', values=['score', 'grade'])
```

### 30. **Performance tips**
```python
# Memory optimization
df.info(memory_usage='deep')           # check memory usage

# Change data types
df['category'] = df['category'].astype('category')  # categories
df['int_col'] = pd.to_numeric(df['int_col'], downcast='integer')

# 💡 TIP: Use vectorized operations
# Instead of loop:
result = []
for idx, row in df.iterrows():
    result.append(row['a'] + row['b'])

# Use:
result = df['a'] + df['b']

# Avoid chained assignments
# Instead of: df['col'][df['col'] > 0] = 1
# Use:        df.loc[df['col'] > 0, 'col'] = 1
```

## Debugging and performance

### Common mistakes and how to avoid them:

```python
# 1. SettingWithCopyWarning
# BAD:
df[df['age'] > 30]['new_col'] = 'value'
# GOOD:
df.loc[df['age'] > 30, 'new_col'] = 'value'

# 2. Memory issues
# Check memory before operations
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# 3. Performance monitoring
import time
start_time = time.time()
# your operation
print(f"Operation took: {time.time() - start_time:.2f} seconds")

# 4. Use method chaining
result = (df
    .query('age > 30')
    .groupby('city')
    .agg({'salary': 'mean'})
    .reset_index()
    .sort_values('salary', ascending=False)
)
```

These functions and tricks cover most daily operations in pandas! 🐼