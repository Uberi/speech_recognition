import io
from typing import Any, Protocol

from speech_recognition.audio import AudioData


class Transcribable(Protocol):
    def transcribe(self, audio_array, **kwargs) -> str | dict[str, Any]:
        pass


class WhisperCompatibleRecognizer:
    def __init__(self, model: Transcribable) -> None:
        self.model = model

    def recognize(
        self, audio_data: AudioData, show_dict: bool = False, **kwargs
    ):
        if not isinstance(audio_data, AudioData):
            raise ValueError(
                "``audio_data`` must be an ``AudioData`` instance"
            )

        import numpy as np
        import soundfile as sf

        # 16 kHz https://github.com/openai/whisper/blob/28769fcfe50755a817ab922a7bc83483159600a9/whisper/audio.py#L98-L99
        wav_bytes = audio_data.get_wav_data(convert_rate=16000)
        wav_stream = io.BytesIO(wav_bytes)
        audio_array, sampling_rate = sf.read(wav_stream)
        audio_array = audio_array.astype(np.float32)

        if "fp16" not in kwargs:
            import torch

            kwargs["fp16"] = torch.cuda.is_available()
        result = self.model.transcribe(audio_array, **kwargs)

        if show_dict:
            return result
        else:
            return result["text"]
