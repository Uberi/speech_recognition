from __future__ import annotations

import os

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import SetupError
from speech_recognition.recognizers.whisper_api import (
    OpenAICompatibleRecognizer,
)


def recognize_groq(
    recognizer,
    audio_data: "AudioData",
    *,
    model: str = "whisper-large-v3-turbo",
) -> str:
    if os.environ.get("GROQ_API_KEY") is None:
        raise SetupError("Set environment variable ``GROQ_API_KEY``")

    try:
        import groq
    except ImportError:
        raise SetupError(
            "missing groq module: ensure that groq is set up correctly."
        )

    recognizer = OpenAICompatibleRecognizer(groq.Groq())
    return recognizer.recognize(audio_data, model)
