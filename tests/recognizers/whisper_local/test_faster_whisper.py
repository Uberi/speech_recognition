import sys
from unittest.mock import ANY, MagicMock, patch

import numpy as np
import pytest
from faster_whisper.transcribe import (
    Segment,
    TranscriptionInfo,
    TranscriptionOptions,
    VadOptions,
)

from speech_recognition import Recognizer
from speech_recognition.audio import AudioData
from speech_recognition.recognizers.whisper_local.faster_whisper import (
    recognize,
)


@pytest.mark.skipif(
    sys.version_info >= (3, 13), reason="skip on Python 3.13 or later"
)
@patch("soundfile.read")
@patch("faster_whisper.WhisperModel")
class TestTranscribe:
    @patch("torch.cuda.is_available", return_value=False)
    def test_default_parameters(self, is_available, WhisperModel, sf_read):
        def segments():
            yield Segment(
                id=1,
                seek=0,
                start=0.0,
                end=2.64,
                text=" 1, 2, 3",
                tokens=[50364, 502, 11, 568, 11, 805, 50496],
                avg_logprob=-0.5378808751702309,
                compression_ratio=0.4666666666666667,
                no_speech_prob=0.17316274344921112,
                words=None,
                temperature=0.0,
            )

        info = TranscriptionInfo(
            language="en",
            language_probability=0.9314374923706055,
            duration=2.7449375,
            duration_after_vad=2.7449375,
            all_language_probs=[("en", 0.9314374923706055)],
            transcription_options=MagicMock(spec=TranscriptionOptions),
            vad_options=MagicMock(spec=VadOptions),
        )

        whisper_model = WhisperModel.return_value
        whisper_model.transcribe.return_value = segments(), info

        audio_data = MagicMock(spec=AudioData)
        audio_data.get_wav_data.return_value = b"audio data"

        audio_array = MagicMock(spec=np.ndarray)
        dummy_sampling_rate = 99_999
        sf_read.return_value = (audio_array, dummy_sampling_rate)

        actual = recognize(MagicMock(spec=Recognizer), audio_data)

        assert actual == " 1, 2, 3"
        is_available.assert_called_once_with()
        WhisperModel.assert_called_once_with("base", device="cpu")
        audio_data.get_wav_data.assert_called_once_with(convert_rate=16_000)
        sf_read.assert_called_once_with(ANY)
        assert sf_read.call_args[0][0].read() == b"audio data"
        audio_array.astype.assert_called_once_with(np.float32)
        whisper_model.transcribe.assert_called_once_with(
            audio_array.astype.return_value
        )
