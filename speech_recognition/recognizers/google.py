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

ENDPOINT = "http://www.google.com/speech-api/v2/recognize"


class RequestBuilder:
    def __init__(
        self,
        *,
        endpoint: str,
        key: str,
        language: str,
        filter_level: ProfanityFilterLevel,
    ) -> None:
        self.endpoint = endpoint
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
        >>> builder = RequestBuilder(endpoint="http://www.google.com/speech-api/v2/recognize", key="awesome-key", language="en-US", filter_level=0)
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
        >>> builder = RequestBuilder(endpoint="", key="", language="", filter_level=1)
        >>> audio_data = AudioData(b"", 16_000, 1)
        >>> builder.build_headers(audio_data)
        {'Content-Type': 'audio/x-flac; rate=16000'}
        """
        rate = audio_data.sample_rate
        headers = {"Content-Type": f"audio/x-flac; rate={rate}"}
        return headers

    def build_data(self, audio_data: AudioData) -> bytes:
        flac_data = audio_data.get_flac_data(
            convert_rate=self.to_convert_rate(audio_data.sample_rate),
            convert_width=2,  # audio samples must be 16-bit
        )
        return flac_data

    @staticmethod
    def to_convert_rate(sample_rate: int) -> int:
        """Audio samples must be at least 8 kHz

        >>> RequestBuilder.to_convert_rate(16_000)
        >>> RequestBuilder.to_convert_rate(8_000)
        >>> RequestBuilder.to_convert_rate(7_999)
        8000
        """
        return None if sample_rate >= 8000 else 8000


def create_request_builder(
    *,
    endpoint: str,
    key: str | None = None,
    language: str = "en-US",
    filter_level: ProfanityFilterLevel = 0,
) -> RequestBuilder:
    if not isinstance(language, str):
        raise ValueError("``language`` must be a string")
    if key is not None and not isinstance(key, str):
        raise ValueError("``key`` must be ``None`` or a string")

    if key is None:
        key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
    return RequestBuilder(
        endpoint=endpoint,
        key=key,
        language=language,
        filter_level=filter_level,
    )


class OutputParser:
    def __init__(self, *, show_all: bool, with_confidence: bool) -> None:
        self.show_all = show_all
        self.with_confidence = with_confidence

    def parse(self, response_text: str):
        actual_result = self.convert_to_result(response_text)
        if self.show_all:
            return actual_result

        best_hypothesis = self.find_best_hypothesis(
            actual_result["alternative"]
        )
        # https://cloud.google.com/speech-to-text/docs/basics#confidence-values
        # "Your code should not require the confidence field as it is not guaranteed to be accurate, or even set, in any of the results."
        confidence = best_hypothesis.get("confidence", 0.5)
        if self.with_confidence:
            return best_hypothesis["transcript"], confidence
        return best_hypothesis["transcript"]

    @staticmethod
    def convert_to_result(response_text: str) -> Result:
        r"""
        >>> response_text = '''{"result":[]}
        ... {"result":[{"alternative":[{"transcript":"one two three","confidence":0.49585345},{"transcript":"1 2","confidence":0.42899391}],"final":true}],"result_index":0}
        ... '''
        >>> OutputParser.convert_to_result(response_text)
        {'alternative': [{'transcript': 'one two three', 'confidence': 0.49585345}, {'transcript': '1 2', 'confidence': 0.42899391}], 'final': True}

        >>> OutputParser.convert_to_result("")
        Traceback (most recent call last):
          ...
        speech_recognition.exceptions.UnknownValueError
        >>> OutputParser.convert_to_result('\n{"result":[]}')
        Traceback (most recent call last):
          ...
        speech_recognition.exceptions.UnknownValueError
        >>> OutputParser.convert_to_result('{"result":[{"foo": "bar"}]}')
        Traceback (most recent call last):
          ...
        speech_recognition.exceptions.UnknownValueError
        >>> OutputParser.convert_to_result('{"result":[{"alternative": []}]}')
        Traceback (most recent call last):
          ...
        speech_recognition.exceptions.UnknownValueError
        """
        # ignore any blank blocks
        for line in response_text.split("\n"):
            if not line:
                continue
            result: list[Result] = json.loads(line)["result"]
            if len(result) != 0:
                if len(result[0].get("alternative", [])) == 0:
                    raise UnknownValueError()
                return result[0]
        raise UnknownValueError()

    @staticmethod
    def find_best_hypothesis(alternatives: list[Alternative]) -> Alternative:
        """
        >>> alternatives = [{"transcript": "one two three", "confidence": 0.42899391}, {"transcript": "1 2", "confidence": 0.49585345}]
        >>> OutputParser.find_best_hypothesis(alternatives)
        {'transcript': 'one two three', 'confidence': 0.42899391}

        >>> alternatives = [{"confidence": 0.49585345}]
        >>> OutputParser.find_best_hypothesis(alternatives)
        Traceback (most recent call last):
          ...
        speech_recognition.exceptions.UnknownValueError
        """
        if "confidence" in alternatives:
            # BUG: actual_result["alternative"] (=alternatives) is list, not dict
            # return alternative with highest confidence score
            best_hypothesis: Alternative = max(
                alternatives,
                key=lambda alternative: alternative["confidence"],
            )
        else:
            # when there is no confidence available, we arbitrarily choose the first hypothesis.
            best_hypothesis: Alternative = alternatives[0]
        if "transcript" not in best_hypothesis:
            raise UnknownValueError()
        return best_hypothesis


def obtain_transcription(request: Request, timeout: int) -> str:
    try:
        response = urlopen(request, timeout=timeout)
    except HTTPError as e:
        raise RequestError("recognition request failed: {}".format(e.reason))
    except URLError as e:
        raise RequestError(
            "recognition connection failed: {}".format(e.reason)
        )
    return response.read().decode("utf-8")


def recognize_legacy(
    recognizer,
    audio_data: AudioData,
    key: str | None = None,
    language: str = "en-US",
    pfilter: ProfanityFilterLevel = 0,
    show_all: bool = False,
    with_confidence: bool = False,
    *,
    endpoint: str = ENDPOINT,
):
    """Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Google Speech Recognition API.

    The Google Speech Recognition API key is specified by ``key``. If not specified, it uses a generic key that works out of the box. This should generally be used for personal or testing purposes only, as it **may be revoked by Google at any time**.

    To obtain your own API key, simply following the steps on the `API Keys <http://www.chromium.org/developers/how-tos/api-keys>`__ page at the Chromium Developers site. In the Google Developers Console, Google Speech Recognition is listed as "Speech API".

    The recognition language is determined by ``language``, an RFC5646 language tag like ``"en-US"`` (US English) or ``"fr-FR"`` (International French), defaulting to US English. A list of supported language tags can be found in this `StackOverflow answer <http://stackoverflow.com/a/14302134>`__.

    The profanity filter level can be adjusted with ``pfilter``: 0 - No filter, 1 - Only shows the first character and replaces the rest with asterisks. The default is level 0.

    Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the raw API response as a JSON dictionary.

    Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.
    """
    request_builder = create_request_builder(
        endpoint=endpoint, key=key, language=language, filter_level=pfilter
    )
    request = request_builder.build(audio_data)

    response_text = obtain_transcription(
        request, timeout=recognizer.operation_timeout
    )

    output_parser = OutputParser(
        show_all=show_all, with_confidence=with_confidence
    )
    return output_parser.parse(response_text)
