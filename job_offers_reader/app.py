import os
import json
import re
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import PyPDF2
import pdfplumber
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'job-offers-reader-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# Initialize Claude client
try:
    claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    CLAUDE_AVAILABLE = True
    print("Claude API initialized successfully")
except Exception as e:
    claude_client = None
    CLAUDE_AVAILABLE = False
    print(f"Claude API not available: {e}")

class JobOfferAnalyzer:
    """
    Analyzes job offer PDFs to extract tech stack and job descriptions.
    """
    
    def __init__(self):
        # Simple analyzer for specific job offer format
        pass
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text content from PDF using multiple methods for better accuracy.
        """
        text_content = ""
        total_pages = 0
        
        try:
            # Method 1: pdfplumber (better for complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"PDF has {total_pages} pages")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"Processing page {page_num}/{total_pages}")
                    page_text = page.extract_text()
                    if page_text:
                        text_content += f"\n--- PAGE {page_num} ---\n"
                        text_content += page_text + "\n"
                        print(f"Page {page_num}: extracted {len(page_text)} characters")
                    else:
                        print(f"Page {page_num}: no text extracted")
                        
        except Exception as e:
            print(f"pdfplumber failed: {e}")
            
            # Fallback Method 2: PyPDF2
            try:
                print("Trying PyPDF2 as fallback...")
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    total_pages = len(pdf_reader.pages)
                    print(f"PyPDF2: PDF has {total_pages} pages")
                    
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        print(f"PyPDF2: Processing page {page_num}/{total_pages}")
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- PAGE {page_num} ---\n"
                            text_content += page_text + "\n"
                            print(f"PyPDF2: Page {page_num}: extracted {len(page_text)} characters")
                        else:
                            print(f"PyPDF2: Page {page_num}: no text extracted")
                            
            except Exception as e2:
                print(f"PyPDF2 also failed: {e2}")
                return None
        
        print(f"Total text extracted: {len(text_content)} characters from {total_pages} pages")
        return text_content.strip() if text_content.strip() else None
    
    def extract_tech_stack(self, text):
        """
        Extract everything between 'Tech stack' and ' Job d' sections.
        """
        print("Extracting Tech Stack section...")
        
        # Look for content between "Tech stack" and " Job d"
        pattern = r'tech\s*stack[:\s]*(.*?)(?:\s+job\s*d|$)'
        
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            tech_content = match.group(1).strip()
            # Clean up the content
            tech_content = re.sub(r'\s+', ' ', tech_content)
            tech_content = re.sub(r'--- PAGE \d+ ---', ' ', tech_content)
            print(f"Found Tech Stack: {len(tech_content)} characters")
            return tech_content
        else:
            print("No Tech Stack section found")
            return "Tech Stack section not found"
    
    def extract_job_description(self, text):
        """
        Extract Job description starting from 'Job d' until 'Apply Check similar'.
        """
        print("Extracting Job Description section from 'Job d' to 'Apply Check similar'...")
        
        # Look for content between "Job d" and "Apply Check similar"
        pattern = r'job\s*d(.*?)(?:apply\s*check\s*similar|$)'
        
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            job_content = match.group(1).strip()
            # Clean up the content
            job_content = re.sub(r'\s+', ' ', job_content)
            job_content = re.sub(r'--- PAGE \d+ ---', ' ', job_content)
            job_content = job_content.strip()
            
            print(f"Found Job Description: {len(job_content)} characters")
            return job_content
        else:
            print("No Job Description section found between 'Job d' and 'Apply Check similar'")
            return "Job Description section not found"
    
    def analyze_pdf(self, pdf_path):
        """
        Analyze a single PDF file and extract tech stack and job description.
        """
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return None
        
        tech_stack = self.extract_tech_stack(text)
        job_description = self.extract_job_description(text)
        
        return {
            'filename': os.path.basename(pdf_path),
            'tech_stack': tech_stack,
            'job_description': job_description,
            'extracted_at': datetime.now().isoformat(),
            'text_length': len(text)
        }

analyzer = JobOfferAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        print("Upload request received")
        
        if 'files' not in request.files:
            print("No files in request")
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