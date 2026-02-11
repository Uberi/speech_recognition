from __future__ import annotations

from typing import Literal, TypedDict

from typing_extensions import Unpack

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import SetupError
from speech_recognition.recognizers.whisper_api.base import (
    OpenAICompatibleRecognizer,
)

# https://console.groq.com/docs/speech-to-text#supported-models
GroqModel = Literal[
    "whisper-large-v3-turbo", "whisper-large-v3"
]


class GroqOptionalParameters(TypedDict, total=False):
    """Groq speech transcription's optional parameters.

    https://console.groq.com/docs/api-reference#audio-transcription
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

    Detail: https://console.groq.com/docs/speech-to-text

    Set environment variable ``GROQ_API_KEY``; otherwise groq library will raise a ``groq.GroqError``.
    """
    try:
        import groq
    except ImportError:
        raise SetupError(
            "missing groq module: ensure that groq is set up correctly."
        )

    proxy_url = getattr(recognizer, "proxy_url", None)
    client_kwargs = {}
    if proxy_url is not None:
        from speech_recognition.proxy import build_httpx_client

        http_client = build_httpx_client(proxy_url)
        if http_client is not None:
            client_kwargs["http_client"] = http_client

    groq_recognizer = OpenAICompatibleRecognizer(groq.Groq(**client_kwargs))
    return groq_recognizer.recognize(audio_data, model, **kwargs)
