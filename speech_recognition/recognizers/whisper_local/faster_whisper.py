from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from speech_recognition.audio import AudioData
from speech_recognition.recognizers.whisper_local.base import (
    WhisperCompatibleRecognizer,
)

if TYPE_CHECKING:
    import numpy as np
    from faster_whisper import WhisperModel
    from faster_whisper.transcribe import Segment
    from typing_extensions import Unpack


class TranscribeOutput(TypedDict):
    text: str
    segments: list[Segment]
    language: str


class TranscribableAdapter:
    def __init__(self, model: WhisperModel) -> None:
        self.model = model

    def transcribe(
        self, audio_array: np.ndarray, **kwargs
    ) -> TranscribeOutput:
        segments_generator, info = self.model.transcribe(audio_array, **kwargs)
        segments = list(segments_generator)
        return {
            "text": " ".join(segment.text for segment in segments),
            "segments": segments,
            "language": info.language,
        }


class TranscribeOptionalParameters(TypedDict, total=False):
    # https://github.com/SYSTRAN/faster-whisper/blob/v1.1.0/faster_whisper/transcribe.py#L692
    language: str
    task: Literal["transcribe", "translate"]
    beam_size: int
    # TODO Add others


def recognize(
    recognizer,
    audio_data: AudioData,
    model: str = "base",
    show_dict: bool = False,
    **transcribe_options: Unpack[TranscribeOptionalParameters],
) -> str:
    import torch
    from faster_whisper import WhisperModel

    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = WhisperModel(model, device=device)
    whisper_recognizer = WhisperCompatibleRecognizer(
        TranscribableAdapter(model)
    )
    return whisper_recognizer.recognize(
        audio_data, show_dict=show_dict, **transcribe_options
    )
