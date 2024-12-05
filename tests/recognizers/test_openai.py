from unittest import TestCase
from unittest.mock import MagicMock, patch

import httpx
import pytest
import respx

from speech_recognition import AudioData, Recognizer
from speech_recognition.recognizers import whisper


@respx.mock(assert_all_called=True, assert_all_mocked=True)
def test_transcribe_with_openai_whisper(respx_mock, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk_openai_api_key")

    respx_mock.post("https://api.openai.com/v1/audio/transcriptions").mock(
        return_value=httpx.Response(
            200,
            json={"text": "Transcription by OpenAI Whisper"},
        )
    )

    audio_data = MagicMock(spec=AudioData)
    audio_data.get_wav_data.return_value = b"audio_data"

    actual = whisper.recognize_whisper_api(
        MagicMock(spec=Recognizer), audio_data, model="whisper-1"
    )

    assert actual == "Transcription by OpenAI Whisper"


@pytest.mark.skip
@patch("speech_recognition.recognizers.whisper.os.environ")
@patch("speech_recognition.recognizers.whisper.BytesIO")
@patch("openai.OpenAI")
class RecognizeWhisperApiTestCase(TestCase):
    def test_recognize_default_arguments(self, OpenAI, BytesIO, environ):
        client = OpenAI.return_value
        transcript = client.audio.transcriptions.create.return_value

        recognizer = MagicMock(spec=Recognizer)
        audio_data = MagicMock(spec=AudioData)

        actual = whisper.recognize_whisper_api(recognizer, audio_data)

        self.assertEqual(actual, transcript.text)
        audio_data.get_wav_data.assert_called_once_with()
        BytesIO.assert_called_once_with(audio_data.get_wav_data.return_value)
        OpenAI.assert_called_once_with(api_key=None)
        client.audio.transcriptions.create.assert_called_once_with(
            file=BytesIO.return_value, model="whisper-1"
        )

    def test_recognize_pass_arguments(self, OpenAI, BytesIO, environ):
        client = OpenAI.return_value

        recognizer = MagicMock(spec=Recognizer)
        audio_data = MagicMock(spec=AudioData)

        _ = whisper.recognize_whisper_api(
            recognizer, audio_data, model="x-whisper", api_key="OPENAI_API_KEY"
        )

        OpenAI.assert_called_once_with(api_key="OPENAI_API_KEY")
        client.audio.transcriptions.create.assert_called_once_with(
            file=BytesIO.return_value, model="x-whisper"
        )
