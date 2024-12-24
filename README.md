# FastAPI Invoice Application

An intelligent invoice processing system that uses FastAPI and Google's Gemini AI to extract data from Arabic invoices.

## Features

- Process invoices using Google's Gemini-1.5-flash AI model
- Support for multiple invoice types:
  - Al-Drsoni
  - Al-Othman
  - Al-Ifari
  - Almarai
  - AlsafiDanone
  - sadafco
- Accepts various file formats including PDF, images (JPEG, PNG, GIF, WEBP, HEIC)
- RESTful API endpoints
- Secure environment variable configuration
- Automatic upload folder management

## Prerequisites

- Python 3.7+
- Google API Key (for Gemini AI)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a .env file and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Project Structure

```
Invoice_FastAPI/
├── app.py              # Main application file
├── prompts/           # Invoice type-specific prompts
├── uploads/           # Directory for temporary file storage
├── requirements.txt   # Project dependencies
├── .env              # Environment variables
└── README.md
```

## API Endpoints

### GET /
- Health check endpoint
- Returns: `{"message": "Hello World..."}`

### POST /process_invoice
- Processes an invoice image and extracts data
- Request body:
  ```json
  {
    "image_url": "string",
    "invoice_type": "string"
  }
  ```
- Returns: JSON object with extracted invoice data

## Dependencies

Key dependencies include:
- FastAPI
- Google Generative AI
- Python-dotenv
- Uvicorn
- Pydantic
- Requests

## Running the Application

Start the FastAPI server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

API documentation can be accessed at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
