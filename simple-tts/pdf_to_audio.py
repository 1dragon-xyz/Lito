import asyncio
import edge_tts
import os
from pypdf import PdfReader

# Configuration
PDF_PATH = r"D:\my-code\lito\documents\Đề xuất đầu tư dự án nghĩa trang Đà Nẵng.pdf"
OUTPUT_PATH = r"D:\my-code\lito\documents\Đề xuất đầu tư dự án nghĩa trang Đà Nẵng.mp3"
VOICE = "vi-VN-HoaiMyNeural" # Female voice, usually good for reading

async def generate_audio_from_pdf():
    print(f"Reading PDF from: {PDF_PATH}")
    
    if not os.path.exists(PDF_PATH):
        print("Error: PDF file not found.")
        return

    # 1. Extract Text
    reader = PdfReader(PDF_PATH)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    
    # Text Cleaning Strategy:
    # 1. Replace zero-width spaces or other artifacts
    full_text = full_text.replace('\u200b', '')
    
    # 2. Fix broken lines from PDF (hyphenation at end of line)
    # This might not be common in Vietnamese but good to have
    full_text = full_text.replace('-\n', '')
    
    # 3. Merge lines that are part of the same sentence.
    # Logic: Replace single newline with space. 
    # To preserve paragraphs, we assume paragraphs are separated by double newlines.
    # However, pypdf often returns single newlines for everything. 
    # A simple robust fix for flowing text: replace ALL newlines with spaces, 
    # then rely on punctuation for pauses. 
    # But we want to keep distinct paragraphs if possible.
    
    # Let's try to normalize spaces first
    lines = full_text.split('\n')
    cleaned_text = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # If the line ends with valid punctuation, it might be the end of a sentence/paragraph.
        # Otherwise, implies continuation.
        if line[-1] in ['.', '!', '?', ':', ';']:
            cleaned_text += line + "\n" # Genuine break
        else:
            cleaned_text += line + " " # Continuation
            
    # Collapse multiple spaces
    import re
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Restore explicit punctuation breaks to helpful newlines for TTS pacing if needed,
    # but strictly speaking, punctuation is enough for the engine.
    # We will just print the stats.
    
    if not cleaned_text:
        print("Error: No text extracted from PDF.")
        return

    print(f"Original length: {len(full_text)}")
    print(f"Cleaned length: {len(cleaned_text)}")
    print(f"Preview: {cleaned_text[:500]}...")

    # 2. Convert to Audio
    communicate = edge_tts.Communicate(cleaned_text, VOICE)
    await communicate.save(OUTPUT_PATH)
    
    print(f"Success! Audio saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    asyncio.run(generate_audio_from_pdf())