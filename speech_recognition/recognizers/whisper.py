from io import BytesIO


def recognize_whisper_api(
    recognizer, audio_data, *, model="whisper-1", api_key=None
):
    import openai

    wav_data = BytesIO(audio_data.get_wav_data())
    wav_data.name = "SpeechRecognition_audio.wav"

    transcript = openai.Audio.transcribe(model, wav_data, api_key=api_key)
    return transcript["text"]
