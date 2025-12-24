from fastapi import FastAPI, HTTPException, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google.cloud import texttospeech
from pypdf import PdfReader
import os
import io
import re
import json

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service kill switch - can be disabled via environment variable
SERVICE_ENABLED = os.environ.get("SERVICE_ENABLED", "true").lower() == "true"

# Character limit for demo (HOOK: enough to demo, triggers download desire)
MAX_CHARS = 1500

# Initialize Google Cloud TTS client
# For Vercel: credentials from environment variable
credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if credentials_json:
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(credentials_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f.name

client = texttospeech.TextToSpeechClient()

class TTSRequest(BaseModel):
    text: str
    voice: str

# 20 languages with male + female voices (40 total)
SUPPORTED_VOICES = [
    # Vietnamese
    {"id": "vi-VN-Standard-A", "name": "Vietnamese (Female)", "gender": "Female", "locale": "vi-VN"},
    {"id": "vi-VN-Standard-B", "name": "Vietnamese (Male)", "gender": "Male", "locale": "vi-VN"},
    # English (US)
    {"id": "en-US-Neural2-C", "name": "English US (Female)", "gender": "Female", "locale": "en-US"},
    {"id": "en-US-Neural2-D", "name": "English US (Male)", "gender": "Male", "locale": "en-US"},
    # Spanish
    {"id": "es-ES-Neural2-A", "name": "Spanish (Female)", "gender": "Female", "locale": "es-ES"},
    {"id": "es-ES-Neural2-B", "name": "Spanish (Male)", "gender": "Male", "locale": "es-ES"},
    # Chinese (Mandarin)
    {"id": "cmn-CN-Standard-A", "name": "Chinese (Female)", "gender": "Female", "locale": "cmn-CN"},
    {"id": "cmn-CN-Standard-B", "name": "Chinese (Male)", "gender": "Male", "locale": "cmn-CN"},
    # Arabic
    {"id": "ar-XA-Standard-A", "name": "Arabic (Female)", "gender": "Female", "locale": "ar-XA"},
    {"id": "ar-XA-Standard-B", "name": "Arabic (Male)", "gender": "Male", "locale": "ar-XA"},
    # Portuguese (Brazil)
    {"id": "pt-BR-Neural2-A", "name": "Portuguese BR (Female)", "gender": "Female", "locale": "pt-BR"},
    {"id": "pt-BR-Neural2-B", "name": "Portuguese BR (Male)", "gender": "Male", "locale": "pt-BR"},
    # French
    {"id": "fr-FR-Neural2-A", "name": "French (Female)", "gender": "Female", "locale": "fr-FR"},
    {"id": "fr-FR-Neural2-B", "name": "French (Male)", "gender": "Male", "locale": "fr-FR"},
    # German
    {"id": "de-DE-Neural2-A", "name": "German (Female)", "gender": "Female", "locale": "de-DE"},
    {"id": "de-DE-Neural2-B", "name": "German (Male)", "gender": "Male", "locale": "de-DE"},
    # Japanese
    {"id": "ja-JP-Neural2-B", "name": "Japanese (Female)", "gender": "Female", "locale": "ja-JP"},
    {"id": "ja-JP-Neural2-C", "name": "Japanese (Male)", "gender": "Male", "locale": "ja-JP"},
    # Russian
    {"id": "ru-RU-Standard-A", "name": "Russian (Female)", "gender": "Female", "locale": "ru-RU"},
    {"id": "ru-RU-Standard-B", "name": "Russian (Male)", "gender": "Male", "locale": "ru-RU"},
    # Korean
    {"id": "ko-KR-Neural2-A", "name": "Korean (Female)", "gender": "Female", "locale": "ko-KR"},
    {"id": "ko-KR-Neural2-C", "name": "Korean (Male)", "gender": "Male", "locale": "ko-KR"},
    # Italian
    {"id": "it-IT-Neural2-A", "name": "Italian (Female)", "gender": "Female", "locale": "it-IT"},
    {"id": "it-IT-Neural2-C", "name": "Italian (Male)", "gender": "Male", "locale": "it-IT"},
    # Turkish
    {"id": "tr-TR-Standard-A", "name": "Turkish (Female)", "gender": "Female", "locale": "tr-TR"},
    {"id": "tr-TR-Standard-B", "name": "Turkish (Male)", "gender": "Male", "locale": "tr-TR"},
    # Dutch
    {"id": "nl-NL-Standard-A", "name": "Dutch (Female)", "gender": "Female", "locale": "nl-NL"},
    {"id": "nl-NL-Standard-B", "name": "Dutch (Male)", "gender": "Male", "locale": "nl-NL"},
    # Polish
    {"id": "pl-PL-Standard-A", "name": "Polish (Female)", "gender": "Female", "locale": "pl-PL"},
    {"id": "pl-PL-Standard-B", "name": "Polish (Male)", "gender": "Male", "locale": "pl-PL"},
    # Indonesian
    {"id": "id-ID-Standard-A", "name": "Indonesian (Female)", "gender": "Female", "locale": "id-ID"},
    {"id": "id-ID-Standard-B", "name": "Indonesian (Male)", "gender": "Male", "locale": "id-ID"},
    # Hindi
    {"id": "hi-IN-Neural2-A", "name": "Hindi (Female)", "gender": "Female", "locale": "hi-IN"},
    {"id": "hi-IN-Neural2-B", "name": "Hindi (Male)", "gender": "Male", "locale": "hi-IN"},
    # Thai
    {"id": "th-TH-Standard-A", "name": "Thai (Female)", "gender": "Female", "locale": "th-TH"},
    {"id": "th-TH-Neural2-C", "name": "Thai (Male)", "gender": "Male", "locale": "th-TH"},
    # Hebrew
    {"id": "he-IL-Standard-A", "name": "Hebrew (Female)", "gender": "Female", "locale": "he-IL"},
    {"id": "he-IL-Standard-B", "name": "Hebrew (Male)", "gender": "Male", "locale": "he-IL"},
    # Swedish
    {"id": "sv-SE-Standard-A", "name": "Swedish (Female)", "gender": "Female", "locale": "sv-SE"},
    {"id": "sv-SE-Standard-B", "name": "Swedish (Male)", "gender": "Male", "locale": "sv-SE"},
]

@app.get("/api/voices")
async def get_voices():
    return SUPPORTED_VOICES

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    # Check if service is enabled (kill switch)
    if not SERVICE_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="🚫 Demo service temporarily unavailable due to high usage. "
                   "Download Lito Desktop for unlimited, free text-to-speech: "
                   "https://github.com/1dragon-xyz/lito/releases"
        )
    
    text = request.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(text) > MAX_CHARS:
        raise HTTPException(
            status_code=400, 
            detail=f"Text exceeds {MAX_CHARS} character limit. Download Lito Desktop for unlimited use."
        )
    
    # Validate voice
    valid_voice_ids = [v["id"] for v in SUPPORTED_VOICES]
    if request.voice not in valid_voice_ids:
        raise HTTPException(status_code=400, detail="Invalid voice selected")
    
    # Get locale from voice id
    voice_info = next((v for v in SUPPORTED_VOICES if v["id"] == request.voice), None)
    language_code = voice_info["locale"] if voice_info else "en-US"

    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=request.voice
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return Response(content=response.audio_content, media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def clean_text(text: str) -> str:
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
        
        # Truncate if over limit
        if len(final_text) > MAX_CHARS:
            final_text = final_text[:MAX_CHARS]

        return {"text": final_text, "truncated": len(extracted_text) > MAX_CHARS}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


# Mount static files for local development (MUST be after all API routes)
# In production (Vercel), this is handled by vercel.json rewrites
import os.path
if os.path.exists("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="static")
