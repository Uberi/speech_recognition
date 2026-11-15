import aifc
import io
import wave

import pytest

from speech_recognition import AudioData


@pytest.mark.parametrize("sample_width", [1, 2, 3, 4])
@pytest.mark.parametrize("file_format", ["raw", "wav", "aiff"])
def test_24_bit_conversion_preserves_samples(sample_width, file_format):
    limit = 1 << (sample_width * 8 - 1)
    samples = [-limit, -limit + 1, -1, 0, 1, limit - 2, limit - 1]
    raw = b"".join(
        (sample + 128).to_bytes(1, "little") if sample_width == 1
        else sample.to_bytes(sample_width, "little", signed=True)
        for sample in samples
    )
    expected_samples = [
        sample << (8 * (3 - sample_width)) if sample_width <= 3
        else sample >> 8
        for sample in samples
    ]
    audio = AudioData(raw, 16000, sample_width)

    if file_format == "raw":
        converted = audio.get_raw_data(convert_width=3)
        byteorder = "little"
    else:
        if file_format == "wav":
            data = audio.get_wav_data(convert_width=3)
            reader = wave.open(io.BytesIO(data), "rb")
            byteorder = "little"
        else:
            data = audio.get_aiff_data(convert_width=3)
            reader = aifc.open(io.BytesIO(data), "rb")
            byteorder = "big"
        with reader:
            assert reader.getnchannels() == 1
            assert reader.getframerate() == 16000
            assert reader.getsampwidth() == 3
            assert reader.getnframes() == len(samples)
            converted = reader.readframes(reader.getnframes())

    assert converted == b"".join(
        sample.to_bytes(3, byteorder, signed=True)
        for sample in expected_samples
    )


@pytest.mark.parametrize("sample_width", [1, 2])
@pytest.mark.parametrize("convert_rate", [8000, 32000])
def test_24_bit_conversion_after_resampling(sample_width, convert_rate):
    # A constant signal stays constant under the linear resampler.
    raw_sample = b"\x81" if sample_width == 1 else b"\x34\x12"
    sample = 1 << 16 if sample_width == 1 else 0x1234 << 8
    audio = AudioData(raw_sample * 9, 16000, sample_width)
    expected_frames = 8 * convert_rate // 16000 + 1

    assert audio.get_raw_data(convert_rate=convert_rate, convert_width=3) == (
        sample.to_bytes(3, "little", signed=True) * expected_frames
    )
