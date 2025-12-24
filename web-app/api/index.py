from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice: str

# Define supported voices
SUPPORTED_VOICES = [
    {"ShortName": "vi-VN-HoaiMyNeural", "FriendlyName": "Vietnamese (Female)", "Gender": "Female", "Locale": "vi-VN"},
    {"ShortName": "vi-VN-NamMinhNeural", "FriendlyName": "Vietnamese (Male)", "Gender": "Male", "Locale": "vi-VN"},
    {"ShortName": "en-US-AvaNeural", "FriendlyName": "English (Female)", "Gender": "Female", "Locale": "en-US"},
    {"ShortName": "en-US-AndrewNeural", "FriendlyName": "English (Male)", "Gender": "Male", "Locale": "en-US"},
    {"ShortName": "zh-CN-XiaoxiaoNeural", "FriendlyName": "Chinese (Female)", "Gender": "Female", "Locale": "zh-CN"},
    {"ShortName": "zh-CN-YunxiNeural", "FriendlyName": "Chinese (Male)", "Gender": "Male", "Locale": "zh-CN"},
    {"ShortName": "ja-JP-NanamiNeural", "FriendlyName": "Japanese (Female)", "Gender": "Female", "Locale": "ja-JP"},
    {"ShortName": "ja-JP-KeitaNeural", "FriendlyName": "Japanese (Male)", "Gender": "Male", "Locale": "ja-JP"},
]

@app.get("/api/voices")
async def get_voices():
    return SUPPORTED_VOICES

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        communicate = edge_tts.Communicate(request.text, request.voice)
        audio_data = b""
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return Response(content=audio_data, media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import UploadFile, File
from pypdf import PdfReader
import io
import re

def clean_text(text: str) -> str:
    # Basic cleaning
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.post("/api/extract-text")
async def extract_text(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename.lower()
        extracted_text = ""

        if filename.endswith(".pdf"):
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        else:
            # Assume text/md
            extracted_text = content.decode("utf-8")
        
        # Clean up
        final_text = clean_text(extracted_text)
        
        if not final_text:
             raise HTTPException(status_code=400, detail="Could not extract text from file")

        return {"text": final_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
