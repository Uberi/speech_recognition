from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from urllib.error import URLError

from speech_recognition.audio import AudioData
from speech_recognition.exceptions import RequestError, UnknownValueError

if TYPE_CHECKING:
    from google.cloud.speech import (
        RecognitionConfig,
        RecognizeResponse,
        SpeechContext,
    )
    from typing_extensions import Required


class GoogleCloudRecognizerParameters(TypedDict, total=False):
    """Optional parameters.

    The recognition language is determined by ``language_code``, which is a BCP-47 language tag like ``"en-US"`` (US English). Default: ``"en-US"``.
    A list of supported language tags can be found in the `Speech-to-Text supported languages <https://cloud.google.com/speech/docs/languages>`__.

    If ``preferred_phrases`` is an iterable of phrase strings, those given phrases will be more likely to be recognized over similar-sounding alternatives.
    This is useful for things like keyword/command recognition or adding new phrases that aren't in Google's vocabulary.
    Note that the API imposes certain `restrictions on the list of phrase strings <https://cloud.google.com/speech/limits#content>`__.

    ``show_all``: See :py:func:`recognize`.

    ``model``: You can select the model to get best results. (See `RecognitionConfig's documentation <https://cloud.google.com/python/docs/reference/speech/latest/google.cloud.speech_v1.types.RecognitionConfig>`__ for detail)

    ``use_enhanced``: Set to true to use an enhanced model for speech recognition.
    """

    # SpeechRecognition specific parameters
    preferred_phrases: list[str]
    show_all: bool

    # Speech-to-Text V1 API's parameters
    language_code: str
    model: str
    use_enhanced: bool
    # TODO Add others support


class GoogleCloudSpeechV1Parameters(TypedDict, total=False):
    """Speech-to-Text V1 API's parameters.

    https://cloud.google.com/python/docs/reference/speech/latest/google.cloud.speech_v1.types.RecognitionConfig
    """

    encoding: Required[RecognitionConfig.AudioEncoding]
    sample_rate_hertz: Required[int]
    language_code: Required[str]
    speech_contexts: list[SpeechContext]
    enable_word_time_offsets: bool
    model: str
    use_enhanced: bool


def _build_config(
    audio_data: AudioData, recognizer_params: GoogleCloudRecognizerParameters
) -> RecognitionConfig:
    from google.cloud import speech

    parameters: GoogleCloudSpeechV1Parameters = {
        "encoding": speech.RecognitionConfig.AudioEncoding.FLAC,
        "sample_rate_hertz": audio_data.sample_rate,
        "language_code": recognizer_params.pop("language_code", "en-US"),
    }
    if preferred_phrases := recognizer_params.pop("preferred_phrases", None):
        parameters["speech_contexts"] = [
            speech.SpeechContext(phrases=preferred_phrases)
        ]
    if recognizer_params.pop("show_all", False):
        # ref: https://cloud.google.com/speech-to-text/docs/async-time-offsets
        parameters["enable_word_time_offsets"] = True
    return speech.RecognitionConfig(**(parameters | recognizer_params))


def recognize(
    recognizer,
    audio_data: AudioData,
    credentials_json_path: str | None = None,
    **kwargs: GoogleCloudRecognizerParameters,
) -> str | RecognizeResponse:
    """Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Google Cloud Speech-to-Text V1 API.

    This function requires a Google Cloud Platform account; see the `Set up Speech-to-Text <https://cloud.google.com/speech-to-text/docs/before-you-begin>`__ for details and instructions. Basically, create a project, enable billing for the project, enable the Google Cloud Speech API for the project.
    And create local authentication credentials for your user account. The result is a JSON file containing the API credentials. You can specify the JSON file by ``credentials_json_path``. If not specified, the library will try to automatically `find the default API credentials JSON file <https://developers.google.com/identity/protocols/application-default-credentials>`__.

    Returns the most likely transcription if ``show_all`` is False (the default). Otherwise, returns the raw API response as a JSON dictionary.
    For other parameters, see :py:class:`GoogleCloudRecognizerParameters`.

    Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the credentials aren't valid, or if there is no Internet connection.
    """
    try:
        from google.api_core.exceptions import GoogleAPICallError
        from google.cloud import speech
    except ImportError:
        raise RequestError(
            "missing google-cloud-speech module: ensure that google-cloud-speech is set up correctly."
        )

    client = (
        speech.SpeechClient.from_service_account_json(credentials_json_path)
        if credentials_json_path
        else speech.SpeechClient()
    )

    flac_data = audio_data.get_flac_data(
        # audio sample rate must be between 8 kHz and 48 kHz inclusive - clamp sample rate into this range
        convert_rate=(
            None
            if 8000 <= audio_data.sample_rate <= 48000
            else max(8000, min(audio_data.sample_rate, 48000))
        ),
        convert_width=2,  # audio samples must be 16-bit
    )
    audio = speech.RecognitionAudio(content=flac_data)

    config = _build_config(audio_data, kwargs.copy())

    try:
        response = client.recognize(config=config, audio=audio)
    except GoogleAPICallError as e:
        raise RequestError(e)
    except URLError as e:
        raise RequestError(
            "recognition connection failed: {0}".format(e.reason)
        )

    if kwargs.get("show_all"):
        return response
    if len(response.results) == 0:
        raise UnknownValueError()

    transcript = " ".join(
        result.alternatives[0].transcript.strip()
        for result in response.results
    )
    return transcript
