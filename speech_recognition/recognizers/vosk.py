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
    _recognizer, audio_data: AudioData, *, verbose: Literal[False]
) -> str: ...


@overload
def recognize(  # noqa: E704
    _recognizer, audio_data: AudioData, *, verbose: Literal[True]
) -> VoskResponse: ...


def recognize(
    _recognizer, audio_data: AudioData, *, verbose: bool = False
) -> Union[str, VoskResponse]:
    """
    Perform speech recognition on ``audio_data`` using Vosk.

    Requires the Vosk model to be downloaded and unpacked in a folder named 'model' (``$PWD/model``).

    If ``verbose`` is ``False`` (default), only the recognized text is returned.
    If ``verbose`` is ``True``, the parsed result dictionary from Vosk is returned.
    """

    from vosk import KaldiRecognizer, Model
    import speech_recognition

    # Look for the model in the speech_recognition package directory
    package_model_dir = os.path.join(os.path.dirname(speech_recognition.__file__), "model")
    # Check if model exists in the package directory
    if os.path.exists(package_model_dir):
        model_path = package_model_dir
    # Fallback to current directory for backward compatibility
    elif os.path.exists("model"):
        model_path = "model"
    else:
        return "Please download the model using 'sprc download vosk' command."

    SAMPLE_RATE = 16_000
    rec = KaldiRecognizer(Model(model_path), SAMPLE_RATE)

    rec.AcceptWaveform(
        audio_data.get_raw_data(convert_rate=SAMPLE_RATE, convert_width=2)
    )
    final_recognition: str = rec.FinalResult()

    result = cast(VoskResponse, json.loads(final_recognition))
    if verbose:
        return result

    return result["text"]
