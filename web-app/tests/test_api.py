from fastapi.testclient import TestClient
from api.index import app, clean_text

client = TestClient(app)

def test_clean_text():
    assert clean_text("Hello   World") == "Hello World"
    assert clean_text("  Hi  ") == "Hi"

def test_get_voices():
    response = client.get("/api/voices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check for a known voice
    assert any(v['ShortName'] == "vi-VN-HoaiMyNeural" for v in data)

def test_tts_empty_text():
    response = client.post("/api/tts", json={"text": "", "voice": "vi-VN-HoaiMyNeural"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Text cannot be empty"
