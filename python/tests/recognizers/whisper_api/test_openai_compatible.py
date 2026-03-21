from unittest.mock import MagicMock

from speech_recognition import AudioData, Recognizer


def test_transcribe_with_openai_compatible_api(httpserver, monkeypatch):
    # https://github.com/Uberi/speech_recognition/issues/850
    httpserver.expect_request(
        "/v1/audio/transcriptions",
        method="POST",
    ).respond_with_json({"text": "Transcription by OpenAI compatible API"})

    monkeypatch.setenv("OPENAI_API_KEY", "EMPTY")
    monkeypatch.setenv("OPENAI_BASE_URL", httpserver.url_for("/v1"))

    audio_data = MagicMock(spec=AudioData)
    audio_data.get_wav_data.return_value = b"audio_data"

    sut = Recognizer()
    actual = sut.recognize_openai(audio_data)

    assert actual == "Transcription by OpenAI compatible API"
    audio_data.get_wav_data.assert_called_once_with()
