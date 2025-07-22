# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Job Offers Reader is a Flask web application that analyzes job offer PDFs to extract technology stacks and job descriptions. The application provides a user-friendly web interface for batch processing PDF files and saves results to JSON files for further analysis.

## Development Commands

### Running the Application
```bash
pip install -r requirements.txt
python app.py
```

The application runs on http://localhost:1289 with debug mode enabled.

### Dependencies
- Flask 2.3.3: Web framework
- PyPDF2 3.0.1: Primary PDF text extraction
- pdfplumber 0.9.0: Advanced PDF text extraction (fallback)
- python-dotenv 1.0.0: Environment variable management
- Werkzeug 2.3.7: WSGI utilities and file handling

## Architecture Overview

### Core Components

**JobOfferAnalyzer Class (app.py:19-108):**
- `extract_text_from_pdf()`: Dual-method PDF text extraction (pdfplumber primary, PyPDF2 fallback)
- `extract_tech_stack()`: Pattern matching for technology keywords across 5 categories
- `extract_job_description()`: Regex-based description section identification
- `analyze_pdf()`: Main analysis pipeline combining all extraction methods

**Technology Stack Detection:**
The analyzer recognizes technologies in 5 categories:
- Languages: Python, JavaScript, Java, C++, etc.
- Frameworks: React, Django, Flask, Angular, etc.
- Databases: MySQL, MongoDB, PostgreSQL, etc.
- Tools: Docker, Git, Jenkins, etc.
- Cloud: AWS, Azure, GCP, etc.

**Text Extraction Strategy:**
1. Primary: pdfplumber for complex layouts and tables
2. Fallback: PyPDF2 for simple text extraction
3. Error handling: Returns None if both methods fail

### Route Structure

**Main Application Routes:**
- `/` - Upload interface with drag-and-drop functionality
- `/upload` (POST) - PDF processing endpoint with AJAX response
- `/results` - List view of all analysis results
- `/results/<filename>` - Detailed view of specific analysis

**File Processing Pipeline:**
1. Secure filename generation via Werkzeug
2. Temporary file storage in `uploads/` directory
3. PDF analysis via JobOfferAnalyzer
4. JSON output to `outputs/` directory
5. Cleanup of temporary upload files

### Frontend Architecture

**Bootstrap 5 + jQuery Stack:**
- Responsive design with gradient styling
- Drag-and-drop file upload interface
- AJAX form submission with progress indicators
- Real-time file list updates and validation

**Key UI Features:**
- Multi-file selection and preview
- Upload progress visualization
- Expandable results display
- Tech stack badge visualization
- JSON data toggle view

### Data Flow

```
PDF Upload → Text Extraction → Pattern Analysis → JSON Output
     ↓              ↓               ↓              ↓
 Temp Storage → pdfplumber/PyPDF2 → Tech Stack + → Timestamped
                                    Description     JSON File
```

### JSON Output Structure

Each analysis produces a JSON file containing:
```json
{
  "filename": "job_offer.pdf",
  "tech_stack": {
    "languages": ["python", "javascript"],
    "frameworks": ["flask", "react"],
    "databases": ["postgresql"]
  },
  "job_description": "extracted description text...",
  "extracted_at": "2024-01-01T12:00:00",
  "text_length": 1500
}
```

## Directory Structure

```
job_offers_reader/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── uploads/              # Temporary PDF storage (auto-created)
├── output/               # JSON results storage (auto-created)
└── templates/            # Jinja2 templates
    ├── base.html         # Base template with Bootstrap
    ├── index.html        # Upload interface
    ├── results.html      # Results listing
    └── result_detail.html # Individual result view
```

## Implementation Details

### PDF Processing Strategy
- **Dual extraction approach** for maximum compatibility
- **Regex patterns with word boundaries** to avoid false tech stack matches
- **Content length validation** to ensure substantial job descriptions
- **Automatic file cleanup** after processing

### Tech Stack Detection Logic
Uses comprehensive keyword lists with case-insensitive matching and word boundary detection to avoid false positives (e.g., "java" in "javascript" won't match as Java language).

### Job Description Extraction
Employs multiple regex patterns to identify common job description sections:
- "Job Description:", "Description:", "About the Role:"
- "Role Description:", "Position Summary:"
- Falls back to first 500 characters if no structured section found

### Security Considerations
- **Secure filename generation** via Werkzeug's secure_filename()
- **File size limits** (16MB maximum)
- **PDF file type validation**
- **Temporary file cleanup** after processing
- **No file persistence** on server (uploads deleted immediately)

### Error Handling
- **Graceful PDF extraction failures** with fallback methods
- **Empty file detection** and user feedback
- **AJAX error responses** with descriptive messages
- **File validation** before processing