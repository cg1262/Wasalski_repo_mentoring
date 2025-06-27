# MongoDB - jak działa?

## Co to jest MongoDB?

MongoDB to **dokumentowa baza danych NoSQL**, która przechowuje dane w formacie podobnym do JSON (BSON - Binary JSON).

### Główne cechy:
- **Dokumentowa** - dane w dokumentach, nie w tabelach
- **Schemat-flexible** - dokumenty mogą mieć różne struktury
- **Skalowalna** - łatwe skalowanie horyzontalne
- **Wydajna** - szybkie zapytania i indeksowanie

## Podstawowe pojęcia

### MongoDB vs SQL:
| MongoDB | SQL | Opis |
|---------|-----|------|
| Database | Database | Baza danych |
| Collection | Table | Zbiór dokumentów/rekordów |
| Document | Row | Pojedynczy rekord |
| Field | Column | Pole w dokumencie |

### Struktura dokumentu:
```javascript
// Przykład dokumentu w MongoDB
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "Jan Kowalski",
  "age": 30,
  "email": "jan@example.com",
  "address": {
    "street": "Marszałkowska 1",
    "city": "Warszawa",
    "zipCode": "00-001"
  },
  "hobbies": ["czytanie", "sport", "programowanie"],
  "isActive": true,
  "createdAt": ISODate("2023-01-15T10:30:00Z")
}
```

## Podstawowe operacje CRUD

### 1. **Create** - Tworzenie dokumentów

```javascript
// Wstawienie pojedynczego dokumentu
db.users.insertOne({
  name: "Anna Nowak",
  age: 25,
  email: "anna@example.com",
  skills: ["JavaScript", "Python", "MongoDB"]
});

// Wstawienie wielu dokumentów
db.users.insertMany([
  {
    name: "Piotr Wiśniewski",
    age: 35,
    department: "IT"
  },
  {
    name: "Maria Kowalczyk",
    age: 28,
    department: "Marketing"
  }
]);
```

### 2. **Read** - Odczytywanie dokumentów

```javascript
// Wszystkie dokumenty
db.users.find();

// Z filtrem
db.users.find({ age: { $gte: 30 } }); // Wiek >= 30

// Jeden dokument
db.users.findOne({ email: "jan@example.com" });

// Z projekcją (wybrane pola)
db.users.find(
  { department: "IT" },
  { name: 1, email: 1, _id: 0 } // Pokaż tylko name i email
);

// Sortowanie i limit
db.users.find().sort({ age: -1 }).limit(5); // 5 najstarszych

// Zagnieżdżone pola
db.users.find({ "address.city": "Warszawa" });

// Tablice
db.users.find({ hobbies: "sport" }); // Zawiera "sport"
db.users.find({ skills: { $in: ["Python", "Java"] } }); // Zawiera Python LUB Java
```

### 3. **Update** - Aktualizacja dokumentów

```javascript
// Aktualizacja jednego dokumentu
db.users.updateOne(
  { email: "jan@example.com" },
  { 
    $set: { age: 31 },
    $push: { hobbies: "gotowanie" } // Dodaj do tablicy
  }
);

// Aktualizacja wielu dokumentów
db.users.updateMany(
  { department: "IT" },
  { $set: { "benefits.health": true } }
);

// Upsert - wstaw jeśli nie istnieje
db.users.updateOne(
  { email: "nowy@example.com" },
  { $set: { name: "Nowy Użytkownik", age: 20 } },
  { upsert: true }
);

// Operatory aktualizacji
db.users.updateOne(
  { _id: ObjectId("...") },
  {
    $set: { name: "Nowa nazwa" },           // Ustaw wartość
    $unset: { oldField: "" },               // Usuń pole
    $inc: { age: 1 },                       // Zwiększ o 1
    $push: { tags: "nowy-tag" },            // Dodaj do tablicy
    $pull: { tags: "stary-tag" },           // Usuń z tablicy
    $currentDate: { lastModified: true }    // Ustaw na aktualną datę
  }
);
```

### 4. **Delete** - Usuwanie dokumentów

```javascript
// Usuń jeden dokument
db.users.deleteOne({ email: "temp@example.com" });

// Usuń wiele dokumentów
db.users.deleteMany({ isActive: false });

// Usuń wszystkie dokumenty z kolekcji
db.users.deleteMany({});
```

## Zaawansowane zapytania

### Operatory porównania:
```javascript
// Równość, nierówność
db.users.find({ age: 30 });                    // age = 30
db.users.find({ age: { $ne: 30 } });           // age != 30
db.users.find({ age: { $gt: 30 } });           // age > 30
db.users.find({ age: { $gte: 30 } });          // age >= 30
db.users.find({ age: { $lt: 30 } });           // age < 30
db.users.find({ age: { $lte: 30 } });          // age <= 30
db.users.find({ age: { $in: [25, 30, 35] } }); // age IN (25,30,35)
```

### Operatory logiczne:
```javascript
// AND (domyślnie)
db.users.find({ age: { $gte: 25 }, department: "IT" });

// OR
db.users.find({
  $or: [
    { age: { $lt: 25 } },
    { department: "Management" }
  ]
});

// NOT
db.users.find({ age: { $not: { $gt: 50 } } });

// NOR
db.users.find({
  $nor: [
    { age: { $lt: 18 } },
    { isActive: false }
  ]
});
```

### Wyrażenia regularne:
```javascript
// Nazwa zaczyna się od "A"
db.users.find({ name: /^A/ });

// Email zawiera "gmail"
db.users.find({ email: /gmail/ });

// Case-insensitive
db.users.find({ name: /anna/i });
```

## Agregacja - zaawansowane przetwarzanie

### Pipeline agregacji:
```javascript
db.users.aggregate([
  // Filtrowanie
  { $match: { age: { $gte: 25 } } },
  
  // Grupowanie
  { $group: {
    _id: "$department",
    avgAge: { $avg: "$age" },
    count: { $sum: 1 },
    maxSalary: { $max: "$salary" }
  }},
  
  // Sortowanie
  { $sort: { avgAge: -1 } },
  
  // Limit
  { $limit: 5 }
]);

// Bardziej zaawansowany przykład
db.orders.aggregate([
  // Rozwiń tablicę items
  { $unwind: "$items" },
  
  // Dołącz informacje o produktach
  { $lookup: {
    from: "products",
    localField: "items.productId",
    foreignField: "_id",
    as: "productInfo"
  }},
  
  // Oblicz wartość każdej pozycji
  { $addFields: {
    itemValue: { $multiply: ["$items.quantity", "$items.price"] }
  }},
  
  // Grupuj według klienta
  { $group: {
    _id: "$customerId",
    totalSpent: { $sum: "$itemValue" },
    orderCount: { $sum: 1 }
  }},
  
  // Sortuj według wydanych pieniędzy
  { $sort: { totalSpent: -1 } }
]);
```

## Indeksowanie

### Tworzenie indeksów:
```javascript
// Prosty indeks
db.users.createIndex({ email: 1 }); // 1 = rosnąco, -1 = malejąco

// Indeks złożony
db.users.createIndex({ department: 1, age: -1 });

// Indeks tekstowy
db.articles.createIndex({ title: "text", content: "text" });

// Indeks 2dsphere (geolokalizacja)
db.places.createIndex({ location: "2dsphere" });

// Indeks sparse (tylko dla dokumentów z tym polem)
db.users.createIndex({ phoneNumber: 1 }, { sparse: true });

// Indeks unique
db.users.createIndex({ email: 1 }, { unique: true });
```

### Sprawdzanie indeksów:
```javascript
// Lista indeksów
db.users.getIndexes();

// Statystyki użycia indeksu
db.users.find({ email: "test@example.com" }).explain("executionStats");

// Usuwanie indeksu
db.users.dropIndex({ email: 1 });
```

## Replikacja i Sharding

### Replica Set (replikacja):
```javascript
// Konfiguracja replica set
rs.initiate({
  _id: "myReplicaSet",
  members: [
    { _id: 0, host: "mongodb1.example.com:27017" },
    { _id: 1, host: "mongodb2.example.com:27017" },
    { _id: 2, host: "mongodb3.example.com:27017" }
  ]
});

// Status repliki
rs.status();
```

### Sharding (partycjonowanie):
```javascript
// Włączenie sharding dla bazy
sh.enableSharding("myDatabase");

// Sharding kolekcji
sh.shardCollection("myDatabase.users", { userId: 1 });
```

## Połączenie z aplikacją (Python)

```python
import pymongo
from pymongo import MongoClient

# Połączenie
client = MongoClient('mongodb://localhost:27017/')
db = client['myDatabase']
collection = db['users']

# Wstawienie
result = collection.insert_one({
    "name": "Jan Kowalski",
    "age": 30,
    "email": "jan@example.com"
})

# Wyszukiwanie
user = collection.find_one({"email": "jan@example.com"})
print(user)

# Aktualizacja
collection.update_one(
    {"email": "jan@example.com"},
    {"$set": {"age": 31}}
)

# Usuwanie
collection.delete_one({"email": "jan@example.com"})

# Agregacja
pipeline = [
    {"$match": {"age": {"$gte": 25}}},
    {"$group": {
        "_id": "$department",
        "avgAge": {"$avg": "$age"}
    }}
]
results = list(collection.aggregate(pipeline))
```

## Zalety i wady MongoDB

### Zalety:
- ✅ **Elastyczny schemat** - łatwe zmiany struktury
- ✅ **Szybkie zapytania** - dobrze zoptymalizowane
- ✅ **Skalowanie horyzontalne** - sharding
- ✅ **Dokumenty JSON** - naturalne dla aplikacji web
- ✅ **Bogata funkcjonalność** - aggregation pipeline
- ✅ **Dobra wydajność** dla odczytu

### Wady:
- ❌ **Brak JOIN-ów** - trzeba robić lookup lub denormalizację
- ❌ **Większe zużycie pamięci** - duplikacja danych
- ❌ **Eventual consistency** w niektórych konfiguracjach
- ❌ **Brak ACID na poziomie kolekcji** (do wersji 4.0)
- ❌ **Křiva uczenia** - inne podejście niż SQL

## Kiedy używać MongoDB?

### ✅ Dobrze nadaje się do:
- **Aplikacji web** - dane JSON/BSON
- **Katalogów produktów** - różne atrybuty produktów
- **Logów i analityki** - duże ilości danych
- **CMS** - różne typy treści
- **Real-time aplikacji** - czaty, powiadomienia

### ❌ Unikaj gdy:
- **Złożone relacje** - lepiej SQL
- **Silne wymagania ACID** - lepiej PostgreSQL
- **Małe budżety** - licencjonowanie MongoDB
- **Zespół zna tylko SQL** - křiva uczenia