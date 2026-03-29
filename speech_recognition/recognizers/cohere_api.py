from __future__ import annotations

import logging
from io import BytesIO

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import SetupError

logger = logging.getLogger(__name__)


def recognize(
    recognizer,
    audio_data: AudioData,
    *,
    language: str,
    model: str = "cohere-transcribe-03-2026",
) -> str:
    """Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the `Cohere Transcribe <https://docs.cohere.com/docs/transcribe>`__ API via the official Python SDK.

    Requires the ``cohere`` package (install with ``pip install SpeechRecognition[cohere-api]``).
    Set environment variable ``CO_API_KEY`` as documented by Cohere; this library does not read or override it in code.

    ``language`` is required by the Cohere transcription API (e.g. ``\"en\"``, ``\"ja\"``).

    Detail: https://docs.cohere.com/reference/create-audio-transcription
    """
    try:
        import cohere
    except ImportError:
        raise SetupError(
            "missing cohere module: ensure that cohere is set up correctly "
            "(e.g. pip install SpeechRecognition[cohere-api])."
        )

    if not isinstance(audio_data, AudioData):
        raise ValueError("``audio_data`` must be an ``AudioData`` instance")

    wav_data = BytesIO(audio_data.get_wav_data())
    wav_data.name = "SpeechRecognition_audio.wav"

    client = cohere.ClientV2()
    logger.debug(
        "cohere audio.transcriptions.create: model=%r language=%r",
        model,
        language,
    )
    response = client.audio.transcriptions.create(
        model=model,
        file=wav_data,
        language=language,
    )
    return response.text
