import pytest
from unittest.mock import MagicMock
import sys
import os

# Ensure we can import the app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import App

@pytest.fixture
def mock_app(mocker):
    # 1. Create the App instance without calling __init__
    app = MagicMock(spec=App)
    
    # 2. Re-enable the real methods we want to test
    # (We are testing the LOGIC inside these methods)
    app.prepare_conversion = lambda: App.prepare_conversion(app)
    app.on_conversion_complete = lambda result, path: App.on_conversion_complete(app, result, path)
    
    # 3. Manually mock dependencies and UI state
    app.notebook = MagicMock()
    app.text_area = MagicMock()
    app.voice_combo = MagicMock()
    app.status_var = MagicMock()
    app.btn_convert = MagicMock()
    app.btn_play = MagicMock()
    app.btn_folder = MagicMock()
    app.voice_mapping = {"Test Voice": "test-voice"}
    app.selected_file_path = ""
    app.tts_manager = MagicMock()
    app.is_converting = False
    app.cancel_event = MagicMock()
    
    # Mock messagebox
    app.mock_msgbox = mocker.patch('tkinter.messagebox')
    
    return app

def test_validation_empty_text(mock_app):
    """Test that clicking convert with no text shows a warning."""
    mock_app.notebook.index.return_value = 0 # Text Tab
    mock_app.text_area.get.return_value = "" # Empty text
    
    mock_app.prepare_conversion()
    
    mock_app.mock_msgbox.showwarning.assert_called_with("Warning", "Please enter some text.")

def test_validation_no_file(mock_app):
    """Test that clicking convert on file tab with no file shows warning."""
    mock_app.notebook.index.return_value = 1 # File Tab
    mock_app.selected_file_path = ""
    
    mock_app.prepare_conversion()
    
    mock_app.mock_msgbox.showwarning.assert_called_with("Warning", "Please select a file first.")

def test_conversion_flow_text(mock_app, mocker):
    """Test the full conversion flow for text input."""
    mock_app.notebook.index.return_value = 0 # Text Tab
    mock_app.text_area.get.return_value = "Hello World"
    mock_app.voice_combo.get.return_value = "Test Voice"
    
    mock_thread = mocker.patch('threading.Thread')
    
    mock_app.prepare_conversion()
    
    assert mock_app.is_converting is True
    mock_thread.assert_called_once()

def test_conversion_completion_success(mock_app, mocker):
    """Test success callback."""
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('winsound.MessageBeep')
    
    mock_app.on_conversion_complete("success", "path.mp3")
    
    assert mock_app.is_converting is False
    mock_app.btn_play.config.assert_called_with(state="normal")
    mock_app.mock_msgbox.showinfo.assert_called_with("Success", "Conversion complete!")