from __future__ import annotations

from typing import Literal

from typing_extensions import Unpack

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import SetupError
from speech_recognition.recognizers.whisper_api.base import (
    OpenAICompatibleRecognizer,
)

# https://platform.openai.com/docs/api-reference/audio/createTranscription#audio-createtranscription-model
WhisperModel = Literal["whisper-1"]


class OpenAIOptionalParameters:
    """OpenAI speech transcription's optional parameters.

    https://platform.openai.com/docs/api-reference/audio/createTranscription
    """

    language: str
    prompt: str
    # TODO Add support `Literal["text", "srt", "verbose_json", "vtt"]`
    response_format: Literal["json"]
    temperature: float
    # timestamp_granularities  # TODO support


def recognize(
    recognizer,
    audio_data: "AudioData",
    *,
    model: WhisperModel = "whisper-1",
    **kwargs: Unpack[OpenAIOptionalParameters],
) -> str:
    """Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the OpenAI Whisper API.

    This function requires an OpenAI account; visit https://platform.openai.com/signup, then generate API Key in `User settings <https://platform.openai.com/account/api-keys>`__.

    Detail: https://platform.openai.com/docs/guides/speech-to-text

    Set environment variable ``OPENAI_API_KEY``; otherwise openai library will raise a ``openai.OpenAIError``.
    """
    try:
        import openai
    except ImportError:
        raise SetupError(
            "missing openai module: ensure that openai is set up correctly."
        )

    openai_recognizer = OpenAICompatibleRecognizer(openai.OpenAI())
    return openai_recognizer.recognize(audio_data, model, **kwargs)
