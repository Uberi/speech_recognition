import io
import wave

import pytest

from speech_recognition import AudioData


@pytest.mark.parametrize("sample_width", [1, 2, 3, 4])
@pytest.mark.parametrize("explicit_width", [False, True])
@pytest.mark.parametrize("silent", [False, True])
def test_wav_export_preserves_pcm(sample_width, explicit_width, silent):
    if sample_width == 1:
        raw = b"\x80" * 256 if silent else bytes(range(256))
    else:
        limit = 1 << (sample_width * 8 - 1)
        samples = [0] * 7 if silent else [
            -limit, -limit + 1, -1, 0, 1, limit - 2, limit - 1
        ]
        raw = b"".join(
            sample.to_bytes(sample_width, "little", signed=True)
            for sample in samples
        )
    audio = AudioData(raw, 16000, sample_width)
    kwargs = {"convert_width": sample_width} if explicit_width else {}

    with wave.open(io.BytesIO(audio.get_wav_data(**kwargs)), "rb") as reader:
        assert reader.getnchannels() == 1
        assert reader.getframerate() == 16000
        assert reader.getsampwidth() == sample_width
        assert reader.getnframes() == len(raw) // sample_width
        assert reader.readframes(reader.getnframes()) == raw


@pytest.mark.parametrize("convert_rate", [8000, 32000])
@pytest.mark.parametrize("explicit_width", [False, True])
def test_resampled_8_bit_wav_preserves_unsigned_samples(convert_rate, explicit_width):
    audio = AudioData(b"\x81" * 9, 16000, 1)
    kwargs = {"convert_width": 1} if explicit_width else {}
    expected_frames = 8 * convert_rate // 16000 + 1

    with wave.open(io.BytesIO(audio.get_wav_data(convert_rate, **kwargs)), "rb") as reader:
        assert reader.getframerate() == convert_rate
        assert reader.getsampwidth() == 1
        assert reader.getnframes() == expected_frames
        assert reader.readframes(expected_frames) == b"\x81" * expected_frames
