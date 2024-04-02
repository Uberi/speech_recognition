from unittest import TestCase
from unittest.mock import MagicMock, patch

from speech_recognition import AudioData, Recognizer
from speech_recognition.recognizers import whisper


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
