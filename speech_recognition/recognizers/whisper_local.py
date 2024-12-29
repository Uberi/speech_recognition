from __future__ import annotations

import io
from typing import TYPE_CHECKING, Any, Literal, Protocol, TypedDict

from speech_recognition.audio import AudioData

if TYPE_CHECKING:
    import torch
    from typing_extensions import Unpack


class Transcribable(Protocol):
    def transcribe(self, audio_array, **kwargs) -> str | dict[str, Any]:
        pass


class WhisperCompatibleRecognizer:
    def __init__(self, model: Transcribable) -> None:
        self.model = model

    def recognize(
        self, audio_data: AudioData, show_dict: bool = False, **kwargs
    ):
        if not isinstance(audio_data, AudioData):
            raise ValueError(
                "``audio_data`` must be an ``AudioData`` instance"
            )

        import numpy as np
        import soundfile as sf

        # 16 kHz https://github.com/openai/whisper/blob/28769fcfe50755a817ab922a7bc83483159600a9/whisper/audio.py#L98-L99
        wav_bytes = audio_data.get_wav_data(convert_rate=16000)
        wav_stream = io.BytesIO(wav_bytes)
        audio_array, sampling_rate = sf.read(wav_stream)
        audio_array = audio_array.astype(np.float32)

        if "fp16" not in kwargs:
            import torch

            kwargs["fp16"] = torch.cuda.is_available()
        result = self.model.transcribe(audio_array, **kwargs)

        if show_dict:
            return result
        else:
            return result["text"]


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


class TranscribeOutput(TypedDict):
    text: str
    segments: list[Any]  # TODO Fix Any
    language: str


def recognize(
    self,
    audio_data: AudioData,
    model: str = "base",
    show_dict: bool = False,
    load_options: LoadModelOptionalParameters | None = None,
    **transcribe_options: Unpack[TranscribeOptionalParameters],
) -> str | TranscribeOutput:
    """
    Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using Whisper.

    Pick ``model`` from output of :command:`python -c 'import whisper; print(whisper.available_models())'`.
    See also https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages.

    If ``show_dict`` is true, returns the full dict response from Whisper, including the detected language. Otherwise returns only the transcription.

    You can specify:

        * ``language``: recognition language, an uncapitalized full language name like "english" or "chinese". See the full language list at https://github.com/openai/whisper/blob/main/whisper/tokenizer.py
        * ``task``

            * If you want transcribe + **translate**, set ``task="translate"``.

    Other values are passed directly to whisper. See https://github.com/openai/whisper/blob/main/whisper/transcribe.py for all options
    """

    import whisper

    whisper_model = whisper.load_model(model, **load_options or {})
    recognizer = WhisperCompatibleRecognizer(whisper_model)
    return recognizer.recognize(
        audio_data, show_dict=show_dict, **transcribe_options
    )
