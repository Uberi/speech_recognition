from __future__ import annotations

import os
from io import BytesIO

from speech_recognition.audio import AudioData


def recognize_whisper_api(
    recognizer,
    audio_data: "AudioData",
    *,
    model: str = "whisper-1",
    api_key: str | None = None,
):
    """
    Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the OpenAI Whisper API.

    This function requires an OpenAI account; visit https://platform.openai.com/signup, then generate API Key in `User settings <https://platform.openai.com/account/api-keys>`__.

    Detail: https://platform.openai.com/docs/guides/speech-to-text
    """
    if not isinstance(audio_data, AudioData):
        raise ValueError("``audio_data`` must be an ``AudioData`` instance")
    if api_key is None and os.environ.get("OPENAI_API_KEY") is None:
        raise ValueError("Set environment variable ``OPENAI_API_KEY``")

    import openai

    wav_data = BytesIO(audio_data.get_wav_data())
    wav_data.name = "SpeechRecognition_audio.wav"

    transcript = openai.Audio.transcribe(model, wav_data, api_key=api_key)
    return transcript["text"]
