# Import standardowych bibliotek Pythona
import os  # System operacyjny - praca z plikami i folderami
import json  # Obsługa formatów JSON - zapis i odczyt danych strukturalnych
import re  # Wyrażenia regularne - wyszukiwanie wzorców w tekście
from datetime import datetime  # Operacje na datach i czasie
from pathlib import Path  # Nowoczesny sposób pracy ze ścieżkami plików

# Import bibliotek Flask - framework webowy do tworzenia aplikacji internetowych
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
# Flask - główna klasa aplikacji webowej
# render_template - renderowanie szablonów HTML
# request - dostęp do danych z żądań HTTP (formularze, pliki)
# jsonify - konwersja danych Pythona na format JSON dla API
# redirect - przekierowania między stronami
# url_for - generowanie URLów na podstawie nazw funkcji
# flash - komunikaty dla użytkownika (błędy, sukces)

from werkzeug.utils import secure_filename  # Bezpieczne nazwy plików - zabezpieczenie przed atakami

# Biblioteki do pracy z plikami PDF
import PyPDF2  # Pierwsza biblioteka do ekstrakcji tekstu z PDF
import pdfplumber  # Druga biblioteka PDF - lepsza dla skomplikowanych layoutów

# Biblioteki do integracji z zewnętrznymi API
from dotenv import load_dotenv  # Ładowanie zmiennych środowiskowych z pliku .env
import anthropic  # Klient API Claude AI dla analizy tekstu

# Ładowanie zmiennych środowiskowych z pliku .env
# Umożliwia przechowywanie kluczy API i innych wrażliwych danych poza kodem
load_dotenv()

# Tworzenie instancji aplikacji Flask
# __name__ przekazuje nazwę aktualnego modułu, co pomaga Flask znaleźć zasoby
app = Flask(__name__)

# Konfiguracja aplikacji Flask
app.config['SECRET_KEY'] = 'job-offers-reader-secret-key'  # Klucz do szyfrowania sesji i flash messages
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder na tymczasowe przesłane pliki PDF
app.config['OUTPUT_FOLDER'] = 'output'  # Folder na wyniki analizy w formacie JSON
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maksymalny rozmiar przesyłanego pliku (16MB)

# Tworzenie niezbędnych folderów dla aplikacji
# exist_ok=True oznacza, że nie wystąpi błąd jeśli folder już istnieje
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Folder uploads/ - tymczasowe pliki PDF
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)  # Folder output/ - wyniki analizy JSON
os.makedirs('templates', exist_ok=True)  # Folder templates/ - szablony HTML
os.makedirs('static', exist_ok=True)  # Folder static/ - CSS, JS, obrazy

# Inicjalizacja klienta Claude AI
# Blok try-except zapewnia graceful degradation - aplikacja działa nawet bez Claude
try:
    # Tworzenie klienta Claude z kluczem API ze zmiennych środowiskowych
    claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    CLAUDE_AVAILABLE = True  # Flaga informująca o dostępności Claude AI
    print("Claude API initialized successfully")  # Komunikat o sukcesie
except Exception as e:
    # Jeśli inicjalizacja nie powiodła się (brak klucza API, błąd połączenia)
    claude_client = None  # Brak klienta
    CLAUDE_AVAILABLE = False  # Flaga - Claude niedostępny
    print(f"Claude API not available: {e}")  # Komunikat o błędzie

class JobOfferAnalyzer:
    """
    Klasa do analizy plików PDF z ofertami pracy.
    Główne funkcje: ekstrakcja tekstu, identyfikacja stosu technologicznego i opisu stanowiska.
    
    Design Pattern: Używa wzorca Single Responsibility - jedna klasa odpowiada tylko za analizę PDF
    """
    
    def __init__(self):
        """
        Konstruktor klasy - inicjalizacja analizatora.
        Obecnie prosty, ale można rozszerzyć o konfigurację wzorców wyszukiwania.
        """
        # Prosty analizator dla konkretnego formatu ofert pracy
        # W przyszłości można dodać konfigurację wzorców regex lub słowniki technologii
        pass
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Ekstrakcja tekstu z PDF używając dwóch metod dla maksymalnej kompatybilności.
        
        Strategia: pdfplumber (główna metoda) + PyPDF2 (fallback)
        Zwraca: string z tekstem lub None przy błędzie
        """
        text_content = ""  # Zmienna do gromadzenia całego tekstu z PDF
        total_pages = 0    # Licznik stron do logowania postępu
        
        try:
            # Metoda 1: pdfplumber (lepsza dla skomplikowanych layoutów PDF)
            # Context manager (with) automatycznie zamyka plik po użyciu
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)  # Pobieranie liczby stron
                print(f"PDF has {total_pages} pages")  # Informacja o postępie
                
                # Iteracja przez wszystkie strony PDF
                # enumerate(pdf.pages, 1) - numeracja od 1 zamiast 0
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"Processing page {page_num}/{total_pages}")  # Postęp przetwarzania
                    page_text = page.extract_text()  # Ekstrakcja tekstu ze strony
                    
                    if page_text:  # Jeśli udało się wyekstraktować tekst
                        text_content += f"\n--- PAGE {page_num} ---\n"  # Separator stron
                        text_content += page_text + "\n"  # Dodanie tekstu strony
                        print(f"Page {page_num}: extracted {len(page_text)} characters")
                    else:
                        print(f"Page {page_num}: no text extracted")  # Brak tekstu na stronie
                        
        except Exception as e:
            print(f"pdfplumber failed: {e}")  # Logowanie błędu pierwszej metody
            
            # Metoda fallback 2: PyPDF2 - druga próba ekstrakcji tekstu
            # Używana gdy pdfplumber nie działa (np. uszkodzony PDF)
            try:
                print("Trying PyPDF2 as fallback...")  # Informacja o próbie fallback
                # Otwieranie pliku w trybie binarnym ('rb') - wymagane dla PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)  # Tworzenie readera PyPDF2
                    total_pages = len(pdf_reader.pages)  # Liczba stron
                    print(f"PyPDF2: PDF has {total_pages} pages")
                    
                    # Iteracja przez strony (podobnie jak w pdfplumber)
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        print(f"PyPDF2: Processing page {page_num}/{total_pages}")
                        page_text = page.extract_text()  # Ekstrakcja tekstu PyPDF2
                        
                        if page_text:  # Jeśli tekst został wyekstraktowany
                            text_content += f"\n--- PAGE {page_num} ---\n"  # Separator
                            text_content += page_text + "\n"  # Dodanie tekstu
                            print(f"PyPDF2: Page {page_num}: extracted {len(page_text)} characters")
                        else:
                            print(f"PyPDF2: Page {page_num}: no text extracted")
                            
            except Exception as e2:
                print(f"PyPDF2 also failed: {e2}")  # Obie metody zawiodły
                return None  # Zwracamy None - nie udało się wyekstraktować tekstu
        
        # Podsumowanie ekstrakcji tekstu
        print(f"Total text extracted: {len(text_content)} characters from {total_pages} pages")
        
        # Zwracanie wyniku: tekst bez białych znaków na początku/końcu lub None jeśli pusty
        # text_content.strip() usuwa spacje, tabulatory, nowe linie z początku i końca
        return text_content.strip() if text_content.strip() else None
    
    def extract_tech_stack(self, text):
        """
        Ekstrakcja stosu technologicznego z tekstu oferty pracy.
        Szuka zawartości między 'Tech stack' a ' Job d' używając regex.
        
        Args: text (str) - pełny tekst z PDF
        Returns: str - znaleziony stos technologiczny lub komunikat o błędzie
        """
        print("Extracting Tech Stack section...")  # Informacja o rozpoczęciu ekstrakcji
        
        # Wzorzec regex do znalezienia sekcji Tech Stack:
        # tech\s*stack - słowo "tech" + opcjonalne białe znaki + "stack"
        # [:\s]* - opcjonalne dwukropki i białe znaki po "Tech stack"
        # (.*?) - grupa przechwytująca (non-greedy) - zawartość stosu tech
        # (?:\s+job\s*d|$) - zakończenie: " job d" lub koniec tekstu
        pattern = r'tech\s*stack[:\s]*(.*?)(?:\s+job\s*d|$)'
        
        # re.search - znajdź pierwsze dopasowanie wzorca
        # re.DOTALL - . dopasowuje także znaki nowej linii
        # re.IGNORECASE - ignoruj wielkość liter
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:  # Jeśli znaleziono dopasowanie wzorca
            tech_content = match.group(1).strip()  # Wyciąg pierwszej grupy (zawartość)
            
            # Czyszczenie zawartości z nadmiarowych białych znaków:
            # re.sub(r'\s+', ' ', tech_content) - zamienia wielokrotne spacje/taby/nowe linie na pojedynczą spację
            tech_content = re.sub(r'\s+', ' ', tech_content)
            # Usuwanie separatorów stron dodanych podczas ekstrakcji PDF
            tech_content = re.sub(r'--- PAGE \d+ ---', ' ', tech_content)
            
            print(f"Found Tech Stack: {len(tech_content)} characters")  # Informacja o sukcesie
            return tech_content  # Zwracanie oczyszczonej zawartości
        else:
            print("No Tech Stack section found")  # Brak dopasowania wzorca
            return "Tech Stack section not found"  # Komunikat o błędzie
    
    def extract_job_description(self, text):
        """
        Ekstrakcja opisu stanowiska z tekstu oferty pracy.
        Szuka zawartości od 'Job d' do 'Apply Check similar'.
        
        Args: text (str) - pełny tekst z PDF
        Returns: str - znaleziony opis stanowiska lub komunikat o błędzie
        """
        print("Extracting Job Description section from 'Job d' to 'Apply Check similar'...")  # Log
        
        # Wzorzec regex do znalezienia opisu stanowiska:
        # job\s*d - słowo "job" + opcjonalne białe znaki + "d" (skrót od "description")
        # (.*?) - grupa przechwytująca (non-greedy) - zawartość opisu
        # (?:apply\s*check\s*similar|$) - zakończenie: "apply check similar" lub koniec tekstu
        pattern = r'job\s*d(.*?)(?:apply\s*check\s*similar|$)'
        
        # Wyszukiwanie wzorca (podobnie jak w extract_tech_stack)
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:  # Jeśli znaleziono dopasowanie wzorca regex
            job_content = match.group(1).strip()  # Wyciąg zawartości z pierwszej grupy
            
            # Proces czyszczenia tekstu (identyczny jak w extract_tech_stack):
            job_content = re.sub(r'\s+', ' ', job_content)  # Normalizacja białych znaków
            job_content = re.sub(r'--- PAGE \d+ ---', ' ', job_content)  # Usunięcie separatorów stron
            job_content = job_content.strip()  # Usunięcie białych znaków z początku/końca
            
            print(f"Found Job Description: {len(job_content)} characters")  # Sukces
            return job_content  # Zwróć oczyszczony opis
        else:
            print("No Job Description section found between 'Job d' and 'Apply Check similar'")  # Błąd
            return "Job Description section not found"  # Komunikat o niepowodzeniu
    
    def analyze_pdf(self, pdf_path):
        """
        Główna metoda analizy pojedynczego pliku PDF.
        Łączy wszystkie poprzednie metody w kompleksową analizę.
        
        Args: pdf_path (str) - ścieżka do pliku PDF
        Returns: dict - słownik z wynikami analizy lub None przy błędzie
        """
        # Krok 1: Ekstrakcja tekstu z PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:  # Jeśli nie udało się wyekstraktować tekstu
            return None  # Zwracamy None - analiza niemożliwa
        
        # Krok 2: Analiza tekstu - wyodrębnienie sekcji
        tech_stack = self.extract_tech_stack(text)  # Stos technologiczny
        job_description = self.extract_job_description(text)  # Opis stanowiska
        
        # Krok 3: Tworzenie struktury wynikowej (słownik)
        return {
            'filename': os.path.basename(pdf_path),  # Nazwa pliku bez ścieżki
            'tech_stack': tech_stack,  # Wyekstraktowany stos technologiczny
            'job_description': job_description,  # Wyekstraktowany opis
            'extracted_at': datetime.now().isoformat(),  # Timestamp analizy (format ISO)
            'text_length': len(text)  # Długość wyekstraktowanego tekstu
        }

# Tworzenie globalnej instancji analizatora PDF
# Używana przez wszystkie trasy aplikacji
analyzer = JobOfferAnalyzer()

# === TRASY FLASK (ROUTES) ===
# Trasy definiują endpointy HTTP i odpowiadające im funkcje

@app.route('/')  # Dekorator - trasa dla URL głównego (/)
def index():
    """
    Strona główna aplikacji - formularz upload pliku.
    HTTP GET na / zwraca szablon HTML z interfejsem uploadu.
    """
    # render_template szuka pliku w folderze templates/
    return render_template('index.html')

@app.route('/upload', methods=['POST'])  # Endpoint dla POST requests na /upload
def upload_files():
    """
    Główny endpoint do przetwarzania przesyłanych plików PDF.
    Obsługuje wielokrotny upload, analizę i zapis wyników do JSON.
    
    Returns: JSON response z wynikami analizy lub komunikatem błędu
    """
    try:  # Blok try-except dla obsługi błędów
        print("Upload request received")  # Log otrzymania żądania
        
        # Sprawdzenie czy żądanie zawiera pliki
        # request.files - MultiDict zawierający przesyłane pliki
        if 'files' not in request.files:
            print("No files in request")  # Log braku plików
            # jsonify() - konwertuje słownik Python na odpowiedź JSON
            return jsonify({'success': False, 'error': 'No files selected'})
        
        files = request.files.getlist('files')
        print(f"Found {len(files)} files in request")
        results = []
        
        for file in files:
            if file.filename == '':
                print("Empty filename, skipping")
                continue
            
            print(f"Processing file: {file.filename}")
            
            if file and file.filename.lower().endswith('.pdf'):
                try:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    print(f"Saving file to: {filepath}")
                    
                    file.save(filepath)
                    print(f"File saved successfully")
                    
                    # Analyze the PDF
                    print(f"Starting PDF analysis...")
                    analysis_result = analyzer.analyze_pdf(filepath)
                    
                    if analysis_result:
                        print(f"Analysis successful for {filename}")
                        results.append(analysis_result)
                    else:
                        print(f"Analysis failed for {filename}")
                    
                    # Clean up uploaded file
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"Cleaned up file: {filepath}")
                        
                except Exception as file_error:
                    print(f"Error processing file {file.filename}: {str(file_error)}")
                    # Try to clean up if file exists
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    except:
                        pass
            else:
                print(f"File {file.filename} is not a PDF, skipping")
        
        if results:
            try:
                # Save results to JSON file
                output_filename = f"job_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                print(f"Saving results to: {output_path}")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                print(f'Successfully analyzed {len(results)} PDF(s). Results saved to {output_filename}')
                return jsonify({
                    'success': True,
                    'results': results,
                    'output_file': output_filename
                })
            except Exception as save_error:
                print(f"Error saving results: {str(save_error)}")
                return jsonify({'success': False, 'error': f'Error saving results: {str(save_error)}'})
        else:
            print('No valid PDFs could be processed')
            return jsonify({'success': False, 'error': 'No valid PDFs could be processed'})
            
    except Exception as e:
        print(f"General upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/results')
def view_results():
    output_dir = Path(app.config['OUTPUT_FOLDER'])
    json_files = list(output_dir.glob('*.json'))
    
    files_info = []
    for json_file in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True):
        files_info.append({
            'filename': json_file.name,
            'size': json_file.stat().st_size,
            'modified': datetime.fromtimestamp(json_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return render_template('results.html', files=files_info)

@app.route('/results/<filename>')
def view_result_file(filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
    
    if not os.path.exists(filepath):
        flash('File not found')
        return redirect(url_for('view_results'))
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return render_template('result_detail.html', data=data, filename=filename)

@app.route('/process_folder', methods=['POST'])
def process_folder():
    """
    Process all PDF files from a specified folder path.
    """
    try:
        folder_path = request.form.get('folder_path', '').strip()
        
        if not folder_path or not os.path.exists(folder_path):
            return jsonify({'success': False, 'error': 'Invalid folder path'})
        
        print(f"Processing folder: {folder_path}")
        
        # Find all PDF files in the folder
        pdf_files = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(folder_path, filename))
        
        print(f"Found {len(pdf_files)} PDF files in folder")
        
        if not pdf_files:
            return jsonify({'success': False, 'error': 'No PDF files found in folder'})
        
        results = []
        processed_count = 0
        
        for pdf_path in pdf_files:
            try:
                print(f"Processing: {os.path.basename(pdf_path)}")
                analysis_result = analyzer.analyze_pdf(pdf_path)
                
                if analysis_result:
                    results.append(analysis_result)
                    processed_count += 1
                    print(f"Successfully processed: {os.path.basename(pdf_path)}")
                else:
                    print(f"Failed to process: {os.path.basename(pdf_path)}")
                    
            except Exception as file_error:
                print(f"Error processing {os.path.basename(pdf_path)}: {str(file_error)}")
                continue
        
        if results:
            # Save results to JSON file
            output_filename = f"folder_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f'Successfully processed {processed_count}/{len(pdf_files)} PDFs from folder')
            return jsonify({
                'success': True,
                'results': results,
                'output_file': output_filename,
                'processed_count': processed_count,
                'total_files': len(pdf_files)
            })
        else:
            return jsonify({'success': False, 'error': 'No PDF files could be processed'})
            
    except Exception as e:
        print(f"Folder processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/analyze_json')
def analyze_json():
    """
    Analyze all JSON files in the output folder and provide insights.
    """
    output_dir = Path(app.config['OUTPUT_FOLDER'])
    json_files = list(output_dir.glob('*.json'))
    
    if not json_files:
        return render_template('json_analysis.html', 
                             analysis={'total_files': 0, 'message': 'No JSON files found'})
    
    all_results = []
    tech_stacks = []
    job_descriptions = []
    filenames = []
    
    # Load all JSON files
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle both single results and arrays
            if isinstance(data, list):
                all_results.extend(data)
            else:
                all_results.append(data)
                
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
            continue
    
    # Extract data for analysis
    for result in all_results:
        if isinstance(result, dict):
            tech_stacks.append(result.get('tech_stack', ''))
            job_descriptions.append(result.get('job_description', ''))
            filenames.append(result.get('filename', 'unknown'))
    
    # Perform analysis
    analysis = perform_json_analysis(tech_stacks, job_descriptions, filenames)
    analysis['total_json_files'] = len(json_files)
    analysis['total_pdf_results'] = len(all_results)
    
    return render_template('json_analysis.html', analysis=analysis, results=all_results[:10])

def perform_json_analysis(tech_stacks, job_descriptions, filenames):
    """
    Analyze the collected tech stacks and job descriptions.
    """
    analysis = {}
    
    # Tech stack analysis
    tech_word_count = {}
    for tech_stack in tech_stacks:
        if tech_stack and tech_stack != "Tech Stack section not found":
            # Count technology mentions
            words = tech_stack.lower().split()
            for word in words:
                # Clean word
                word = word.strip('.,!?;:"()[]{}').lower()
                if len(word) > 2:  # Skip very short words
                    tech_word_count[word] = tech_word_count.get(word, 0) + 1
    
    # Get most common technologies
    common_tech = sorted(tech_word_count.items(), key=lambda x: x[1], reverse=True)[:20]
    
    # Job description analysis
    job_word_count = {}
    total_job_desc_length = 0
    valid_job_descriptions = 0
    
    for job_desc in job_descriptions:
        if job_desc and job_desc != "Job Description section not found":
            valid_job_descriptions += 1
            total_job_desc_length += len(job_desc)
            
            # Count important job-related words
            job_keywords = ['experience', 'work', 'team', 'develop', 'manage', 'project', 
                          'responsible', 'requirements', 'skills', 'knowledge', 'ability']
            
            words = job_desc.lower().split()
            for word in words:
                word = word.strip('.,!?;:"()[]{}').lower()
                if word in job_keywords:
                    job_word_count[word] = job_word_count.get(word, 0) + 1
    
    # Company analysis (from filenames)
    companies = {}
    for filename in filenames:
        # Try to extract company name (assuming format like "Job Title - Company.pdf")
        if ' - ' in filename:
            parts = filename.split(' - ')
            if len(parts) >= 2:
                company = parts[-1].replace('.pdf', '').strip()
                companies[company] = companies.get(company, 0) + 1
    
    common_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]
    
    analysis.update({
        'tech_analysis': {
            'most_common_technologies': common_tech,
            'total_tech_mentions': sum(tech_word_count.values()),
            'unique_technologies': len(tech_word_count)
        },
        'job_analysis': {
            'valid_descriptions': valid_job_descriptions,
            'avg_description_length': total_job_desc_length // max(valid_job_descriptions, 1),
            'common_job_keywords': sorted(job_word_count.items(), key=lambda x: x[1], reverse=True)
        },
        'company_analysis': {
            'total_companies': len(companies),
            'most_common_companies': common_companies
        },
        'summary': {
            'total_files_analyzed': len(filenames),
            'successful_extractions': valid_job_descriptions,
            'success_rate': f"{(valid_job_descriptions/len(filenames)*100):.1f}%" if filenames else "0%"
        }
    })
    
    return analysis

@app.route('/claude_analysis')
def claude_analysis():
    """
    Use Claude AI to analyze JSON data and provide insights.
    """
    if not CLAUDE_AVAILABLE:
        flash('Claude API is not configured. Please set your ANTHROPIC_API_KEY environment variable.')
        return redirect(url_for('analyze_json'))
    
    output_dir = Path(app.config['OUTPUT_FOLDER'])
    json_files = list(output_dir.glob('*.json'))
    
    if not json_files:
        flash('No JSON files found to analyze.')
        return redirect(url_for('analyze_json'))
    
    # Load all results
    all_results = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                all_results.extend(data)
            else:
                all_results.append(data)
        except Exception as e:
            print(f"Error reading {json_file}: {e}")
            continue
    
    if not all_results:
        flash('No valid data found in JSON files.')
        return redirect(url_for('analyze_json'))
    
    # Prepare data for Claude
    analysis_data = prepare_data_for_claude(all_results)
    
    try:
        # Call Claude API
        claude_insights = get_claude_insights(analysis_data)
        
        return render_template('claude_analysis.html', 
                             insights=claude_insights,
                             total_jobs=len(all_results))
    
    except Exception as e:
        flash(f'Error getting Claude analysis: {str(e)}')
        return redirect(url_for('analyze_json'))

def prepare_data_for_claude(results):
    """
    Prepare job offer data for Claude analysis.
    """
    tech_stacks = []
    job_descriptions = []
    companies = []
    
    for result in results:
        if isinstance(result, dict):
            tech_stack = result.get('tech_stack', '')
            job_desc = result.get('job_description', '')
            filename = result.get('filename', '')
            
            if tech_stack and tech_stack != "Tech Stack section not found":
                tech_stacks.append(tech_stack)
            
            if job_desc and job_desc != "Job Description section not found":
                job_descriptions.append(job_desc[:500])  # Limit length for API
            
            # Extract company from filename
            if ' - ' in filename:
                company = filename.split(' - ')[-1].replace('.pdf', '').strip()
                companies.append(company)
    
    return {
        'tech_stacks': tech_stacks[:20],  # Limit to prevent API overload
        'job_descriptions': job_descriptions[:20],
        'companies': list(set(companies)),
        'total_jobs': len(results)
    }

def get_claude_insights(data):
    """
    Get AI insights from Claude about job market data.
    """
    prompt = f"""
    Analyze this job market data from {data['total_jobs']} job offers and provide insights:

    TECHNOLOGY STACKS (sample of {len(data['tech_stacks'])}):
    {json.dumps(data['tech_stacks'][:10], indent=2)}

    JOB DESCRIPTIONS (sample of {len(data['job_descriptions'])}):
    {json.dumps(data['job_descriptions'][:5], indent=2)}

    COMPANIES:
    {', '.join(data['companies'][:10])}

    Please provide a comprehensive analysis covering:
    1. **Technology Trends**: What technologies are most in demand? Any emerging trends?
    2. **Skills Gap Analysis**: What skills appear most frequently vs. what might be missing?
    3. **Job Market Insights**: What can you infer about the job market from these descriptions?
    4. **Career Recommendations**: Based on this data, what advice would you give to job seekers?
    5. **Company Analysis**: What can you tell about the companies and their requirements?

    Format your response in clear sections with actionable insights.
    """
    
    try:
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",  # Using faster/cheaper model
            max_tokens=2000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return response.content[0].text
        
    except Exception as e:
        print(f"Claude API error: {e}")
        raise e

if __name__ == '__main__':
    app.run(host='localhost', port=1290, debug=True)