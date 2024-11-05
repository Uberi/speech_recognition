import sys
from unittest.mock import patch

import pytest

from speech_recognition.microphone import PyAudioWrapper


@pytest.mark.skip(sys.platform.startswith("win"), "skip on Windows")
class TestPyAudioWrapper:
    @patch("pyaudio.PyAudio")
    def test_get_pyaudio(self, PyAudio):
        assert PyAudioWrapper.get_pyaudio() == PyAudio.return_value
        PyAudio.assert_called_once_with()
