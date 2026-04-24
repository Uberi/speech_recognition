from unittest.mock import MagicMock, patch

import pytest

from speech_recognition import AudioData, Recognizer
from speech_recognition.recognizers import cohere_api

pytest.importorskip("cohere")


@patch("cohere.ClientV2")
def test_transcribe_default_model(mock_client_cls):
    mock_response = MagicMock()
    mock_response.text = "Transcription by Cohere"
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.return_value = mock_response
    mock_client_cls.return_value = mock_client

    audio_data = MagicMock(spec=AudioData)
    audio_data.get_wav_data.return_value = b"fake_wav"

    actual = cohere_api.recognize(
        MagicMock(spec=Recognizer), audio_data, language="en"
    )

    assert actual == "Transcription by Cohere"
    audio_data.get_wav_data.assert_called_once()
    mock_client_cls.assert_called_once_with()
    mock_client.audio.transcriptions.create.assert_called_once()
    call_kw = mock_client.audio.transcriptions.create.call_args.kwargs
    assert call_kw["model"] == "cohere-transcribe-03-2026"
    assert call_kw["language"] == "en"
    assert "file" in call_kw


@patch("cohere.ClientV2")
def test_transcribe_with_language(mock_client_cls):
    mock_response = MagicMock()
    mock_response.text = "Japanese transcription"
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create.return_value = mock_response
    mock_client_cls.return_value = mock_client

    audio_data = MagicMock(spec=AudioData)
    audio_data.get_wav_data.return_value = b"fake_wav"

    actual = cohere_api.recognize(
        MagicMock(spec=Recognizer), audio_data, language="ja"
    )

    assert actual == "Japanese transcription"
    call_kw = mock_client.audio.transcriptions.create.call_args.kwargs
    assert call_kw["model"] == "cohere-transcribe-03-2026"
    assert call_kw["language"] == "ja"
