import sys
from unittest import TestCase, skipIf
from unittest.mock import ANY, MagicMock, patch

import numpy as np

from speech_recognition import AudioData, Recognizer
from speech_recognition.recognizers.whisper_local.whisper import recognize


@skipIf(sys.version_info >= (3, 13), "skip on Python 3.13")
@patch("soundfile.read")
@patch("torch.cuda.is_available")
@patch("whisper.load_model")
class RecognizeWhisperTestCase(TestCase):
    def test_default_parameters(self, load_model, is_available, sf_read):
        whisper_model = load_model.return_value
        whisper_model.transcribe.return_value = {
            "text": "Transcription by Whisper model",
            "language": "en",
            # Omit "segments"
        }
        audio_array = MagicMock(spec=np.ndarray)
        dummy_sampling_rate = 99_999
        sf_read.return_value = (audio_array, dummy_sampling_rate)

        audio_data = MagicMock(spec=AudioData)
        audio_data.get_wav_data.return_value = b"wav_data"
        actual = recognize(MagicMock(spec=Recognizer), audio_data)

        assert actual == "Transcription by Whisper model"
        load_model.assert_called_once_with("base")
        audio_data.get_wav_data.assert_called_once_with(convert_rate=16000)
        sf_read.assert_called_once_with(ANY)
        assert sf_read.call_args[0][0].read() == b"wav_data"
        audio_array.astype.assert_called_once_with(np.float32)
        whisper_model.transcribe.assert_called_once_with(
            audio_array.astype.return_value,
            fp16=is_available.return_value,
        )

    def test_return_as_dict(self, load_model, is_available, sf_read):
        whisper_model = load_model.return_value
        whisper_model.transcribe.return_value = {
            "text": " 1, 2, 3",
            "segments": [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 2.64,
                    "text": " 1, 2, 3",
                    "tokens": [50364, 502, 11, 568, 11, 805, 50496],
                    "temperature": 0.0,
                    "avg_logprob": -0.5379014015197754,
                    "compression_ratio": 0.4666666666666667,
                    "no_speech_prob": 0.17316073179244995,
                }
            ],
            "language": "en",
        }
        audio_array = MagicMock(spec=np.ndarray)
        dummy_sampling_rate = 99_999
        sf_read.return_value = (audio_array, dummy_sampling_rate)

        audio_data = MagicMock(spec=AudioData)
        audio_data.get_wav_data.return_value = b""
        actual = recognize(
            MagicMock(spec=Recognizer), audio_data, show_dict=True
        )

        expected = {
            "text": " 1, 2, 3",
            "segments": [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 2.64,
                    "text": " 1, 2, 3",
                    "tokens": [50364, 502, 11, 568, 11, 805, 50496],
                    "temperature": 0.0,
                    "avg_logprob": -0.5379014015197754,
                    "compression_ratio": 0.4666666666666667,
                    "no_speech_prob": 0.17316073179244995,
                }
            ],
            "language": "en",
        }

        assert actual == expected

    def test_pass_parameters(self, load_model, is_available, sf_read):
        whisper_model = load_model.return_value
        audio_array = MagicMock(spec=np.ndarray)
        dummy_sampling_rate = 99_999
        sf_read.return_value = (audio_array, dummy_sampling_rate)

        audio_data = MagicMock(spec=AudioData)
        audio_data.get_wav_data.return_value = b""
        _ = recognize(
            MagicMock(spec=Recognizer),
            audio_data,
            model="small",
            language="english",
            task="translate",
            temperature=0,
        )

        load_model.assert_called_once_with("small")
        whisper_model.transcribe.assert_called_once_with(
            audio_array.astype.return_value,
            fp16=is_available.return_value,
            language="english",
            task="translate",
            temperature=0,
        )
