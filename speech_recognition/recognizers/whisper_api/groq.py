from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import Unpack

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import SetupError
from speech_recognition.recognizers.whisper_api.base import (
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


def recognize(
    recognizer,
    audio_data: "AudioData",
    *,
    model: GroqModel = "whisper-large-v3-turbo",
    **kwargs: Unpack[GroqOptionalParameters],
) -> str:
    """Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Groq Whisper API.

    This function requires login to Groq; visit https://console.groq.com/login, then generate API Key in `API Keys <https://console.groq.com/keys>`__ menu.

    Detail: https://console.groq.com/docs/speech-text

    Set environment variable ``GROQ_API_KEY``; otherwise groq library will raise a ``groq.GroqError``.
    """
    try:
        import groq
    except ImportError:
        raise SetupError(
            "missing groq module: ensure that groq is set up correctly."
        )

    groq_recognizer = OpenAICompatibleRecognizer(groq.Groq())
    return groq_recognizer.recognize(audio_data, model, **kwargs)
