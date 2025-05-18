from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from speech_recognition.audio import AudioData


def recognize(recognizer, audio_data: AudioData) -> str:
    from vosk import KaldiRecognizer, Model

    if not os.path.exists("model"):
        return "Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder."

    rec = KaldiRecognizer(Model("model"), 16000)

    rec.AcceptWaveform(
        audio_data.get_raw_data(convert_rate=16000, convert_width=2)
    )
    finalRecognition = rec.FinalResult()

    return finalRecognition
