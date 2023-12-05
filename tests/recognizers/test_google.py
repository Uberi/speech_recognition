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

    @patch(f"{CLASS_UNDER_TEST}.to_convert_rate")
    def test_build_data(self, to_convert_rate):
        # mock has AudioData's attributes (e.g. sample_rate)
        audio_data = MagicMock(spec=AudioData(None, 1, 1))
        sut = google.RequestBuilder(key="", language="", filter_level=0)

        actual = sut.build_data(audio_data)

        self.assertEqual(actual, audio_data.get_flac_data.return_value)
        audio_data.get_flac_data.assert_called_once_with(
            convert_rate=to_convert_rate.return_value, convert_width=2
        )
        to_convert_rate.assert_called_once_with(audio_data.sample_rate)
