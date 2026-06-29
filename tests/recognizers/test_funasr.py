import sys
import types
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from speech_recognition import AudioData, Recognizer
from speech_recognition.exceptions import SetupError
from speech_recognition.recognizers import funasr


@pytest.fixture(autouse=True)
def clear_model_cache():
    funasr._MODEL_CACHE.clear()
    yield
    funasr._MODEL_CACHE.clear()


def install_fake_funasr(monkeypatch):
    model_instance = MagicMock()
    model_instance.generate.return_value = [{"text": "<|zh|><|NEUTRAL|> 你好世界 "}]

    funasr_module = types.ModuleType("funasr")
    funasr_module.AutoModel = MagicMock(return_value=model_instance)

    utils_module = types.ModuleType("funasr.utils")
    postprocess_module = types.ModuleType("funasr.utils.postprocess_utils")
    postprocess_module.rich_transcription_postprocess = MagicMock(return_value="你好世界")

    monkeypatch.setitem(sys.modules, "funasr", funasr_module)
    monkeypatch.setitem(sys.modules, "funasr.utils", utils_module)
    monkeypatch.setitem(sys.modules, "funasr.utils.postprocess_utils", postprocess_module)

    return funasr_module, postprocess_module, model_instance


def test_recognize_funasr_missing_dependency_raises_setup_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "funasr", None)

    audio_data = MagicMock(spec=AudioData)

    with pytest.raises(SetupError, match="missing funasr"):
        funasr.recognize(MagicMock(spec=Recognizer), audio_data)


def test_recognize_funasr_uses_cached_model_and_converts_audio(monkeypatch):
    funasr_module, postprocess_module, model_instance = install_fake_funasr(monkeypatch)
    raw_pcm = np.array([0, 32767, -32768], dtype=np.int16).tobytes()
    audio_data = MagicMock(spec=AudioData)
    audio_data.get_raw_data.return_value = raw_pcm

    first = funasr.recognize(
        MagicMock(spec=Recognizer),
        audio_data,
        model="iic/SenseVoiceSmall",
        device="cpu",
        language="zh",
        use_itn=False,
    )
    second = funasr.recognize(
        MagicMock(spec=Recognizer),
        audio_data,
        model="iic/SenseVoiceSmall",
        device="cpu",
        language="zh",
    )

    assert first == "你好世界"
    assert second == "你好世界"
    funasr_module.AutoModel.assert_called_once_with(
        model="iic/SenseVoiceSmall", device="cpu", disable_update=True
    )
    assert audio_data.get_raw_data.call_count == 2
    audio_data.get_raw_data.assert_called_with(convert_rate=16000, convert_width=2)
    assert model_instance.generate.call_count == 2
    first_call = model_instance.generate.call_args_list[0].kwargs
    np.testing.assert_allclose(first_call["input"], np.array([0.0, 32767 / 32768, -1.0], dtype=np.float32))
    assert first_call["cache"] == {}
    assert first_call["language"] == "zh"
    assert first_call["use_itn"] is False
    postprocess_module.rich_transcription_postprocess.assert_called_with("<|zh|><|NEUTRAL|> 你好世界 ")


def test_recognize_funasr_falls_back_to_auto_for_unknown_language(monkeypatch):
    _, _, model_instance = install_fake_funasr(monkeypatch)
    audio_data = MagicMock(spec=AudioData)
    audio_data.get_raw_data.return_value = np.array([0], dtype=np.int16).tobytes()

    funasr.recognize(MagicMock(spec=Recognizer), audio_data, language="fr")

    assert model_instance.generate.call_args.kwargs["language"] == "auto"


def test_recognizer_has_recognize_funasr_method():
    assert Recognizer.recognize_funasr is funasr.recognize
