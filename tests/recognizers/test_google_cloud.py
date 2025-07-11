from unittest.mock import MagicMock, patch

from google.cloud.speech import (
    RecognitionAudio,
    RecognitionConfig,
    RecognizeResponse,
    SpeechContext,
    SpeechRecognitionAlternative,
    SpeechRecognitionResult,
    WordInfo,
)

from speech_recognition import Recognizer
from speech_recognition.audio import AudioData
from speech_recognition.recognizers.google_cloud import recognize


@patch("google.cloud.speech.SpeechClient")
def test_transcribe_with_google_cloud_speech(SpeechClient):
    client = SpeechClient.return_value
    # ref: https://cloud.google.com/speech-to-text/docs/transcribe-gcloud?hl=ja#make_an_audio_transcription_request
    client.recognize.return_value = RecognizeResponse(
        results=[
            SpeechRecognitionResult(
                alternatives=[
                    SpeechRecognitionAlternative(
                        transcript="how old is the Brooklyn Bridge",
                        confidence=0.9840146,
                    )
                ]
            )
        ]
    )

    audio_data = MagicMock(spec=AudioData)
    audio_data.sample_rate = 16_000
    audio_data.get_flac_data.return_value = b"flac_data"

    actual = recognize(MagicMock(spec=Recognizer), audio_data)

    assert actual == "how old is the Brooklyn Bridge"
    SpeechClient.assert_called_once_with()
    client.recognize.assert_called_once_with(
        config=RecognitionConfig(
            encoding=RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=16_000,
            language_code="en-US",
        ),
        audio=RecognitionAudio(content=b"flac_data"),
    )


@patch("google.cloud.speech.SpeechClient")
def test_transcribe_with_specified_credentials(SpeechClient):
    client = SpeechClient.from_service_account_json.return_value
    client.recognize.return_value = RecognizeResponse(
        results=[
            SpeechRecognitionResult(
                alternatives=[
                    SpeechRecognitionAlternative(
                        transcript="transcript", confidence=0.9
                    )
                ]
            )
        ]
    )

    audio_data = MagicMock(spec=AudioData)
    audio_data.sample_rate = 16_000
    audio_data.get_flac_data.return_value = b"flac_data"

    _ = recognize(
        MagicMock(spec=Recognizer),
        audio_data,
        credentials_json_path="path/to/credentials.json",
    )

    SpeechClient.from_service_account_json.assert_called_once_with(
        "path/to/credentials.json"
    )


@patch("google.cloud.speech.SpeechClient")
def test_transcribe_with_specified_credentials_json(SpeechClient):
    client = SpeechClient.from_service_account_info.return_value
    client.recognize.return_value = RecognizeResponse(
        results=[
            SpeechRecognitionResult(
                alternatives=[
                    SpeechRecognitionAlternative(
                        transcript="transcript", confidence=0.9
                    )
                ]
            )
        ]
    )

    audio_data = MagicMock(spec=AudioData)
    audio_data.sample_rate = 16_000
    audio_data.get_flac_data.return_value = b"flac_data"

    _ = recognize(
        MagicMock(spec=Recognizer),
        audio_data,
        credentials_json={
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "client_email": "",
            "client_id": "",
            "client_x509_cert_url": "",
            "private_key": "",
            "private_key_id": "",
            "project_id": "",
            "token_uri": "https://oauth2.googleapis.com/token",
            "type": "service_account"
        },
    )

    SpeechClient.from_service_account_info.assert_called_once_with(
        {
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "client_email": "",
            "client_id": "",
            "client_x509_cert_url": "",
            "private_key": "",
            "private_key_id": "",
            "project_id": "",
            "token_uri": "https://oauth2.googleapis.com/token",
            "type": "service_account"
        }
    )


@patch("google.cloud.speech.SpeechClient")
def test_transcribe_show_all(SpeechClient):
    client = SpeechClient.return_value
    client.recognize.return_value = RecognizeResponse(
        results=[
            SpeechRecognitionResult(
                alternatives=[
                    SpeechRecognitionAlternative(
                        transcript="transcript",
                        confidence=0.9,
                        words=[
                            WordInfo(
                                word="transcript",
                                start_time="0s",
                                end_time="0.400s",
                            )
                        ],
                    )
                ],
                language_code="en-US",
                result_end_time="0.400s",
            )
        ]
    )

    audio_data = MagicMock(spec=AudioData)
    audio_data.sample_rate = 16_000
    audio_data.get_flac_data.return_value = b"flac_data"

    actual = recognize(MagicMock(spec=Recognizer), audio_data, show_all=True)

    assert actual == RecognizeResponse(
        results=[
            SpeechRecognitionResult(
                alternatives=[
                    SpeechRecognitionAlternative(
                        transcript="transcript",
                        confidence=0.9,
                        words=[
                            WordInfo(
                                word="transcript",
                                start_time="0s",
                                end_time="0.400s",
                            )
                        ],
                    )
                ],
                language_code="en-US",
                result_end_time="0.400s",
            )
        ]
    )
    client.recognize.assert_called_once_with(
        config=RecognitionConfig(
            encoding=RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=16_000,
            language_code="en-US",
            enable_word_time_offsets=True,
        ),
        audio=RecognitionAudio(content=b"flac_data"),
    )


@patch("google.cloud.speech.SpeechClient")
def test_transcribe_with_specified_api_parameters(SpeechClient):
    client = SpeechClient.return_value
    client.recognize.return_value = RecognizeResponse(
        results=[
            SpeechRecognitionResult(
                alternatives=[
                    SpeechRecognitionAlternative(
                        transcript="こんにちは", confidence=0.99
                    )
                ]
            )
        ]
    )

    audio_data = MagicMock(spec=AudioData)
    audio_data.sample_rate = 16_000
    audio_data.get_flac_data.return_value = b"flac_data"

    _ = recognize(
        MagicMock(spec=Recognizer),
        audio_data,
        language_code="ja-JP",
        preferred_phrases=["numero", "hoge"],
        use_enhanced=True,
    )

    client.recognize.assert_called_once_with(
        config=RecognitionConfig(
            encoding=RecognitionConfig.AudioEncoding.FLAC,
            sample_rate_hertz=16_000,
            language_code="ja-JP",
            speech_contexts=[SpeechContext(phrases=["numero", "hoge"])],
            use_enhanced=True,
        ),
        audio=RecognitionAudio(content=b"flac_data"),
    )
