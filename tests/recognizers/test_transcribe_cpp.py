from array import array
from struct import pack
from unittest.mock import MagicMock

import pytest

from speech_recognition import AudioData, Recognizer, UnknownValueError


def test_converts_audio_for_the_loaded_model_and_closes_the_session():
    # Unsigned 8-bit PCM at half the model rate exercises scaling and resampling.
    audio = AudioData(bytes([0, 128, 255]), 8000, 1)
    model = MagicMock()
    model.capabilities.native_sample_rate = 16000
    context = model.session.return_value
    session = context.__enter__.return_value
    session.run.return_value.text = "  hello  "

    text = Recognizer().recognize_transcribe_cpp(audio, model=model, language="en")

    assert text == "hello"
    samples, = session.run.call_args.args
    assert samples.typecode == "f"
    assert samples.tolist() == pytest.approx([-1.0, -0.5, 0, 0.4921875, 0.9921875], abs=0.004)
    assert session.run.call_args.kwargs == {"language": "en", "timestamps": "none"}
    context.__exit__.assert_called_once()
    model.close.assert_not_called()


def test_model_can_be_reused_with_independent_phrase_sessions():
    model = MagicMock()
    model.capabilities.native_sample_rate = 16000
    contexts = [MagicMock(), MagicMock()]
    model.session.side_effect = contexts
    recognizer = Recognizer()
    for phrase, context in zip(("first", "second"), contexts):
        session = context.__enter__.return_value
        session.run.return_value.text = phrase
        assert recognizer.recognize_transcribe_cpp(
            AudioData(pack("<hh", -32768, 16384), 16000, 2), model=model
        ) == phrase
        session.run.assert_called_once_with(array("f", [-1.0, 0.5]), language=None, timestamps="none")
        context.__exit__.assert_called_once()


def test_empty_audio_and_empty_recognition_raise_unknown_value():
    model = MagicMock()
    model.capabilities.native_sample_rate = 16000
    recognizer = Recognizer()
    with pytest.raises(UnknownValueError):
        recognizer.recognize_transcribe_cpp(AudioData(b"", 16000, 2), model=model)
    model.session.assert_not_called()
    model.session.return_value.__enter__.return_value.run.return_value.text = "  "
    with pytest.raises(UnknownValueError):
        recognizer.recognize_transcribe_cpp(AudioData(bytes(160), 16000, 2), model=model)
