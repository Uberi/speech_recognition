from unittest.mock import MagicMock

import httpx
import respx

from speech_recognition import AudioData, Recognizer
from speech_recognition.recognizers.whisper_api import groq


@respx.mock(assert_all_called=True, assert_all_mocked=True)
def test_transcribe_with_groq_whisper(respx_mock, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_grok_api_key")

    respx_mock.post(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        headers__contains={"Authorization": "Bearer gsk_grok_api_key"},
        data__contains={"model": "whisper-large-v3"},
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "text": "Transcription by Groq Whisper",
                "x_groq": {"id": "req_unique_id"},
            },
        )
    )

    audio_data = MagicMock(spec=AudioData)
    audio_data.get_wav_data.return_value = b"audio_data"

    actual = groq.recognize(
        MagicMock(spec=Recognizer), audio_data, model="whisper-large-v3"
    )

    assert actual == "Transcription by Groq Whisper"
