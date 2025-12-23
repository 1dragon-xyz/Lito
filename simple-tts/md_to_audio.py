import asyncio
import edge_tts
import os
import re

# Configuration
SOURCE_FILE = r"D:\my-code\lito\personal-docs\Đề xuất đầu tư dự án nghĩa trang Đà Nẵng.md"
OUTPUT_FILE = r"D:\my-code\lito\personal-docs\Đề xuất đầu tư dự án nghĩa trang Đà Nẵng.mp3"
VOICE = "vi-VN-HoaiMyNeural"

def clean_markdown(text):
    # 1. Remove Headers (e.g. "## Title" -> "Title")
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # 2. Remove Bold/Italic (**text** or *text*)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # 3. Remove Links [text](url) -> text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    # 4. Remove horizontal rules
    text = re.sub(r'^-{3,}', '', text, flags=re.MULTILINE)
    
    # 5. Remove citations/footnotes roughly (like \.1 or .1 at end of sentences if they appear)
    # The file has "\.1" patterns. Let's fix escaped dots.
    text = text.replace(r'\.', '.') 
    
    # 6. Remove URLs that might remain
    text = re.sub(r'http[s]?://\S+', '', text)
    
    return text

async def generate_audio():
    print(f"Reading Markdown from: {SOURCE_FILE}")
    
    if not os.path.exists(SOURCE_FILE):
        print("Error: File not found.")
        return

    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Apply cleaning
    cleaned_text = clean_markdown(content)
    
    print(f"Original length: {len(content)}")
    print(f"Cleaned length: {len(cleaned_text)}")
    
    print("Generating audio (this may take a moment)...")
    
    communicate = edge_tts.Communicate(cleaned_text, VOICE)
    await communicate.save(OUTPUT_FILE)
    
    print(f"Success! Audio saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(generate_audio())