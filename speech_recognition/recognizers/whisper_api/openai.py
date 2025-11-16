from __future__ import annotations

import logging
from typing import Literal

from typing_extensions import Unpack

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import SetupError
from speech_recognition.recognizers.whisper_api.base import (
    OpenAICompatibleRecognizer,
)

# https://platform.openai.com/docs/api-reference/audio/createTranscription#audio-createtranscription-model
WhisperModel = Literal[
    "whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe"
]


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


if __name__ == "__main__":
    import argparse
    from typing import get_args

    import speech_recognition as sr

    parser = argparse.ArgumentParser()
    parser.add_argument("audio_file")
    parser.add_argument(
        "-m", "--model", choices=get_args(WhisperModel), default="whisper-1"
    )
    parser.add_argument("-l", "--language")
    parser.add_argument("-p", "--prompt")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        speech_recognition_logger = logging.getLogger("speech_recognition")
        speech_recognition_logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        speech_recognition_logger.addHandler(console_handler)

    audio_data = sr.AudioData.from_file(args.audio_file)

    recognize_args = {"model": args.model}
    if args.language:
        recognize_args["language"] = args.language
    if args.prompt:
        recognize_args["prompt"] = args.prompt

    transcription = recognize(None, audio_data, **recognize_args)
    print(transcription)
