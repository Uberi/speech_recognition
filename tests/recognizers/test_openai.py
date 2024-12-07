from unittest.mock import MagicMock

import httpx
import respx

from speech_recognition import AudioData, Recognizer
from speech_recognition.recognizers import whisper


@respx.mock(assert_all_called=True, assert_all_mocked=True)
def test_transcribe_with_openai_whisper(respx_mock, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk_openai_api_key")

    respx_mock.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers__contains={"Authorization": "Bearer sk_openai_api_key"},
        data__contains={"model": "whisper-1"},
    ).mock(
        return_value=httpx.Response(
            200,
            json={"text": "Transcription by OpenAI Whisper"},
        )
    )

    audio_data = MagicMock(spec=AudioData)
    audio_data.get_wav_data.return_value = b"audio_data"

    actual = whisper.recognize_whisper_api(
        MagicMock(spec=Recognizer), audio_data
    )

    assert actual == "Transcription by OpenAI Whisper"
    audio_data.get_wav_data.assert_called_once()
