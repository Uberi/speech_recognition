from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypedDict, Union, cast, overload

from speech_recognition.exceptions import SetupError

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

    vosk_model_path = Path(__file__).parent.parent / "models" / "vosk"
    if not vosk_model_path.exists():
        raise SetupError(
            f"Vosk model not found at {vosk_model_path}. "
            "Please download the model using `sprc download vosk` command."
        )

    SAMPLE_RATE = 16_000
    rec = KaldiRecognizer(Model(str(vosk_model_path)), SAMPLE_RATE)

    rec.AcceptWaveform(
        audio_data.get_raw_data(convert_rate=SAMPLE_RATE, convert_width=2)
    )
    final_recognition: str = rec.FinalResult()

    result = cast(VoskResponse, json.loads(final_recognition))
    if verbose:
        return result

    return result["text"]
