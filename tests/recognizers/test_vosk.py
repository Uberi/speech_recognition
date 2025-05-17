from pathlib import Path

from speech_recognition import AudioData, Recognizer


def test_recognize_vosk():
    audio_file = str(Path(__file__).parent.parent / "english.wav")
    audio_data = AudioData.from_file(audio_file)
    sut = Recognizer()

    actual = sut.recognize_vosk(audio_data)

    expected = """\
{
  "text" : "one two three"
}\
"""
    assert actual == expected
