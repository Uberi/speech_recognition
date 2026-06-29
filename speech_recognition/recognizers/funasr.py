from __future__ import annotations

from typing import TYPE_CHECKING

from speech_recognition.exceptions import SetupError

if TYPE_CHECKING:
    from speech_recognition.audio import AudioData

# Cache loaded models by (model, device) so repeated calls do not reload from disk.
_MODEL_CACHE: dict = {}

# Languages SenseVoice understands; anything else falls back to auto-detection.
_SENSEVOICE_LANGUAGES = {"auto", "zh", "en", "yue", "ja", "ko", "nospeech"}

SAMPLE_RATE = 16_000


def recognize(
    _recognizer,
    audio_data: "AudioData",
    model: str = "iic/SenseVoiceSmall",
    *,
    device: str = "cpu",
    language: str = "auto",
    use_itn: bool = True,
) -> str:
    """Perform speech recognition on ``audio_data`` using FunASR (runs locally, no API key).

    `FunASR <https://github.com/modelscope/FunASR>`__ is an open-source speech toolkit
    providing models such as SenseVoice (multilingual: Chinese, Cantonese, English,
    Japanese, Korean ...), Paraformer and Fun-ASR-Nano, with strong Chinese accuracy.

    ``model`` is a FunASR / ModelScope / Hugging Face model id
    (default ``"iic/SenseVoiceSmall"``). ``device`` is ``"cpu"`` or ``"cuda"``.
    ``language`` is the spoken language (``"auto"`` to auto-detect; SenseVoice supports
    ``zh`` / ``en`` / ``yue`` / ``ja`` / ``ko``). ``use_itn`` applies inverse text
    normalization (e.g. "nine" -> "9").

    The model is downloaded on first use and cached for subsequent calls.

    Requires `funasr` to be installed (``pip install funasr``).
    """
    try:
        from funasr import AutoModel
        from funasr.utils.postprocess_utils import rich_transcription_postprocess
    except ImportError:
        raise SetupError("missing funasr, please `pip install funasr`")

    import numpy as np

    cache_key = (model, device)
    if cache_key not in _MODEL_CACHE:
        _MODEL_CACHE[cache_key] = AutoModel(model=model, device=device, disable_update=True)
    funasr_model = _MODEL_CACHE[cache_key]

    spoken_language = language if language in _SENSEVOICE_LANGUAGES else "auto"
    raw_data = audio_data.get_raw_data(convert_rate=SAMPLE_RATE, convert_width=2)
    samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0

    result = funasr_model.generate(
        input=samples, cache={}, language=spoken_language, use_itn=use_itn
    )
    text = result[0]["text"] if result else ""
    return rich_transcription_postprocess(text).strip()
