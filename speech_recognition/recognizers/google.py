from __future__ import annotations

import json
from typing import Dict, Literal, TypedDict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from typing_extensions import NotRequired

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import RequestError, UnknownValueError


class Alternative(TypedDict):
    transcript: str
    confidence: float


class Result(TypedDict):
    alternative: list[Alternative]
    final: bool


class GoogleResponse(TypedDict):
    result: list[Result]
    result_index: NotRequired[int]


ProfanityFilterLevel = Literal[0, 1]
RequestHeaders = Dict[str, str]


class RequestBuilder:
    endpoint = "http://www.google.com/speech-api/v2/recognize"

    def __init__(
        self, *, key: str, language: str, filter_level: ProfanityFilterLevel
    ) -> None:
        self.key = key
        self.language = language
        self.filter_level = filter_level

    def build(self, audio_data: AudioData) -> Request:
        if not isinstance(audio_data, AudioData):
            raise ValueError("``audio_data`` must be audio data")

        url = self.build_url()
        headers = self.build_headers(audio_data)
        flac_data = self.build_data(audio_data)
        request = Request(url, data=flac_data, headers=headers)
        return request

    def build_url(self) -> str:
        """
        >>> builder = RequestBuilder(key="awesome-key", language="en-US", filter_level=0)
        >>> builder.build_url()
        'http://www.google.com/speech-api/v2/recognize?client=chromium&lang=en-US&key=awesome-key&pFilter=0'
        """
        params = urlencode(
            {
                "client": "chromium",
                "lang": self.language,
                "key": self.key,
                "pFilter": self.filter_level,
            }
        )
        return f"{self.endpoint}?{params}"

    def build_headers(self, audio_data: AudioData) -> RequestHeaders:
        """
        >>> builder = RequestBuilder(key="", language="", filter_level=1)
        >>> audio_data = AudioData(b"", 16_000, 1)
        >>> builder.build_headers(audio_data)
        {'Content-Type': 'audio/x-flac; rate=16000'}
        """
        rate = audio_data.sample_rate
        headers = {"Content-Type": f"audio/x-flac; rate={rate}"}
        return headers

    def build_data(self, audio_data: AudioData) -> bytes:
        flac_data = audio_data.get_flac_data(
            convert_rate=None
            if audio_data.sample_rate >= 8000
            else 8000,  # audio samples must be at least 8 kHz
            convert_width=2,  # audio samples must be 16-bit
        )
        return flac_data


def create_request_builder(
    *,
    key: str | None = None,
    language: str = "en-US",
    filter_level: ProfanityFilterLevel = 0,
) -> RequestBuilder:
    if not isinstance(language, str):
        raise ValueError("``language`` must be a string")
    if key is not None and not isinstance(key, str):
        raise "``key`` must be ``None`` or a string"

    if key is None:
        key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
    return RequestBuilder(
        key=key, language=language, filter_level=filter_level
    )


def recognize_legacy(
    recognizer,
    audio_data: AudioData,
    key: str | None = None,
    language: str = "en-US",
    pfilter: ProfanityFilterLevel = 0,
    show_all: bool = False,
    with_confidence: bool = False,
):
    """
    Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Google Speech Recognition API.

    The Google Speech Recognition API key is specified by ``key``. If not specified, it uses a generic key that works out of the box. This should generally be used for personal or testing purposes only, as it **may be revoked by Google at any time**.

    To obtain your own API key, simply following the steps on the `API Keys <http://www.chromium.org/developers/how-tos/api-keys>`__ page at the Chromium Developers site. In the Google Developers Console, Google Speech Recognition is listed as "Speech API".

    The recognition language is determined by ``language``, an RFC5646 language tag like ``"en-US"`` (US English) or ``"fr-FR"`` (International French), defaulting to US English. A list of supported language tags can be found in this `StackOverflow answer <http://stackoverflow.com/a/14302134>`__.

    The profanity filter level can be adjusted with ``pfilter``: 0 - No filter, 1 - Only shows the first character and replaces the rest with asterisks. The default is level 0.

    Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the raw API response as a JSON dictionary.

    Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.
    """
    request_builder = create_request_builder(
        key=key, language=language, filter_level=pfilter
    )
    request = request_builder.build(audio_data)

    # obtain audio transcription results
    try:
        response = urlopen(request, timeout=recognizer.operation_timeout)
    except HTTPError as e:
        raise RequestError("recognition request failed: {}".format(e.reason))
    except URLError as e:
        raise RequestError(
            "recognition connection failed: {}".format(e.reason)
        )
    response_text = response.read().decode("utf-8")

    # ignore any blank blocks
    actual_result = []
    for line in response_text.split("\n"):
        if not line:
            continue
        result: list[Result] = json.loads(line)["result"]
        if len(result) != 0:
            actual_result: Result = result[0]
            break

    # return results
    if show_all:
        return actual_result

    if (
        not isinstance(actual_result, dict)
        or len(actual_result.get("alternative", [])) == 0
    ):
        raise UnknownValueError()

    if "confidence" in actual_result["alternative"]:
        # return alternative with highest confidence score
        best_hypothesis: Alternative = max(
            actual_result["alternative"],
            key=lambda alternative: alternative["confidence"],
        )
    else:
        # when there is no confidence available, we arbitrarily choose the first hypothesis.
        best_hypothesis: Alternative = actual_result["alternative"][0]
    if "transcript" not in best_hypothesis:
        raise UnknownValueError()
    # https://cloud.google.com/speech-to-text/docs/basics#confidence-values
    # "Your code should not require the confidence field as it is not guaranteed to be accurate, or even set, in any of the results."
    confidence = best_hypothesis.get("confidence", 0.5)
    if with_confidence:
        return best_hypothesis["transcript"], confidence
    return best_hypothesis["transcript"]
