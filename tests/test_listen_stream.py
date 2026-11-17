import io
import wave

import pytest

from speech_recognition import AudioFile, Recognizer


CHUNK = 1024
RATE = 8192


def wav_audio(raw, width):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setparams((1, width, RATE, 0, "NONE", "not compressed"))
        writer.writeframes(raw)
    buffer.seek(0)
    return buffer


def recognizer():
    result = Recognizer()
    result.dynamic_energy_threshold = False
    result.energy_threshold = 1
    result.phrase_threshold = 0
    return result


@pytest.mark.parametrize("width", [1, 2, 3, 4])
@pytest.mark.parametrize("limit", [0.0625, 0.125, 0.25, 0.5])
def test_stream_time_limit_does_not_repeat_last_buffer(width, limit):
    raw = b"".join(value.to_bytes(width, "little") * CHUNK for value in range(10, 90, 10))
    with AudioFile(wav_audio(raw, width)) as source:
        source.CHUNK = CHUNK
        chunks = list(recognizer().listen(source, stream=True, phrase_time_limit=limit))
        read_frames = source.audio_reader.tell()
    expected_frames = (1 + int(limit * RATE // CHUNK)) * CHUNK
    assert read_frames == expected_frames
    assert b"".join(chunk.frame_data for chunk in chunks) == raw[:read_frames * width]


@pytest.mark.parametrize("width", [1, 2, 3, 4])
def test_stream_eof_preserves_partial_buffer(width):
    raw = b"\x0a" * (CHUNK * 4 + CHUNK // 2) * width
    with AudioFile(wav_audio(raw, width)) as source:
        source.CHUNK = CHUNK
        chunks = list(recognizer().listen(source, stream=True))
    assert b"".join(chunk.frame_data for chunk in chunks) == raw
    assert chunks[-1].frame_data == b""


@pytest.mark.parametrize("width", [2, 3, 4])
def test_stream_pause_preserves_final_unyielded_buffer(width):
    voice = (10).to_bytes(width, "little") * CHUNK
    silence = b"\x00" * CHUNK * width
    raw = voice * 2 + silence * 4 + voice
    listener = recognizer()
    listener.non_speaking_duration = 0.125
    listener.pause_threshold = 0.25
    with AudioFile(wav_audio(raw, width)) as source:
        source.CHUNK = CHUNK
        chunks = list(listener.listen(source, stream=True))
        assert source.audio_reader.tell() == CHUNK * 5
    assert b"".join(chunk.frame_data for chunk in chunks) == voice * 2 + silence * 3
    assert chunks[-1].frame_data == silence


def test_stream_hotword_eof_still_yields_empty_buffer(tmp_path, monkeypatch):
    (tmp_path / "snowboydetect.py").touch()
    listener = recognizer()
    monkeypatch.setattr(listener, "snowboy_wait_for_hot_word", lambda *args: (b"", 0))
    with AudioFile(wav_audio(b"\x0a\x00" * CHUNK, 2)) as source:
        chunks = list(listener.listen(source, stream=True, snowboy_configuration=(str(tmp_path), [])))
    assert [chunk.frame_data for chunk in chunks] == [b""]
