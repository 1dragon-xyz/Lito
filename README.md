# Vietnamese Text-to-Speech (TTS) Utility

A collection of Python scripts to convert Vietnamese text content from various formats into audio files using Microsoft Edge's online TTS services.

## Features

- Converts plain text, Markdown, and PDF files to speech.
- Uses the high-quality `vi-VN-HoaiMyNeural` (Female) voice by default.
- Simple, script-based approach for easy modification.

## Directory Structure

```
.
├── documents/          # Intended for your input/output files.
│   └── .gitkeep
├── personal-docs/      # A private folder (ignored by Git) for your use.
├── simple-tts/         # Contains all the core Python scripts.
└── README.md
```

## Setup & Installation

This project uses `uv` for package management.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/anhdhnguyen/tts-vietnamese.git
    cd tts-vietnamese
    ```

2.  **Install dependencies:**
    Make sure you have `uv` installed. If not, you can install it with `pip install uv`.
    ```bash
    uv pip sync --python 3.12 simple-tts/pyproject.toml
    ```

## How to Use

The scripts for file conversion require you to **manually edit the file paths** at the top of each script. It is recommended to place your files in the `documents` folder.

### 1. Interactive Text-to-Speech

For quick conversions of short text snippets.

-   **Run the script:**
    ```bash
    python simple-tts/main.py
    ```
-   You will be prompted to enter text. The output will be saved as `output.mp3` in the `simple-tts` directory and played automatically.

### 2. Convert a Markdown File to Audio

-   **Prepare your file:** Place your `.md` file in the `documents` folder.
-   **Edit the script:** Open `simple-tts/md_to_audio.py` and change the `SOURCE_FILE` and `OUTPUT_FILE` variables to point to your Markdown file and desired output MP3 file.

    ```python
    # Example configuration in md_to_audio.py
    SOURCE_FILE = r"d:\My Code\tts-vietnamese\documents\my-document.md"
    OUTPUT_FILE = r"d:\My Code\tts-vietnamese\documents\my-document.mp3"
    ```
-   **Run the script:**
    ```bash
    python simple-tts/md_to_audio.py
    ```

### 3. Convert a PDF File to Audio

-   **Prepare your file:** Place your `.pdf` file in the `documents` folder.
-   **Edit the script:** Open `simple-tts/pdf_to_audio.py` and change the `PDF_PATH` and `OUTPUT_FILE` variables.

    ```python
    # Example configuration in pdf_to_audio.py
    PDF_PATH = r"d:\My Code\tts-vietnamese\documents\my-report.pdf"
    OUTPUT_PATH = r"d:\My Code\tts-vietnamese\documents\my-report.mp3"
    ```
-   **Run the script:**
    ```bash
    python simple-tts/pdf_to_audio.py
    ```

## Contributing

Contributions are welcome! If you have ideas for improvements, such as adding command-line arguments instead of hardcoding paths, feel free to open an issue or submit a pull request.
