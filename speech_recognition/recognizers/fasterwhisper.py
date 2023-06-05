from __future__ import annotations

import os
from io import BytesIO

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import SetupError


def recognize_faster_whisper(
    recognizer,
    audio_data: "AudioData",
    model="base",
    beam_size=5,
    device="auto",
    compute_type="int8",
    show_dict=False,
    language=None,
    translate=False,
    **transcribe_options
):
    """
    Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Faster Whisper implementation of OpenAI Whisper.

    Detail: https://github.com/guillaumekln/faster-whisper

    Most options are identical to the original Whisper function. New options are:

    {beam_size}: Allows overriding the default beam size if desired.
    {device}: Allows setting the device, e.g. "auto", "cpu", "cuda", etc.
    {compute_type}: Allows setting the compute type, e.g. "int8", "float16", etc.

    The return dict is also customized to avoid returning a mess of FasterWhisper objects.
    """

    assert isinstance(audio_data, AudioData), "Data must be audio data"

    import numpy as np
    import soundfile as sf
    import faster_whisper

    print(f"model: {model}, beam_size: {beam_size}, device: {device}, compute_type: {compute_type}, language: {language}, translate: {translate}")

    whisper_model = faster_whisper.WhisperModel(model, device=device, compute_type=compute_type)

    # 16 kHz https://github.com/openai/whisper/blob/28769fcfe50755a817ab922a7bc83483159600a9/whisper/audio.py#L98-L99
    wav_bytes = audio_data.get_wav_data(convert_rate=16000)
    wav_stream = BytesIO(wav_bytes)
    audio_array, sampling_rate = sf.read(wav_stream)
    audio_array = audio_array.astype(np.float32)

    segments, info = whisper_model.transcribe(
        audio_array,
        beam_size=beam_size,
        language=language,
        task="translate" if translate else None,
        **transcribe_options
    )
    found_text = list()
    for segment in segments:
        found_text.append(segment.text)
    text = ' '.join(found_text).strip()

    if show_dict:
        result = {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
        }
    else:
        result = text

    return result
