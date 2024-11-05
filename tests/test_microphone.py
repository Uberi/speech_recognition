from unittest.mock import patch

from speech_recognition.microphone import PyAudioWrapper


class TestPyAudioWrapper:
    @patch("pyaudio.PyAudio")
    def test_get_pyaudio(self, PyAudio):
        assert PyAudioWrapper.get_pyaudio() == PyAudio.return_value
        PyAudio.assert_called_once_with()
