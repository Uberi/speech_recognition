from __future__ import annotations

from typing import TYPE_CHECKING

from speech_recognition.audio import AudioData

if TYPE_CHECKING:
    from nemo.collections.asr.models import ASRModel


def recognize(recognizer, audio_data: AudioData, *, model: ASRModel) -> str:
    """Transcribe ``audio_data`` offline using a loaded 16 kHz NVIDIA NeMo ASR model.

    Pass a loaded ``model`` so the same checkpoint can be reused across calls.
    For CPU inference, load it with ``ASRModel.restore_from(path, map_location="cpu")``.
    Returns the best transcript, which may be empty if the model emits no text.
    """
    if not isinstance(audio_data, AudioData):
        raise ValueError("``audio_data`` must be an ``AudioData`` instance")

    import numpy as np

    pcm = audio_data.get_raw_data(convert_rate=16000, convert_width=2)
    waveform = np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768.0
    hypothesis = model.transcribe([waveform], verbose=False)[0]
    if isinstance(hypothesis, list):
        hypothesis = hypothesis[0]
    return hypothesis.text
