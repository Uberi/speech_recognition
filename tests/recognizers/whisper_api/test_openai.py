from unittest.mock import MagicMock

import httpx
import pytest
import respx

from speech_recognition import AudioData, Recognizer
from speech_recognition.recognizers.whisper_api import openai


@pytest.fixture
def setenv_openai_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk_openai_api_key")


@respx.mock(assert_all_called=True, assert_all_mocked=True)
def test_transcribe_with_openai_whisper(respx_mock, setenv_openai_api_key):
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

    actual = openai.recognize(MagicMock(spec=Recognizer), audio_data)

    assert actual == "Transcription by OpenAI Whisper"
    audio_data.get_wav_data.assert_called_once()


@respx.mock(assert_all_called=True, assert_all_mocked=True)
def test_transcribe_with_specified_language(respx_mock, setenv_openai_api_key):
    # https://github.com/Uberi/speech_recognition/issues/681
    respx_mock.post(
        "https://api.openai.com/v1/audio/transcriptions",
        data__contains={"language": "en"},
    ).respond(
        200,
        json={"text": "English transcription"},
    )

    audio_data = MagicMock(spec=AudioData)
    audio_data.get_wav_data.return_value = b"english_audio"

    actual = openai.recognize(
        MagicMock(spec=Recognizer), audio_data, language="en"
    )

    assert actual == "English transcription"


@respx.mock(assert_all_called=True, assert_all_mocked=True)
def test_transcribe_with_specified_prompt(respx_mock, setenv_openai_api_key):
    # https://github.com/Uberi/speech_recognition/pull/676
    respx_mock.post(
        "https://api.openai.com/v1/audio/transcriptions",
        # ref: https://cookbook.openai.com/examples/whisper_prompting_guide
        data__contains={"prompt": "Glossary: Aimee, Shawn, BBQ"},
    ).respond(
        200,
        json={"text": "Prompted transcription"},
    )

    audio_data = MagicMock(spec=AudioData)
    audio_data.get_wav_data.return_value = b"audio_data"

    actual = openai.recognize(
        MagicMock(spec=Recognizer),
        audio_data,
        prompt="Glossary: Aimee, Shawn, BBQ",
    )

    assert actual == "Prompted transcription"
