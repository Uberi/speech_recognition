import os
from io import BytesIO

from speech_recognition.audio import AudioData


def recognize_whisper_api(
    recognizer, audio_data, *, model="whisper-1", api_key=None
):
    if not isinstance(audio_data, AudioData):
        raise ValueError("``audio_data`` must be an ``AudioData`` instance")
    if api_key is None and os.environ.get("OPENAI_API_KEY") is None:
        raise ValueError("Set environment variable ``OPENAI_API_KEY``")

    import openai

    wav_data = BytesIO(audio_data.get_wav_data())
    wav_data.name = "SpeechRecognition_audio.wav"

    transcript = openai.Audio.transcribe(model, wav_data, api_key=api_key)
    return transcript["text"]
