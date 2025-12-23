# Lito Manual Smoke Test Procedure

Before pushing changes to the repository, you must manually verify the application's core functionality to ensure no regressions were introduced.

## Pass/Fail Criteria

A test run is considered a **PASS** only if **ALL** the following steps are completed successfully without crashes, errors, or significant UI glitches.

## Test Steps

1.  **Launch the App:**
    *   Run: `uv run desktop-app/main.py`
    *   **Check:** App window opens. Title is "Lito vX.X.X". Header says "Lito: Text to Speech". "?" button is visible.

2.  **Verify About Dialog:**
    *   Click "?".
    *   **Check:** Popup appears with correct Version, Copyright, and Contact Info.
    *   Close the popup.

3.  **Test Voice Selection:**
    *   Click "Select Voice" dropdown.
    *   **Check:** List contains Vietnamese, English, and Chinese voices.
    *   Select "English (Male)".

4.  **Test Text Conversion:**
    *   Go to "Text Input" tab.
    *   Type: "Hello, this is a test."
    *   Click "Convert to Audio".
    *   **Check:** Status bar shows "Generating audio...", then "Done!".
    *   **Check:** "Play Audio" and "Open Folder" buttons become enabled.

5.  **Test Audio Playback:**
    *   Click "Play Audio".
    *   **Check:** System default media player opens and plays the audio clearly.

6.  **Test File Upload (Optional but Recommended):**
    *   Go to "File Upload" tab.
    *   Select a small `.txt` file.
    *   Click "Convert to Audio".
    *   **Check:** Conversion succeeds.

## Failure Handling
If ANY step fails:
1.  **Abort the push.**
2.  Fix the issue.
3.  Restart the Smoke Test from Step 1.
