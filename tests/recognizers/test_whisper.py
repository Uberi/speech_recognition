from unittest import TestCase
from unittest.mock import MagicMock, patch

from speech_recognition import AudioData, Recognizer
from speech_recognition.exceptions import SetupError
from speech_recognition.recognizers import whisper

class RecognizeWhisperApiTestCase(TestCase):
    @patch("speech_recognition.recognizers.whisper.os.environ")
    @patch("speech_recognition.recognizers.whisper.BytesIO")
    @patch("openai.OpenAI")
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

    @patch("speech_recognition.recognizers.whisper.os.environ")
    @patch("speech_recognition.recognizers.whisper.BytesIO")
    @patch("openai.OpenAI")
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

    # Test case to verify that ValueError is raised for invalid audio data
    # Mocking the os.environ to control environment variables
    @patch("speech_recognition.recognizers.whisper.os.environ")
    # Mocking BytesIO for handling byte streams
    @patch("speech_recognition.recognizers.whisper.BytesIO")
    # Mocking the OpenAI API client
    @patch("openai.OpenAI")
    def test_value_error_invalid_audio_data(self, OpenAI, BytesIO, environ):
        # Create a mock client for OpenAI
        client = OpenAI.return_value
        
        # Create a mock Recognizer instance
        recognizer = MagicMock(spec=Recognizer)  
        # Define invalid audio data
        invalid_audio_data = "invalid data"
        
        # Assert that ValueError is raised when invalid audio data is passed
        with self.assertRaises(ValueError) as context:
            whisper.recognize_whisper_api(recognizer, invalid_audio_data)
        # Check that the exception message is as expected
        self.assertEqual(str(context.exception), "``audio_data`` must be an ``AudioData`` instance")

    # Test case to verify that SetupError is raised when API key is missing
    def test_missing_api_key(self):
        # Create a mock Recognizer instance
        recognizer = MagicMock(spec=Recognizer)
        # Create a mock AudioData instance
        audio_data = MagicMock(spec=AudioData)

        # Assert that SetupError is raised when no API key is provided
        with self.assertRaises(SetupError) as context:
            whisper.recognize_whisper_api(recognizer, audio_data, model="x-whisper", api_key=None)
        
        # Check that the exception message indicates the API key is not set
        self.assertEqual(str(context.exception), "Set environment variable ``OPENAI_API_KEY``")
    
    # Test case to verify that SetupError is raised when the OpenAI module is not found
    # Mocking the os.environ
    @patch("speech_recognition.recognizers.whisper.os.environ")
    # Mocking BytesIO
    @patch("speech_recognition.recognizers.whisper.BytesIO")
    # Simulate that the OpenAI module is not available
    @patch.dict("sys.modules", {"openai": None})
    def test_import_error_openai(self, BytesIO, environ):
        # Create a mock Recognizer instance
        recognizer = MagicMock(spec=Recognizer)
        # Create a mock AudioData instance
        audio_data = MagicMock(spec=AudioData)

        # Assert that SetupError is raised when OpenAI module is missing
        with self.assertRaises(SetupError) as context:
            whisper.recognize_whisper_api(recognizer, audio_data)

        # Check that the exception message indicates the missing OpenAI module
        self.assertEqual(
            str(context.exception),
            "missing openai module: ensure that openai is set up correctly."
        )