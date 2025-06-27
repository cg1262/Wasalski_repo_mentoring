# XML - składnia i podstawy

## Co to jest XML?

XML (eXtensible Markup Language) to **znacznikowy język danych** używany do przechowywania i transportu danych w sposób czytelny dla człowieka i maszyny.

### Główne cechy:
- 📝 **Self-describing** - dane opisują same siebie
- 🔄 **Platform independent** - działa wszędzie
- 📊 **Structured** - hierarchiczna struktura danych
- ✅ **Validatable** - można sprawdzić poprawność
- 🌐 **Web standard** - W3C standard

## Podstawowa składnia XML

### Struktura dokumentu:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- To jest komentarz -->
<root>
    <element attribute="value">Content</element>
</root>
```

### Elementy podstawowe:

#### 1. **Deklaracja XML**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
```

#### 2. **Elementy (Tags)**:
```xml
<!-- Element z zawartością -->
<title>Tytuł książki</title>

<!-- Element pusty -->
<br/>
<image src="photo.jpg"/>

<!-- Element zagnieżdżony -->
<book>
    <title>Wiedźmin</title>
    <author>Andrzej Sapkowski</author>
</book>
```

#### 3. **Atrybuty**:
```xml
<book id="123" language="pl" published="1993">
    <title>Wiedźmin</title>
</book>

<!-- Atrybuty vs elementy -->
<!-- Jako atrybut -->
<person age="30" name="Jan"/>

<!-- Jako element -->
<person>
    <age>30</age>
    <name>Jan</name>
</person>
```

#### 4. **Komentarze**:
```xml
<!-- To jest komentarz -->
<!-- 
    Komentarz
    wielolinijkowy
-->

<book>
    <title>Tytuł</title> <!-- Komentarz inline -->
</book>
```

## Praktyczne przykłady

### 1. **Książka adresowa**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<addressBook>
    <contact id="1">
        <firstName>Jan</firstName>
        <lastName>Kowalski</lastName>
        <email>jan.kowalski@example.com</email>
        <phone type="mobile">+48 123 456 789</phone>
        <phone type="home">+48 22 123 4567</phone>
        <address>
            <street>Marszałkowska 1</street>
            <city>Warszawa</city>
            <postalCode>00-001</postalCode>
            <country>Polska</country>
        </address>
        <birthDate>1990-05-15</birthDate>
        <notes>Znajomy z pracy</notes>
    </contact>
    
    <contact id="2">
        <firstName>Anna</firstName>
        <lastName>Nowak</lastName>
        <email>anna.nowak@example.com</email>
        <phone type="mobile">+48 987 654 321</phone>
        <address>
            <street>Krakowska 10</street>
            <city>Kraków</city>
            <postalCode>30-001</postalCode>
            <country>Polska</country>
        </address>
        <birthDate>1985-12-03</birthDate>
    </contact>
</addressBook>
```

### 2. **Konfiguracja aplikacji**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <database>
        <connection>
            <host>localhost</host>
            <port>5432</port>
            <database>myapp</database>
            <username>dbuser</username>
            <password>secretpassword</password>
            <ssl enabled="true"/>
        </connection>
        <pool>
            <minConnections>5</minConnections>
            <maxConnections>20</maxConnections>
            <timeout>30</timeout>
        </pool>
    </database>
    
    <logging>
        <level>INFO</level>
        <file>/var/log/myapp.log</file>
        <maxSize>10MB</maxSize>
        <backup count="5"/>
    </logging>
    
    <features>
        <feature name="authentication" enabled="true"/>
        <feature name="caching" enabled="false"/>
        <feature name="monitoring" enabled="true"/>
    </features>
    
    <api>
        <baseUrl>https://api.example.com</baseUrl>
        <timeout>5000</timeout>
        <retries>3</retries>
        <keys>
            <key name="primary">abc123xyz</key>
            <key name="secondary">def456uvw</key>
        </keys>
    </api>
</configuration>
```

### 3. **Menu restauracji**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<menu restaurant="Bistro Roma" date="2024-01-15">
    <category name="Przystawki">
        <dish id="A001">
            <name lang="pl">Bruschetta</name>
            <name lang="en">Bruschetta</name>
            <description>Grzanki z pomidorami, bazylią i mozzarellą</description>
            <price currency="PLN">18.00</price>
            <allergens>
                <allergen>gluten</allergen>
                <allergen>dairy</allergen>
            </allergens>
            <vegetarian>true</vegetarian>
        </dish>
        
        <dish id="A002">
            <name lang="pl">Carpaccio z wołowiny</name>
            <name lang="en">Beef Carpaccio</name>
            <description>Cienkie plasterki surowej wołowiny z rukolą</description>
            <price currency="PLN">28.00</price>
            <allergens/>
            <vegetarian>false</vegetarian>
            <spicy level="1"/>
        </dish>
    </category>
    
    <category name="Dania główne">
        <dish id="M001">
            <name lang="pl">Spaghetti Carbonara</name>
            <name lang="en">Spaghetti Carbonara</name>
            <description>Makaron z boczkiem, jajkiem i parmezanem</description>
            <price currency="PLN">32.00</price>
            <allergens>
                <allergen>gluten</allergen>
                <allergen>eggs</allergen>
                <allergen>dairy</allergen>
            </allergens>
            <vegetarian>false</vegetarian>
            <preparationTime>15</preparationTime>
        </dish>
    </category>
    
    <category name="Desery">
        <dish id="D001">
            <name lang="pl">Tiramisu</name>
            <name lang="en">Tiramisu</name>
            <description>Tradycyjny włoski deser z mascarpone</description>
            <price currency="PLN">22.00</price>
            <allergens>
                <allergen>eggs</allergen>
                <allergen>dairy</allergen>
                <allergen>alcohol</allergen>
            </allergens>
            <vegetarian>true</vegetarian>
        </dish>
    </category>
</menu>
```

## Zasady składni XML

### 1. **Well-formed XML** - podstawowe zasady:
```xml
<!-- ✅ DOBRZE -->
<root>
    <element>content</element>
</root>

<!-- ❌ ŹLE - brak closing tag -->
<root>
    <element>content
</root>

<!-- ❌ ŹLE - nieprawidłowa kolejność tagów -->
<root>
    <element>content</root>
</element>

<!-- ❌ ŹLE - case sensitive -->
<Root>
    <element>content</element>
</root>
```

### 2. **Reguły nazewnictwa**:
```xml
<!-- ✅ DOBRZE -->
<firstName>Jan</firstName>
<first-name>Jan</first-name>
<first_name>Jan</first_name>
<name2>Jan</name2>

<!-- ❌ ŹLE -->
<2name>Jan</2name>        <!-- nie może zaczynać się od cyfry -->
<first name>Jan</first>   <!-- brak spacji -->
<first.name>Jan</first.name> <!-- kropka tylko w namespace -->
```

### 3. **Znaki specjalne**:
```xml
<!-- Encoded entities -->
<message>
    Cena: 100 &lt; 200        <!-- < -->
    Firma: Johnson &amp; Sons   <!-- & -->
    Cytat: &quot;Hello&quot;      <!-- " -->
    Apostrofe: &apos;world&apos; <!-- ' -->
    Większe: 200 &gt; 100     <!-- > -->
</message>

<!-- CDATA section - tekst dosłowny -->
<code>
    <![CDATA[
        if (x < y && y > z) {
            print("Hello & Goodbye");
        }
    ]]>
</code>
```

## Namespaces (przestrzenie nazw)

### Podstawy namespace:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:book="http://example.com/book"
      xmlns:author="http://example.com/author">
    
    <book:title>Wiedźmin</book:title>
    <book:isbn>978-83-7469-000-0</book:isbn>
    
    <author:name>Andrzej Sapkowski</author:name>
    <author:nationality>Polish</author:nationality>
</root>
```

### Default namespace:
```xml
<library xmlns="http://example.com/library">
    <book>  <!-- należy do namespace library -->
        <title>Książka</title>
        <author>Autor</author>
    </book>
</library>
```

## XML Schema (XSD) - walidacja

### Przykład schematu:
```xml
<!-- books.xsd -->
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://example.com/books"
           xmlns="http://example.com/books">

    <xs:element name="library">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="book" maxOccurs="unbounded">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="title" type="xs:string"/>
                            <xs:element name="author" type="xs:string"/>
                            <xs:element name="year" type="xs:int"/>
                            <xs:element name="price" type="xs:decimal"/>
                        </xs:sequence>
                        <xs:attribute name="id" type="xs:string" use="required"/>
                        <xs:attribute name="genre" type="genreType"/>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>

    <xs:simpleType name="genreType">
        <xs:restriction base="xs:string">
            <xs:enumeration value="fiction"/>
            <xs:enumeration value="non-fiction"/>
            <xs:enumeration value="science"/>
            <xs:enumeration value="history"/>
        </xs:restriction>
    </xs:simpleType>

</xs:schema>
```

### XML zgodny ze schematem:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<library xmlns="http://example.com/books"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://example.com/books books.xsd">
    
    <book id="B001" genre="fiction">
        <title>Wiedźmin</title>
        <author>Andrzej Sapkowski</author>
        <year>1993</year>
        <price>29.99</price>
    </book>
    
    <book id="B002" genre="science">
        <title>Krótka historia czasu</title>
        <author>Stephen Hawking</author>
        <year>1988</year>
        <price>39.99</price>
    </book>
    
</library>
```

## Parsowanie XML w różnych językach

### Python:
```python
import xml.etree.ElementTree as ET

# Parsowanie z pliku
tree = ET.parse('books.xml')
root = tree.getroot()

# Parsowanie z stringa
xml_string = """
<books>
    <book id="1">
        <title>Wiedźmin</title>
        <author>Sapkowski</author>
    </book>
</books>
"""
root = ET.fromstring(xml_string)

# Znajdowanie elementów
for book in root.findall('book'):
    title = book.find('title').text
    author = book.find('author').text
    book_id = book.get('id')
    print(f"Book {book_id}: {title} by {author}")

# Tworzenie XML
books = ET.Element('books')
book = ET.SubElement(books, 'book', id='1')
ET.SubElement(book, 'title').text = 'Wiedźmin'
ET.SubElement(book, 'author').text = 'Sapkowski'

# Zapisz do pliku
tree = ET.ElementTree(books)
tree.write('output.xml', encoding='utf-8', xml_declaration=True)
```

### JavaScript (Browser/Node.js):
```javascript
// Browser - DOMParser
const xmlString = `
<books>
    <book id="1">
        <title>Wiedźmin</title>
        <author>Sapkowski</author>
    </book>
</books>`;

const parser = new DOMParser();
const xmlDoc = parser.parseFromString(xmlString, "text/xml");

// Znajdowanie elementów
const books = xmlDoc.getElementsByTagName('book');
for (let book of books) {
    const title = book.getElementsByTagName('title')[0].textContent;
    const author = book.getElementsByTagName('author')[0].textContent;
    const id = book.getAttribute('id');
    console.log(`Book ${id}: ${title} by ${author}`);
}

// Node.js - xml2js
const xml2js = require('xml2js');

xml2js.parseString(xmlString, (err, result) => {
    if (!err) {
        console.log(JSON.stringify(result, null, 2));
    }
});
```

### Java:
```java
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Element;

// Parsowanie XML
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
DocumentBuilder builder = factory.newDocumentBuilder();
Document doc = builder.parse("books.xml");

// Normalizacja
doc.getDocumentElement().normalize();

// Znajdowanie elementów
NodeList bookList = doc.getElementsByTagName("book");

for (int i = 0; i < bookList.getLength(); i++) {
    Element book = (Element) bookList.item(i);
    String id = book.getAttribute("id");
    String title = book.getElementsByTagName("title").item(0).getTextContent();
    String author = book.getElementsByTagName("author").item(0).getTextContent();
    
    System.out.println("Book " + id + ": " + title + " by " + author);
}
```

## XML vs inne formaty

### XML vs JSON:
```xml
<!-- XML -->
<person>
    <name>Jan Kowalski</name>
    <age>30</age>
    <city>Warszawa</city>
    <skills>
        <skill>Java</skill>
        <skill>Python</skill>
    </skills>
</person>
```

```json
// JSON
{
    "person": {
        "name": "Jan Kowalski",
        "age": 30,
        "city": "Warszawa",
        "skills": ["Java", "Python"]
    }
}
```

| Aspekt | XML | JSON |
|--------|-----|------|
| **Czytelność** | Verbose | Zwięzły |
| **Rozmiar** | Większy | Mniejszy |
| **Atrybuty** | ✅ Tak | ❌ Nie |
| **Komentarze** | ✅ Tak | ❌ Nie |
| **Schema** | XSD | JSON Schema |
| **Namespace** | ✅ Tak | ❌ Nie |
| **Web APIs** | Rzadko | Często |

## Zastosowania XML

### ✅ Gdzie XML jest używany:
- **Web Services** - SOAP APIs
- **Konfiguracja** - Spring, Maven, Ant
- **Dokumenty** - DOCX, SVG, RSS
- **Bazy danych** - XML databases
- **Enterprise** - EDI, B2B communication
- **Android** - Layout files
- **Microsoft Office** - DOCX, XLSX

### Przykłady z życia:

#### Android Layout:
```xml
<!-- activity_main.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        android:textSize="24sp" />

    <Button
        android:id="@+id/button"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Click me" />

</LinearLayout>
```

#### Maven pom.xml:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.8.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
</project>
```

## Podsumowanie

### ✅ Używaj XML gdy:
- Potrzebujesz atrybutów i namespace
- Wymagana jest walidacja schema
- Enterprise/B2B integration
- Konfiguracja złożonych aplikacji
- Zgodność z legacy systems

### ❌ Unikaj XML gdy:
- Proste API REST
- Ograniczona przepustowość
- Mobile applications
- Real-time komunikacja
- Preferujesz prostotę

**XML = Powerful but verbose data format** 📄