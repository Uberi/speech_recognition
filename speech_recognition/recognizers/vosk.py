from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from speech_recognition.audio import AudioData


def recognize(recognizer, audio_data: AudioData) -> str:
    """
    Perform speech recognition on ``audio_data`` using Vosk.

    Requires the Vosk model to be downloaded and unpacked in a folder named 'model' (``$PWD/model``).
    """

    from vosk import KaldiRecognizer, Model

    if not os.path.exists("model"):
        return "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder."

    SAMPLE_RATE = 16_000
    rec = KaldiRecognizer(Model("model"), SAMPLE_RATE)

    rec.AcceptWaveform(
        audio_data.get_raw_data(convert_rate=SAMPLE_RATE, convert_width=2)
    )
    finalRecognition = rec.FinalResult()

    return finalRecognition
