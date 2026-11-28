from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from speech_recognition import AudioData, Recognizer
from speech_recognition.recognizers.nemo import recognize


@pytest.mark.parametrize("text", ["こんにちは。", ""])
def test_recognize_nemo(text):
    model = Mock()
    model.transcribe.return_value = [SimpleNamespace(text=text)]
    audio = AudioData(bytes([0, 255, 128, 255, 255]), 32000, 1)

    assert Recognizer().recognize_nemo(audio, model=model) == text

    model.transcribe.assert_called_once()
    (waveforms,), options = model.transcribe.call_args
    assert options == {"verbose": False}
    assert len(waveforms) == 1
    assert waveforms[0].dtype == np.float32
    np.testing.assert_array_equal(waveforms[0], [-1.0, 0.0, 127 / 128])


def test_recognize_nemo_requires_audio_data():
    model = Mock()
    with pytest.raises(ValueError, match="must be an ``AudioData`` instance"):
        recognize(Recognizer(), None, model=model)
    model.transcribe.assert_not_called()
