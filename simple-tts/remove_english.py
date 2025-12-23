import re
import os

FILE_PATH = r"D:\my-code\lito\documents\Đề xuất đầu tư dự án nghĩa trang Đà Nẵng.md"

def remove_english_glosses():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to remove parenthesized text containing only letters, spaces, and ampersands
    # This avoids removing things like (Giai đoạn 2) or (18ha)
    # Explanation:
    # \(          Literal opening parenthesis
    # [A-Za-z\s&-,]+  Character class: Letters (upper/lower), whitespace, &, -, and ,
    # \)+         Literal closing parenthesis (one or more, just in case)
    #
    # Added comma and hyphen to handle slightly more complex phrases if any, but sticking to plan 
    # [A-Za-z\s&] is safer. Let's strictly follow the plan first.
    # Plan said: [A-Za-z\s&]+
    
    pattern = r'\([A-Za-z\s&]+\)'
    
    # Let's verify what matches before replacing
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} matches to remove:")
    for m in matches[:10]:
        print(f"  - {m}")
    if len(matches) > 10:
        print(f"  ... and {len(matches)-10} more.")

    new_content = re.sub(pattern, '', content)
    
    # Also clean up double spaces that might result from removal
    new_content = re.sub(r'  +', ' ', new_content)

    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\nSuccessfully removed English glosses.")

if __name__ == "__main__":
    remove_english_glosses()