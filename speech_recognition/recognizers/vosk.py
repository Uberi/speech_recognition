from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Literal, TypedDict, Union, cast, overload

if TYPE_CHECKING:
    from speech_recognition.audio import AudioData


class VoskResponse(TypedDict):
    text: str


@overload
def recognize(  # noqa: E704
    recognizer, audio_data: AudioData, *, verbose: Literal[False]
) -> str: ...


@overload
def recognize(  # noqa: E704
    recognizer, audio_data: AudioData, *, verbose: Literal[True]
) -> VoskResponse: ...


def recognize(
    recognizer, audio_data: AudioData, *, verbose: bool = False
) -> Union[str, VoskResponse]:
    """
    Perform speech recognition on ``audio_data`` using Vosk.

    Requires the Vosk model to be downloaded and unpacked in a folder named 'model' (``$PWD/model``).

    If ``verbose`` is ``False`` (default), only the recognized text is returned.
    If ``verbose`` is ``True``, the parsed result dictionary from Vosk is returned.
    """

    from vosk import KaldiRecognizer, Model

    if not os.path.exists("model"):
        return "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder."

    SAMPLE_RATE = 16_000
    rec = KaldiRecognizer(Model("model"), SAMPLE_RATE)

    rec.AcceptWaveform(
        audio_data.get_raw_data(convert_rate=SAMPLE_RATE, convert_width=2)
    )
    final_recognition: str = rec.FinalResult()

    result = cast(VoskResponse, json.loads(final_recognition))
    if verbose:
        return result

    return result["text"]
