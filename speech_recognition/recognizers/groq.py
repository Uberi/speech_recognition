from __future__ import annotations

import os
from typing import Literal, TypedDict
from typing_extensions import Unpack

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import SetupError
from speech_recognition.recognizers.whisper_api import (
    OpenAICompatibleRecognizer,
)

# https://console.groq.com/docs/speech-text#supported-models
GroqModel = Literal[
    "whisper-large-v3-turbo", "whisper-large-v3", "distil-whisper-large-v3-en"
]


class GroqOptionalParameters(TypedDict):
    """Groq speech transcription's optional parameters.

    https://console.groq.com/docs/speech-text#transcription-endpoint-usage
    """

    prompt: str
    response_format: str
    temperature: float
    language: str


def recognize_groq(
    recognizer,
    audio_data: "AudioData",
    *,
    model: GroqModel = "whisper-large-v3-turbo",
    **kwargs: Unpack[GroqOptionalParameters],
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
