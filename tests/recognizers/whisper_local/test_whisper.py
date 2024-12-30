import sys
from unittest import TestCase, skipIf
from unittest.mock import MagicMock, patch

from speech_recognition import AudioData, Recognizer
from speech_recognition.recognizers.whisper_local.whisper import recognize


@skipIf(sys.version_info >= (3, 13), "skip on Python 3.13")
@patch("speech_recognition.recognizers.whisper_local.base.io.BytesIO")
@patch("soundfile.read")
@patch("torch.cuda.is_available")
@patch("whisper.load_model")
class RecognizeWhisperTestCase(TestCase):
    def test_default_parameters(
        self, load_model, is_available, sf_read, BytesIO
    ):
        import numpy as np

        whisper_model = load_model.return_value
        transcript = whisper_model.transcribe.return_value
        audio_array = MagicMock()
        dummy_sampling_rate = 99_999
        sf_read.return_value = (audio_array, dummy_sampling_rate)

        audio_data = MagicMock(spec=AudioData)
        actual = recognize(MagicMock(spec=Recognizer), audio_data)

        self.assertEqual(actual, transcript.__getitem__.return_value)
        load_model.assert_called_once_with("base")
        audio_data.get_wav_data.assert_called_once_with(convert_rate=16000)
        BytesIO.assert_called_once_with(audio_data.get_wav_data.return_value)
        sf_read.assert_called_once_with(BytesIO.return_value)
        audio_array.astype.assert_called_once_with(np.float32)
        whisper_model.transcribe.assert_called_once_with(
            audio_array.astype.return_value,
            fp16=is_available.return_value,
        )
        transcript.__getitem__.assert_called_once_with("text")

    def test_return_as_dict(self, load_model, is_available, sf_read, BytesIO):
        whisper_model = load_model.return_value
        audio_array = MagicMock()
        dummy_sampling_rate = 99_999
        sf_read.return_value = (audio_array, dummy_sampling_rate)

        audio_data = MagicMock(spec=AudioData)
        actual = recognize(
            MagicMock(spec=Recognizer), audio_data, show_dict=True
        )

        self.assertEqual(actual, whisper_model.transcribe.return_value)

    def test_pass_parameters(self, load_model, is_available, sf_read, BytesIO):
        whisper_model = load_model.return_value
        transcript = whisper_model.transcribe.return_value
        audio_array = MagicMock()
        dummy_sampling_rate = 99_999
        sf_read.return_value = (audio_array, dummy_sampling_rate)

        audio_data = MagicMock(spec=AudioData)
        actual = recognize(
            MagicMock(spec=Recognizer),
            audio_data,
            model="small",
            language="english",
            task="translate",
            temperature=0,
        )

        self.assertEqual(actual, transcript.__getitem__.return_value)
        load_model.assert_called_once_with("small")
        whisper_model.transcribe.assert_called_once_with(
            audio_array.astype.return_value,
            fp16=is_available.return_value,
            language="english",
            task="translate",
            temperature=0,
        )
