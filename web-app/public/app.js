document.addEventListener('DOMContentLoaded', () => {
    // Constants (HOOK: enough to demo, triggers download desire)
    const MAX_CHARS = 1500;

    // Elements
    const voiceSelect = document.getElementById('voice-select');
    const textInput = document.getElementById('text-input');
    const convertBtn = document.getElementById('convert-btn');
    const statusDiv = document.getElementById('status');
    const audioPlayer = document.getElementById('audio-player');
    const charCount = document.getElementById('char-count');

    // Tab Elements
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const fileNameDisplay = document.getElementById('file-name-display');

    let currentMode = 'text';
    let selectedFile = null;

    // --- 1. Initialization & UI Logic ---

    // Load Voices
    async function loadVoices() {
        try {
            const response = await fetch('/api/voices');
            const voices = await response.json();

            voiceSelect.innerHTML = '';
            voices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.id;
                option.textContent = voice.name;
                voiceSelect.appendChild(option);
            });
        } catch (error) {
            statusDiv.textContent = "Error loading voices.";
            statusDiv.style.color = "red";
        }
    }
    loadVoices();

    // Character Counter
    textInput.addEventListener('input', () => {
        const count = textInput.value.length;
        charCount.textContent = count.toLocaleString();

        if (count > MAX_CHARS) {
            charCount.parentElement.classList.add('over-limit');
        } else if (count > MAX_CHARS * 0.9) {
            charCount.parentElement.classList.add('near-limit');
            charCount.parentElement.classList.remove('over-limit');
        } else {
            charCount.parentElement.classList.remove('near-limit', 'over-limit');
        }
    });

    // Tab Switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.style.display = 'none');

            btn.classList.add('active');
            const target = btn.dataset.tab;
            document.getElementById(`${target}-tab`).style.display = 'block';
            currentMode = target;
        });
    });

    // File Upload Handling
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        selectedFile = file;
        fileNameDisplay.textContent = `Selected: ${file.name}`;
    }

    // --- 2. Core Logic ---

    // Download Button (created dynamically)
    const downloadBtn = document.createElement('button');
    downloadBtn.textContent = "Download Full Audio";
    downloadBtn.style.marginTop = "10px";
    downloadBtn.style.backgroundColor = "#10b981";
    downloadBtn.style.display = "none";
    document.querySelector('.action-group').appendChild(downloadBtn);

    // Play Full Audio Button (created dynamically)
    const playFullBtn = document.createElement('button');
    playFullBtn.textContent = "Play Full Audio";
    playFullBtn.style.marginTop = "10px";
    playFullBtn.style.backgroundColor = "#3b82f6";
    playFullBtn.style.display = "none";
    document.querySelector('.action-group').insertBefore(playFullBtn, downloadBtn);


    function splitIntoChunks(text, maxChars = 800) {
        const sentences = text.match(/[^.!?]+[.!?]+(?:\s+|$)|[^.!?]+$/g) || [text];
        const chunks = [];
        let currentChunk = "";

        for (let sentence of sentences) {
            if ((currentChunk + sentence).length > maxChars && currentChunk !== "") {
                chunks.push(currentChunk.trim());
                currentChunk = sentence;
            } else {
                currentChunk += (currentChunk === "" ? "" : " ") + sentence;
            }
        }
        if (currentChunk) chunks.push(currentChunk.trim());
        return chunks;
    }

    async function fetchAudioChunk(text, voice) {
        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, voice }),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch audio');
        }
        return await response.blob();
    }

    async function extractTextFromFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/extract-text', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to extract text');
        }

        const data = await response.json();
        if (data.truncated) {
            statusDiv.textContent = `Note: Text was truncated to ${MAX_CHARS.toLocaleString()} characters.`;
            statusDiv.style.color = "#f59e0b";
        }
        return data.text;
    }

    // --- Main Action ---
    convertBtn.addEventListener('click', async () => {
        let textToConvert = "";
        const voice = voiceSelect.value;

        statusDiv.textContent = "";
        downloadBtn.style.display = "none";
        playFullBtn.style.display = "none";
        audioPlayer.hidden = true;
        audioPlayer.pause();

        statusDiv.style.color = "#94a3b8";

        try {
            convertBtn.disabled = true;
            convertBtn.textContent = "Processing...";
            statusDiv.textContent = "Reading input...";

            if (currentMode === 'text') {
                textToConvert = textInput.value.trim();
                if (!textToConvert) throw new Error("Please enter some text.");
                if (textToConvert.length > MAX_CHARS) {
                    throw new Error(`Text exceeds ${MAX_CHARS.toLocaleString()} character limit. Download Lito Desktop for unlimited use.`);
                }
            } else {
                if (!selectedFile) throw new Error("Please select a file.");
                textToConvert = await extractTextFromFile(selectedFile);
            }

            // Chunking
            const chunks = splitIntoChunks(textToConvert);
            statusDiv.textContent = "Generating Preview...";

            // Process Chunk 1 for Preview
            const firstChunkBlob = await fetchAudioChunk(chunks[0], voice);
            const firstChunkUrl = URL.createObjectURL(firstChunkBlob);

            // Play Preview
            audioPlayer.src = firstChunkUrl;
            audioPlayer.hidden = false;
            audioPlayer.play();

            statusDiv.textContent = "Playing Preview... (Generating full audio in background)";
            statusDiv.style.color = "#3b82f6";

            // Background Process Rest
            if (chunks.length > 1) {
                const audioBlobs = [firstChunkBlob];

                const promises = chunks.slice(1).map(chunk => fetchAudioChunk(chunk, voice));
                const remainingBlobs = await Promise.all(promises);
                audioBlobs.push(...remainingBlobs);

                const fullAudioBlob = new Blob(audioBlobs, { type: 'audio/mpeg' });
                const fullAudioUrl = URL.createObjectURL(fullAudioBlob);

                // Generate filename from first few words
                const words = textToConvert.split(/\s+/).slice(0, 3).join('_').replace(/[^a-zA-Z0-9_]/g, '');
                const filename = words ? `lito_${words}.mp3` : "lito_audio.mp3";

                downloadBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = fullAudioUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                };

                playFullBtn.onclick = () => {
                    audioPlayer.src = fullAudioUrl;
                    audioPlayer.play();
                    statusDiv.textContent = "Playing Full Audio";
                };

                downloadBtn.style.display = "block";
                playFullBtn.style.display = "block";
                statusDiv.textContent = "Full audio ready!";
                statusDiv.style.color = "#10b981";
            } else {
                const words = textToConvert.split(/\s+/).slice(0, 3).join('_').replace(/[^a-zA-Z0-9_]/g, '');
                const filename = words ? `lito_${words}.mp3` : "lito_audio.mp3";

                downloadBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = firstChunkUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                };
                downloadBtn.style.display = "block";
                statusDiv.textContent = "Audio ready!";
                statusDiv.style.color = "#10b981";
            }

        } catch (error) {
            console.error(error);
            if (error.message.includes("503") || error.message.includes("unavailable")) {
                statusDiv.innerHTML = `
                    🚫 <strong>Demo limit reached</strong><br>
                    The free demo is currently at capacity. <br>
                    Download Lito Desktop for unlimited, local use:<br>
                    <a href="https://github.com/1dragon-xyz/lito/releases" target="_blank" style="color: #60a5fa; text-decoration: underline; font-weight: bold;">
                        Download Lito Desktop
                    </a>
                `;
                statusDiv.style.color = "#f59e0b";
            } else {
                statusDiv.textContent = error.message;
                statusDiv.style.color = "#f87171";
            }
        } finally {
            convertBtn.disabled = false;
            convertBtn.textContent = "Convert & Play";
        }
    });
});
