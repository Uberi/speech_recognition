from __future__ import annotations

import io

from speech_recognition.audio import AudioData


def recognize(
    self,
    audio_data: AudioData,
    model: str = "base",
    show_dict: bool = False,
    load_options=None,
    language: str | None = None,
    translate: bool = False,
    **transcribe_options,
):
    """
    Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using Whisper.

    The recognition language is determined by ``language``, an uncapitalized full language name like "english" or "chinese". See the full language list at https://github.com/openai/whisper/blob/main/whisper/tokenizer.py

    model can be any of tiny, base, small, medium, large, tiny.en, base.en, small.en, medium.en. See https://github.com/openai/whisper for more details.

    If show_dict is true, returns the full dict response from Whisper, including the detected language. Otherwise returns only the transcription.

    You can translate the result to english with Whisper by passing translate=True

    Other values are passed directly to whisper. See https://github.com/openai/whisper/blob/main/whisper/transcribe.py for all options
    """

    import numpy as np
    import soundfile as sf
    import torch
    import whisper

    if (
        load_options
        or not hasattr(self, "whisper_model")
        or self.whisper_model.get(model) is None
    ):
        self.whisper_model = getattr(self, "whisper_model", {})
        self.whisper_model[model] = whisper.load_model(
            model, **load_options or {}
        )

    # 16 kHz https://github.com/openai/whisper/blob/28769fcfe50755a817ab922a7bc83483159600a9/whisper/audio.py#L98-L99
    wav_bytes = audio_data.get_wav_data(convert_rate=16000)
    wav_stream = io.BytesIO(wav_bytes)
    audio_array, sampling_rate = sf.read(wav_stream)
    audio_array = audio_array.astype(np.float32)

    result = self.whisper_model[model].transcribe(
        audio_array,
        language=language,
        task="translate" if translate else None,
        fp16=torch.cuda.is_available(),
        **transcribe_options,
    )

    if show_dict:
        return result
    else:
        return result["text"]
