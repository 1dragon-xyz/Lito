from fastapi.testclient import TestClient
from api.index import app, clean_text, MAX_CHARS

client = TestClient(app)

def test_clean_text():
    assert clean_text("Hello   World") == "Hello World"
    assert clean_text("  Hi  ") == "Hi"

def test_get_voices():
    response = client.get("/api/voices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 40  # 20 languages × 2 voices
    # Check for Vietnamese voice (new format)
    assert any(v['id'] == "vi-VN-Standard-A" for v in data)
    # Check structure
    first_voice = data[0]
    assert 'id' in first_voice
    assert 'name' in first_voice
    assert 'gender' in first_voice
    assert 'locale' in first_voice

def test_tts_empty_text():
    response = client.post("/api/tts", json={"text": "", "voice": "vi-VN-Standard-A"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Text cannot be empty"

def test_tts_over_limit():
    long_text = "a" * (MAX_CHARS + 1)
    response = client.post("/api/tts", json={"text": long_text, "voice": "vi-VN-Standard-A"})
    assert response.status_code == 400
    assert "limit" in response.json()["detail"].lower()

def test_tts_invalid_voice():
    response = client.post("/api/tts", json={"text": "Hello", "voice": "invalid-voice"})
    assert response.status_code == 400
    assert "invalid voice" in response.json()["detail"].lower()
