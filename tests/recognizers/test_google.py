from unittest import TestCase
from unittest.mock import MagicMock, patch

from speech_recognition.audio import AudioData
from speech_recognition.recognizers import google

MODULE_UNDER_TEST = "speech_recognition.recognizers.google"
CLASS_UNDER_TEST = f"{MODULE_UNDER_TEST}.RequestBuilder"


class RequestBuilderTestCase(TestCase):
    @patch(f"{MODULE_UNDER_TEST}.Request")
    @patch(f"{CLASS_UNDER_TEST}.build_data")
    @patch(f"{CLASS_UNDER_TEST}.build_headers")
    @patch(f"{CLASS_UNDER_TEST}.build_url")
    def test_build(self, build_url, build_headers, build_data, Request):
        audio_data = MagicMock(spec=AudioData)
        sut = google.RequestBuilder(key="", language="", filter_level=0)

        actual = sut.build(audio_data)

        self.assertEqual(actual, Request.return_value)
        build_url.assert_called_once_with()
        build_headers.assert_called_once_with(audio_data)
        build_data.assert_called_once_with(audio_data)
        Request.assert_called_once_with(
            build_url.return_value,
            data=build_data.return_value,
            headers=build_headers.return_value,
        )
