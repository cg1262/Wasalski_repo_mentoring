# Life RPG - Gamifikacja Życia 🎮

Aplikacja webowa inspirowana szablonem Life RPG z Notion, która przekształca codzienne zadania w grę RPG.

## 📋 Wymagania

- Python 3.7+
- pip (menedżer pakietów Python)

## 🚀 Instalacja

1. **Sklonuj lub pobierz pliki projektu**
   
2. **Utwórz wirtualne środowisko (opcjonalne, ale zalecane):**
   ```bash
   python -m venv venv
   
   # Windows:
   venv\Scripts\activate
   
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Zainstaluj wymagane pakiety:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uruchom aplikację:**
   ```bash
   python app.py
   ```

5. **Otwórz przeglądarkę i przejdź do:**
   ```
   http://localhost:5000
   ```

## 🎮 Jak używać aplikacji

### Dashboard
- Widok główny pokazuje poziom, całkowite XP, monety i pasek postępu
- Zakładki: Przegląd, Zadania, Nawyki, Nagrody

### Zadania
- Kliknij "+ Nowe Zadanie" aby dodać quest
- Ustaw nagrodę XP i monet
- Przypisz do obszaru życia
- Kliknij na zadanie aby je ukończyć i zdobyć nagrody

### Nawyki
- Dodaj codzienne nawyki które chcesz śledzić
- Każde wykonanie daje XP
- Śledź serie (streak) - kolejne dni wykonywania

### Nagrody
- Utwórz nagrody które możesz "kupić" za zebrane monety
- Motywuj się prawdziwymi nagrodami (np. "Obejrzyj odcinek serialu" za 10 monet)

### Obszary życia
Domyślnie aplikacja zawiera 6 obszarów:
- 💪 Zdrowie - ćwiczenia, dieta, sen
- 📚 Rozwój Osobisty - nauka, czytanie, kursy
- 💼 Kariera - projekty zawodowe, networking
- 💰 Finanse - oszczędzanie, inwestycje
- ❤️ Relacje - czas z bliskimi, spotkania
- 🎨 Hobby - pasje, kreatywność

## 🛠️ Struktura projektu

```
life-rpg/
│
├── app.py              # Główny plik aplikacji Flask
├── requirements.txt    # Zależności Python
├── life_rpg.db        # Baza danych SQLite (utworzona automatycznie)
│
└── templates/
    └── dashboard.html  # Szablon HTML (utworzony przez app.py)
```

## 📊 Baza danych

Aplikacja używa SQLite - lekkiej bazy danych która nie wymaga instalacji. 
Baza jest tworzona automatycznie przy pierwszym uruchomieniu.

### Modele danych:
- **User** - użytkownik z poziomem i statystykami
- **LifeArea** - obszary życia do śledzenia
- **Task** - zadania do wykonania
- **Habit** - codzienne nawyki
- **HabitCompletion** - rejestr wykonanych nawyków
- **Reward** - nagrody do zdobycia

## 🎨 Personalizacja

### Zmiana obszarów życia
W pliku `app.py` znajdź sekcję `default_areas` i dostosuj do swoich potrzeb:

```python
default_areas = [
    {'name': 'Zdrowie', 'icon': '💪', 'color': '#FF6B6B'},
    # Dodaj własne obszary...
]
```

### Zmiana wyglądu
Edytuj style CSS w szablonie `dashboard.html` aby dostosować kolory i wygląd.

### System poziomów
Domyślnie: 100 XP = 1 poziom. 
Możesz zmienić w funkcji `calculate_level_from_xp()`.

## 🔧 Rozszerzenia

Pomysły na dalszy rozwój:
- System achievementów/odznak
- Statystyki tygodniowe/miesięczne z wykresami
- Kategorie zadań (łatwe/średnie/trudne)
- System przyjaciół i rankingów
- Powiadomienia o nawykach
- Eksport danych
- Ciemny/jasny motyw
- Aplikacja mobilna

## ⚠️ Uwagi

- Aplikacja działa lokalnie na Twoim komputerze
- Dane są przechowywane w pliku `life_rpg.db`
- Dla produkcji zalecane jest użycie PostgreSQL zamiast SQLite
- Pamiętaj o regularnych backupach bazy danych

## 📝 Licencja

Projekt open source - możesz go dowolnie modyfikować i używać.

---

**Miłej gamifikacji życia! 🎮✨**