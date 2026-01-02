from pathlib import Path

import pytest

from speech_recognition import AudioData, Recognizer


@pytest.fixture
def audio_data() -> AudioData:
    audio_file = str(Path(__file__).parent.parent / "english.wav")
    return AudioData.from_file(audio_file)


def test_recognize_vosk(audio_data):
    recognizer = Recognizer()
    actual = recognizer.recognize_vosk(audio_data)

    assert actual == "one two three"


def test_recognize_vosk_verbose(audio_data):
    recognizer = Recognizer()
    actual = recognizer.recognize_vosk(audio_data, verbose=True)

    assert actual == {"text": "one two three"}
