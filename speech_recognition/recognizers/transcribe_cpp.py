from __future__ import annotations

from array import array
from struct import iter_unpack
from typing import TYPE_CHECKING

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import UnknownValueError

if TYPE_CHECKING:
    from transcribe_cpp import Model


def recognize(
    _recognizer, audio_data: AudioData, *, model: Model, language: str | None = None
) -> str:
    """
    Transcribe a phrase locally with a loaded transcribe.cpp ASR model.

    The caller owns the model and can reuse it across phrases. Each call opens
    an independent inference session. Input duration and supported languages
    depend on the model. Raises UnknownValueError when no text is recognized.
    """
    if not isinstance(audio_data, AudioData):
        raise ValueError("``audio_data`` must be an ``AudioData`` instance")
    pcm = audio_data.get_raw_data(
        convert_rate=model.capabilities.native_sample_rate, convert_width=2
    )
    if not pcm:
        raise UnknownValueError()
    samples = array("f", (sample / 32768.0 for (sample,) in iter_unpack("<h", pcm)))
    with model.session() as session:
        text = session.run(samples, language=language, timestamps="none").text.strip()
    if not text:
        raise UnknownValueError()
    return text
