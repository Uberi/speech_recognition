from unittest.mock import patch

from speech_recognition import Microphone

class TestPyAudioWrapper:
    @patch("pyaudio.PyAudio")
    def test_get_pyaudio(self, PyAudio):
        assert Microphone.get_pyaudio_v2() == PyAudio.return_value
        PyAudio.assert_called_once_with()
