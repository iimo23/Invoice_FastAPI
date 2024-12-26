from fastapi import FastAPI, HTTPException
import google.generativeai as genai
import os
from dotenv import load_dotenv
import mimetypes
from typing import Optional
import requests
from pydantic import BaseModel
import uuid
import json

app = FastAPI()
UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

system_instruction = """You are a highly accurate and adaptable data extraction expert specializing in arabic invoice images. 
Given an invoice image, meticulously extract and return all relevant data in JSON format. 
Your response must be a valid JSON object with all the extracted information.
Do not include any explanatory text or markdown - only output valid JSON.
Ensure the output is comprehensive, error-free, and properly formatted JSON, regardless of the image's layout or format.
Adapt to different styles and structures to provide the most accurate and complete data extraction.
If the image quality is poor, apply image enhancement techniques to improve clarity."""

ALLOWED_MIME_TYPES = {
    "application/pdf", "text/plain", "text/html", "text/csv", "text/xml", "text/rtf",
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/heic", "image/heif",
}

ALLOWED_INVOICE_TYPES = {
    "Al-Drsoni", "Al-Othman", "Al-Ifari", "Almarai", "AlsafiDanone", "sadafco", "GlobalAr", "GlobalEn"
}

def allowed_file(filename: str) -> bool:
    mime_type = mimetypes.guess_type(filename)[0]
    return mime_type in ALLOWED_MIME_TYPES

def select_invoice_type(invoice_type: str) -> Optional[str]:
    if invoice_type not in ALLOWED_INVOICE_TYPES:
        return None
    
    filename = f"prompts/{invoice_type}.txt"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except (FileNotFoundError, UnicodeDecodeError):
        return None

class InvoiceRequest(BaseModel):
    image_url: str
    invoice_type: str

@app.get("/")
async def root():
    return {"message": "Hello World...mohammed!"}  

@app.post("/process_invoice")
async def process_invoice(request: InvoiceRequest):
    try:
        # Download image from URL
        response = requests.get(request.image_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to fetch image from URL"
            )
        
        # Get content type from response headers
        content_type = response.headers.get('content-type')
        if content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Please provide an image of type: {', '.join(ALLOWED_MIME_TYPES)}"
            )

        prompt = select_invoice_type(request.invoice_type)
        if not prompt:
            raise HTTPException(
                status_code=400,
                detail="Invalid invoice type. Please select a valid invoice type."
            )

        # Save the image temporarily with a unique filename
        temp_filename = f"{uuid.uuid4()}{mimetypes.guess_extension(content_type)}"
        file_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(response.content)

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
            ),
        )

        file_to_upload = genai.upload_file(file_path)
        response = model.generate_content([file_to_upload, "\n\n", prompt])
        
        # Clean up the temporary file
        os.remove(file_path)

        # Clean and parse the response text as JSON
        try:
            text = response.text
            # Remove markdown code blocks and any extra whitespace
            if "```" in text:
                # Extract content between code blocks
                text = text.split("```")[1]  # Get content after first ```
                if "json" in text:  # If json tag is present
                    text = text.replace("json", "", 1)  # Remove json tag
                text = text.split("```")[0]  # Get content before closing ```
            
            # Clean the text by removing any escape characters and extra whitespace
            text = text.strip().replace("\\n", "").replace("\\", "")
            
            # Parse the cleaned text as JSON
            json_response = json.loads(text)
            return json_response  # Return the JSON directly without wrapping in "result"

        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse response as JSON. Error: {str(e)}"
            )

    except Exception as e:
        # Clean up the file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
