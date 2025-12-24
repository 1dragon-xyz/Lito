document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const voiceSelect = document.getElementById('voice-select');
    const textInput = document.getElementById('text-input');
    const convertBtn = document.getElementById('convert-btn');
    const statusDiv = document.getElementById('status');
    const audioPlayer = document.getElementById('audio-player');

    // Tab Elements
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const fileNameDisplay = document.getElementById('file-name-display');

    let currentMode = 'text'; // 'text' or 'file'
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
                option.value = voice.ShortName;
                option.textContent = voice.FriendlyName;
                voiceSelect.appendChild(option);
            });
        } catch (error) {
            statusDiv.textContent = "Error loading voices.";
            statusDiv.style.color = "red";
        }
    }
    loadVoices();

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
    downloadBtn.style.backgroundColor = "#10b981"; // Emerald green
    downloadBtn.style.display = "none";
    document.querySelector('.action-group').appendChild(downloadBtn);

    // Play Full Audio Button (created dynamically)
    const playFullBtn = document.createElement('button');
    playFullBtn.textContent = "Play Full Audio";
    playFullBtn.style.marginTop = "10px";
    playFullBtn.style.backgroundColor = "#3b82f6"; // Blue
    playFullBtn.style.display = "none";
    // Insert before download button
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
        if (!response.ok) throw new Error('Failed to fetch audio chunk');
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
        return data.text;
    }

    // --- Main Action ---
    convertBtn.addEventListener('click', async () => {
        // 1. Get Text
        let textToConvert = "";
        const voice = voiceSelect.value;

        statusDiv.textContent = "";
        downloadBtn.style.display = "none";
        playFullBtn.style.display = "none";
        audioPlayer.hidden = true;
        audioPlayer.pause();

        // UI Reset
        statusDiv.style.color = "#94a3b8";

        try {
            convertBtn.disabled = true;
            convertBtn.textContent = "Processing...";
            statusDiv.textContent = "Reading input...";

            if (currentMode === 'text') {
                textToConvert = textInput.value.trim();
                if (!textToConvert) throw new Error("Please enter some text.");
            } else {
                if (!selectedFile) throw new Error("Please select a file.");
                textToConvert = await extractTextFromFile(selectedFile);
            }

            // 2. Chunking
            const chunks = splitIntoChunks(textToConvert);
            statusDiv.textContent = "Generating Preview..."; // Magic status

            // 3. Process Chunk 1 for Preview
            const firstChunkBlob = await fetchAudioChunk(chunks[0], voice);
            const firstChunkUrl = URL.createObjectURL(firstChunkBlob);

            // Play Preview
            audioPlayer.src = firstChunkUrl;
            audioPlayer.hidden = false;
            audioPlayer.play();

            statusDiv.textContent = "Playing Preview... (Generating full audio in background)";
            statusDiv.style.color = "#3b82f6"; // Blue info

            // 4. Background Process Rest
            if (chunks.length > 1) {
                const audioBlobs = [firstChunkBlob];

                // Fetch remaining chunks in parallel
                const promises = chunks.slice(1).map(chunk => fetchAudioChunk(chunk, voice));
                const remainingBlobs = await Promise.all(promises);
                audioBlobs.push(...remainingBlobs);

                // Merge
                const fullAudioBlob = new Blob(audioBlobs, { type: 'audio/mpeg' });
                const fullAudioUrl = URL.createObjectURL(fullAudioBlob);

                // Enable Full Actions
                downloadBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = fullAudioUrl;
                    a.download = "lito_full_audio.mp3";
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
                statusDiv.style.color = "#10b981"; // Green success
            } else {
                // If only 1 chunk, we already have full audio
                downloadBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = firstChunkUrl;
                    a.download = "lito_audio.mp3";
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
            statusDiv.textContent = error.message;
            statusDiv.style.color = "#f87171";
        } finally {
            convertBtn.disabled = false;
            convertBtn.textContent = "Convert & Play";
        }
    });
});

