from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from speech_recognition.audio import AudioData
from speech_recognition.recognizers.whisper_local.base import (
    WhisperCompatibleRecognizer,
)

if TYPE_CHECKING:
    import numpy as np
    import torch
    from typing_extensions import Unpack
    from whisper import Whisper


class LoadModelOptionalParameters(TypedDict, total=False):
    # ref: https://github.com/openai/whisper/blob/v20240930/whisper/__init__.py#L103
    device: str | torch.device
    download_root: str
    in_memory: bool


class TranscribeOptionalParameters(TypedDict, total=False):
    """Transcribe optional parameters & DecodingOptions parameters."""

    # ref: https://github.com/openai/whisper/blob/v20240930/whisper/transcribe.py#L38
    temperature: float | tuple[float, ...]
    # TODO Add others

    # ref: https://github.com/openai/whisper/blob/v20240930/whisper/decoding.py#L81
    task: Literal["transcribe", "translate"]
    language: str
    fp16: bool
    # TODO Add others


class Segment(TypedDict):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: list[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float


class TranscribeOutput(TypedDict):
    text: str
    segments: list[Segment]
    language: str


class TranscribableAdapter:
    def __init__(self, model: Whisper) -> None:
        self.model = model

    def transcribe(
        self, audio_array: np.ndarray, **kwargs
    ) -> TranscribeOutput:
        if "fp16" not in kwargs:
            import torch

            kwargs["fp16"] = torch.cuda.is_available()

        return self.model.transcribe(audio_array, **kwargs)


def recognize(
    recognizer,
    audio_data: AudioData,
    model: str = "base",
    show_dict: bool = False,
    load_options: LoadModelOptionalParameters | None = None,
    **transcribe_options: Unpack[TranscribeOptionalParameters],
) -> str | TranscribeOutput:
    """Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using Whisper.

    Pick ``model`` from output of :command:`python -c 'import whisper; print(whisper.available_models())'`.
    See also https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages.

    If ``show_dict`` is true, returns the full dict response from Whisper, including the detected language. Otherwise returns only the transcription.

    You can specify:

        * ``language``: recognition language, an uncapitalized full language name like "english" or "chinese". See the full language list at https://github.com/openai/whisper/blob/main/whisper/tokenizer.py

            * If not set, Whisper will automatically detect the language.

        * ``task``

            * If you want transcribe + **translate** to english, set ``task="translate"``.

    Other values are passed directly to whisper. See https://github.com/openai/whisper/blob/main/whisper/transcribe.py for all options.
    """

    import whisper

    whisper_model = whisper.load_model(model, **load_options or {})
    whisper_recognizer = WhisperCompatibleRecognizer(
        TranscribableAdapter(whisper_model)
    )
    return whisper_recognizer.recognize(
        audio_data, show_dict=show_dict, **transcribe_options
    )
