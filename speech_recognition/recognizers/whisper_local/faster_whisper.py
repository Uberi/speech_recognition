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


class InitOptionalParameters(TypedDict, total=False):
    # https://github.com/SYSTRAN/faster-whisper/blob/v1.1.0/faster_whisper/transcribe.py#L575
    device: Literal["cpu", "gpu", "auto"]
    compute_type: str
    download_root: str
    # TODO Add others


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
    init_options: InitOptionalParameters | None = None,
    **transcribe_options: Unpack[TranscribeOptionalParameters],
) -> str | TranscribeOutput:
    """Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using Whisper.

    Pick ``model`` size (Same as Whisper).

    If ``show_dict`` is true, returns the detailed response from Whisper, including the detected language. Otherwise returns only the transcription.

    You can specify:

        * ``language``: recognition language, an uncapitalized 2 letters language name like "en" or "fr".

            * If not set, Faster Whisper will automatically detect the language.

        * ``task``

            * If you want transcribe + **translate** to english, set ``task="translate"``.

    Other values are passed directly to whisper. See https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/transcribe.py for all options.
    """
    from faster_whisper import WhisperModel

    model = WhisperModel(model, **init_options or {})
    whisper_recognizer = WhisperCompatibleRecognizer(
        TranscribableAdapter(model)
    )
    return whisper_recognizer.recognize(
        audio_data, show_dict=show_dict, **transcribe_options
    )


if __name__ == "__main__":
    import argparse

    import speech_recognition as sr

    parser = argparse.ArgumentParser()
    parser.add_argument("audio_file")
    args = parser.parse_args()

    audio_data = sr.AudioData.from_file(args.audio_file)
    transcription = recognize(None, audio_data)
    print(transcription)
