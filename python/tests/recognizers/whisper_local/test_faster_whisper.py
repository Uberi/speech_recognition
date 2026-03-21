from __future__ import annotations

import sys
from collections.abc import Generator
from typing import TYPE_CHECKING
from unittest.mock import ANY, MagicMock, patch

import numpy as np
import pytest

from speech_recognition import Recognizer
from speech_recognition.audio import AudioData
from speech_recognition.recognizers.whisper_local.faster_whisper import (
    recognize,
)

if TYPE_CHECKING:
    from faster_whisper.transcribe import Segment, TranscriptionInfo


@pytest.fixture
def audio_data() -> AudioData:
    audio = MagicMock(spec=AudioData)
    audio.get_wav_data.return_value = b""
    return audio


@pytest.fixture
def segment() -> Segment:
    from faster_whisper.transcribe import Segment

    mocked_segment = MagicMock(spec=Segment(*[None] * 11))
    mocked_segment.text = ""
    return mocked_segment


@pytest.fixture
def transcription_info() -> TranscriptionInfo:
    from faster_whisper.transcribe import TranscriptionInfo

    return MagicMock(spec=TranscriptionInfo(*[None] * 7))


@pytest.fixture
def soundfile_read() -> Generator[tuple[MagicMock, np.ndarray], None, None]:
    audio_array = MagicMock(spec=np.ndarray)
    dummy_sampling_rate = 99_999

    with patch("soundfile.read") as mock_read:
        mock_read.return_value = (audio_array, dummy_sampling_rate)
        yield mock_read, audio_array


@pytest.mark.skipif(
    sys.version_info >= (3, 13), reason="skip on Python 3.13 or later"
)
@patch("faster_whisper.WhisperModel")
class TestTranscribe:
    def test_default_parameters(
        self, WhisperModel, audio_data, soundfile_read
    ):
        from faster_whisper.transcribe import (
            Segment,
            TranscriptionInfo,
            TranscriptionOptions,
            VadOptions,
        )

        sf_read, audio_array = soundfile_read

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
            all_language_probs=[("en", 0.9314374923706055)],  # Omitted
            transcription_options=MagicMock(spec=TranscriptionOptions),
            vad_options=MagicMock(spec=VadOptions),
        )

        whisper_model = WhisperModel.return_value
        whisper_model.transcribe.return_value = segments(), info

        audio_data.get_wav_data.return_value = b"audio data"
        actual = recognize(MagicMock(spec=Recognizer), audio_data)

        assert actual == " 1, 2, 3"
        WhisperModel.assert_called_once_with("base")
        audio_data.get_wav_data.assert_called_once_with(convert_rate=16_000)
        sf_read.assert_called_once_with(ANY)
        assert sf_read.call_args[0][0].read() == b"audio data"
        audio_array.astype.assert_called_once_with(np.float32)
        whisper_model.transcribe.assert_called_once_with(
            audio_array.astype.return_value
        )

    def test_show_dict(self, WhisperModel, audio_data, soundfile_read):
        from faster_whisper.transcribe import (
            Segment,
            TranscriptionInfo,
            TranscriptionOptions,
            VadOptions,
        )

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
            all_language_probs=[("en", 0.9314374923706055)],  # Omitted
            transcription_options=MagicMock(spec=TranscriptionOptions),
            vad_options=MagicMock(spec=VadOptions),
        )

        whisper_model = WhisperModel.return_value
        whisper_model.transcribe.return_value = segments(), info

        actual = recognize(
            MagicMock(spec=Recognizer), audio_data, show_dict=True
        )

        expected = {
            "text": " 1, 2, 3",
            "language": "en",
            "segments": [
                Segment(
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
            ],
        }
        assert actual == expected

    def test_pass_parameters(
        self,
        WhisperModel,
        audio_data,
        segment,
        transcription_info,
        soundfile_read,
    ):
        _, audio_array = soundfile_read

        def segments_generator():
            yield segment

        whisper_model = WhisperModel.return_value
        whisper_model.transcribe.return_value = (
            segments_generator(),
            transcription_info,
        )

        _ = recognize(
            MagicMock(spec=Recognizer),
            audio_data,
            model="small",
            show_dict=True,
            language="fr",
            task="translate",
            beam_size=5,
        )

        WhisperModel.assert_called_once_with("small")
        whisper_model.transcribe.assert_called_once_with(
            audio_array.astype.return_value,
            language="fr",
            task="translate",
            beam_size=5,
        )

    def test_init_parameters(
        self,
        WhisperModel,
        audio_data,
        segment,
        transcription_info,
        soundfile_read,
    ):
        def segments_generator():
            yield segment

        whisper_model = WhisperModel.return_value
        whisper_model.transcribe.return_value = (
            segments_generator(),
            transcription_info,
        )

        _ = recognize(
            MagicMock(spec=Recognizer),
            audio_data,
            init_options={"compute_type": "int8"},
        )

        WhisperModel.assert_called_once_with("base", compute_type="int8")
