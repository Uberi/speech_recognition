from __future__ import annotations

import os
from io import BytesIO

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import SetupError


def recognize_groq(
    recognizer,
    audio_data: "AudioData",
    *,
    model: str = "whisper-large-v3-turbo",
):
    if not isinstance(audio_data, AudioData):
        raise ValueError("``audio_data`` must be an ``AudioData`` instance")
    if os.environ.get("GROQ_API_KEY") is None:
        raise SetupError("Set environment variable ``GROQ_API_KEY``")

    try:
        import groq
    except ImportError:
        raise SetupError(
            "missing groq module: ensure that groq is set up correctly."
        )

    wav_data = BytesIO(audio_data.get_wav_data())
    wav_data.name = "SpeechRecognition_audio.wav"

    client = groq.Groq()
    transcript = client.audio.transcriptions.create(file=wav_data, model=model)
    return transcript.text
