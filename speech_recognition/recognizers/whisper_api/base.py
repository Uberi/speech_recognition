import logging
from io import BytesIO

from speech_recognition.audio import AudioData

logger = logging.getLogger(__name__)


class OpenAICompatibleRecognizer:
    def __init__(self, client) -> None:
        self.client = client

    def recognize(self, audio_data: "AudioData", model: str, **kwargs) -> str:
        if not isinstance(audio_data, AudioData):
            raise ValueError(
                "``audio_data`` must be an ``AudioData`` instance"
            )

        wav_data = BytesIO(audio_data.get_wav_data())
        wav_data.name = "SpeechRecognition_audio.wav"

        parameters = {"model": model, **kwargs}
        logger.debug(parameters)

        transcript = self.client.audio.transcriptions.create(
            file=wav_data, **parameters
        )
        return transcript.text
