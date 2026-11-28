from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from examples.benchmark_fleurs import recognize_clip, select_clips
from speech_recognition import AudioData, Recognizer


@pytest.mark.parametrize("speech_detected, expected", [(True, "こんにちは"), (False, "")])
def test_benchmark_recognizer_respects_vad(speech_detected, expected):
    model = Mock()
    model.transcribe.return_value = [SimpleNamespace(text="こんにちは")]
    audio = AudioData(b"\x00\x00", 16000, 2)
    recognizer = Recognizer()

    with patch.object(recognizer, "recognize_nemo", wraps=recognizer.recognize_nemo) as recognize:
        assert recognize_clip(recognizer, audio, speech_detected, model) == expected
        if speech_detected:
            recognize.assert_called_once_with(audio, model=model)
        else:
            recognize.assert_not_called()


def test_benchmark_uses_entire_manifest_when_count_matches(tmp_path):
    manifest = tmp_path / "test.tsv"
    manifest.write_text("1\tb.wav\t猫。\n2\ta.wav\t犬。\n", encoding="utf-8")

    assert list(select_clips(manifest, count=2, seed=0).items()) == [
        ("b.wav", "猫。"),
        ("a.wav", "犬。"),
    ]
