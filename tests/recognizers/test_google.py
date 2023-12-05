from unittest import TestCase
from unittest.mock import MagicMock, patch
from urllib.request import Request

from speech_recognition.audio import AudioData
from speech_recognition.recognizers import google

MODULE_UNDER_TEST = "speech_recognition.recognizers.google"


class RequestBuilderTestCase(TestCase):
    CLASS_UNDER_TEST = f"{MODULE_UNDER_TEST}.RequestBuilder"

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


class OutputParserTestCase(TestCase):
    CLASS_UNDER_TEST = f"{MODULE_UNDER_TEST}.OutputParser"

    @patch(f"{CLASS_UNDER_TEST}.convert_to_result")
    def test_parse_show_all(self, convert_to_result):
        parser = google.OutputParser(show_all=True, with_confidence=False)

        actual = parser.parse("dummy response text")

        self.assertEqual(actual, convert_to_result.return_value)
        convert_to_result.assert_called_once_with("dummy response text")

    @patch(f"{CLASS_UNDER_TEST}.find_best_hypothesis")
    @patch(f"{CLASS_UNDER_TEST}.convert_to_result")
    def test_parse_without_confidence(
        self, convert_to_result, find_best_hypothesis
    ):
        convert_to_result.return_value = {"alternative": "dummy"}
        find_best_hypothesis.return_value = {
            "transcript": "1 2",
            "confidence": 0.49585345,
        }

        parser = google.OutputParser(show_all=False, with_confidence=False)
        actual = parser.parse("dummy response text2")

        self.assertEqual(actual, "1 2")
        convert_to_result.assert_called_once_with("dummy response text2")
        find_best_hypothesis.assert_called_once_with("dummy")

    @patch(f"{CLASS_UNDER_TEST}.find_best_hypothesis")
    @patch(f"{CLASS_UNDER_TEST}.convert_to_result")
    def test_parse_without_confidence(
        self, convert_to_result, find_best_hypothesis
    ):
        convert_to_result.return_value = {"alternative": "dummy3"}
        find_best_hypothesis.return_value = {
            "transcript": "1 2",
            "confidence": 0.49585345,
        }

        parser = google.OutputParser(show_all=False, with_confidence=True)
        actual = parser.parse("dummy response text3")

        self.assertEqual(actual, ("1 2", 0.49585345))
        find_best_hypothesis.assert_called_once_with("dummy3")


class ObtainTranscriptionTestCase(TestCase):
    @patch(f"{MODULE_UNDER_TEST}.urlopen")
    def test_obtain(self, urlopen):
        request = MagicMock(spec=Request)
        response = urlopen.return_value

        actual = google.obtain_transcription(request, 0)

        self.assertEqual(
            actual, response.read.return_value.decode.return_value
        )
        urlopen.assert_called_once_with(request, timeout=0)
        response.read.assert_called_once_with()
        response.read.return_value.decode.assert_called_once_with("utf-8")
