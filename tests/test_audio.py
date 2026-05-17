#!/usr/bin/env python3

import sys
import unittest
from os import path
from unittest import mock

import speech_recognition as sr
from speech_recognition.exceptions import SetupError


class TestAudioFile(unittest.TestCase):
    def assertSimilar(self, bytes_1, bytes_2):
        for i, (byte_1, byte_2) in enumerate(zip(bytes_1, bytes_2)):
            if abs(byte_1 - byte_2) > 2:
                raise AssertionError("{} is really different from {} at index {}".format(bytes_1, bytes_2, i))

    def test_get_segment(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-mono-32-bit-44100Hz.wav"))
        self.assertEqual(audio.get_raw_data(), audio.get_segment().get_raw_data())
        self.assertEqual(audio.get_raw_data()[8:], audio.get_segment(0.022675738 * 2).get_raw_data())
        self.assertEqual(audio.get_raw_data()[:16], audio.get_segment(None, 0.022675738 * 4).get_raw_data())
        self.assertEqual(audio.get_raw_data()[8:16], audio.get_segment(0.022675738 * 2, 0.022675738 * 4).get_raw_data())

    def test_wav_mono_8_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-mono-8-bit-44100Hz.wav"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        self.assertEqual(audio.sample_width, 1)
        self.assertSimilar(audio.get_raw_data()[:32], b"\x00\xff\x00\xff\x00\xff\xff\x00\xff\x00\xff\x00\xff\x00\x00\xff\x00\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\x00\xff\xff")

    def test_wav_mono_16_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-mono-16-bit-44100Hz.wav"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        self.assertEqual(audio.sample_width, 2)
        self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\xff\xff\x01\x00\xff\xff\x00\x00\x01\x00\xfe\xff\x01\x00\xfe\xff\x04\x00\xfc\xff\x04\x00\xfe\xff\xff\xff\x03\x00\xfe\xff")

    def test_wav_mono_24_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-mono-24-bit-44100Hz.wav"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        if audio.sample_width == 3:
            self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\x00\xff\xff\x00\x01\x00\x00\xff\xff\x00\x00\x00\x00\x01\x00\x00\xfe\xff\x00\x01\x00\x00\xfe\xff\x00\x04\x00\x00\xfb")
        else:
            self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x01\x00\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xfe\xff\x00\x00\x01\x00")

    def test_wav_mono_32_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-mono-32-bit-44100Hz.wav"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        self.assertEqual(audio.sample_width, 4)
        self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x01\x00\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xfe\xff\x00\x00\x01\x00")

    def test_wav_stereo_8_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-stereo-8-bit-44100Hz.wav"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        self.assertEqual(audio.sample_width, 1)
        self.assertSimilar(audio.get_raw_data()[:32], b"\x00\xff\x00\xff\x00\x00\xff\x7f\x7f\x00\xff\x00\xff\x00\x00\xff\x00\x7f\x7f\x7f\x00\x00\xff\x00\xff\x00\xff\x00\x7f\x7f\x7f\x7f")

    def test_wav_stereo_16_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-stereo-16-bit-44100Hz.wav"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        self.assertEqual(audio.sample_width, 2)
        self.assertSimilar(audio.get_raw_data()[:32], b"\x02\x00\xfb\xff\x04\x00\xfe\xff\xfe\xff\x07\x00\xf6\xff\x07\x00\xf9\xff\t\x00\xf5\xff\x0c\x00\xf8\xff\x02\x00\x04\x00\xfa\xff")

    def test_wav_stereo_24_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-stereo-24-bit-44100Hz.wav"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        if audio.sample_width == 3:
            self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\x00\xfe\xff\x00\x02\x00\x00\xfe\xff\x00\x00\x00\x00\x02\x00\x00\xfc\xff\x00\x02\x00\x00\xfc\xff\x00\x08\x00\x00\xf6")
        else:
            self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\x00\x00\x00\xfe\xff\x00\x00\x02\x00\x00\x00\xfe\xff\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\xfc\xff\x00\x00\x02\x00")

    def test_wav_stereo_32_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-stereo-32-bit-44100Hz.wav"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        self.assertEqual(audio.sample_width, 4)
        self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\x00\x00\x00\xfe\xff\x00\x00\x02\x00\x00\x00\xfe\xff\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\xfc\xff\x00\x00\x02\x00")

    def test_aiff_mono_16_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-mono-16-bit-44100Hz.aiff"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        self.assertEqual(audio.sample_width, 2)
        self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\x00\xff\xff\x01\x00\xff\xff\x01\x00\xfe\xff\x02\x00\xfd\xff\x04\x00\xfc\xff\x03\x00\x00\x00\xfe\xff\x03\x00\xfd\xff")

    def test_aiff_stereo_16_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-stereo-16-bit-44100Hz.aiff"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        self.assertEqual(audio.sample_width, 2)
        self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\xfe\xff\x02\x00\xfe\xff\xff\xff\x04\x00\xfa\xff\x04\x00\xfa\xff\t\x00\xf6\xff\n\x00\xfa\xff\xff\xff\x08\x00\xf5\xff")

    def test_flac_mono_16_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-mono-16-bit-44100Hz.flac"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        self.assertEqual(audio.sample_width, 2)
        self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\xff\xff\x01\x00\xff\xff\x00\x00\x01\x00\xfe\xff\x02\x00\xfc\xff\x06\x00\xf9\xff\x06\x00\xfe\xff\xfe\xff\x05\x00\xfa\xff")

    def test_flac_mono_24_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-mono-24-bit-44100Hz.flac"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        if audio.sample_width == 3:
            self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\xff\xfe\xff\x02\x01\x00\xfd\xfe\xff\x04\x00\x00\xfc\x00\x00\x04\xfe\xff\xfb\x00\x00\x05\xfe\xff\xfc\x03\x00\x04\xfb")
        else:
            self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\x00\x00\xff\xfe\xff\x00\x02\x01\x00\x00\xfd\xfe\xff\x00\x04\x00\x00\x00\xfc\x00\x00\x00\x04\xfe\xff\x00\xfb\x00\x00")

    def test_flac_stereo_16_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-stereo-16-bit-44100Hz.flac"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        self.assertEqual(audio.sample_width, 2)
        self.assertSimilar(audio.get_raw_data()[:32], b"\xff\xff\xff\xff\x02\x00\xfe\xff\x00\x00\x01\x00\xfd\xff\x01\x00\xff\xff\x04\x00\xfa\xff\x05\x00\xff\xff\xfd\xff\x08\x00\xf6\xff")

    def test_flac_stereo_24_bit(self):
        audio = sr.AudioData.from_file(path.join(path.dirname(path.realpath(__file__)), "audio-stereo-24-bit-44100Hz.flac"))
        self.assertIsInstance(audio, sr.AudioData)
        self.assertEqual(audio.sample_rate, 44100)
        if audio.sample_width == 3:
            self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\x00\xfe\xff\x00\x02\x00\x00\xfe\xff\x00\x00\x00\xff\x01\x00\x02\xfc\xff\xfe\x01\x00\x02\xfc\xff\xfe\x07\x00\x01\xf6")
        else:
            self.assertSimilar(audio.get_raw_data()[:32], b"\x00\x00\x00\x00\x00\x00\xfe\xff\x00\x00\x02\x00\x00\x00\xfe\xff\x00\x00\x00\x00\x00\xff\x01\x00\x00\x02\xfc\xff\x00\xfe\x01\x00")


class TestAudioDataSplit(unittest.TestCase):
    def test_returns_self_when_already_fits(self):
        audio = sr.AudioData(b"\x00\x01" * 100, sample_rate=16000, sample_width=2)
        result = audio.split(max_bytes=10_000)
        self.assertEqual(len(result), 1)
        self.assertIs(result[0], audio)

    def test_raises_when_max_bytes_too_small(self):
        audio = sr.AudioData(b"\x00\x01" * 100, sample_rate=16000, sample_width=2)
        with self.assertRaises(ValueError):
            audio.split(max_bytes=44)

    def test_raises_on_unaligned_frame_data(self):
        # split() requires sample-aligned frame_data so it can enforce the
        # ``max_bytes`` cap; AudioData itself accepts unaligned input.
        unaligned = b"\x00\x01" * 100 + b"\x02"  # 201 bytes, sw=2 → unaligned
        audio = sr.AudioData(unaligned, sample_rate=16000, sample_width=2)
        with self.assertRaises(ValueError):
            audio.split(max_bytes=2_048)
        with self.assertRaises(ValueError):
            audio.split(max_bytes=2_048, silence_aware=True)

    def test_raises_when_max_bytes_below_one_sample_per_width(self):
        # Regression: previously only checked > WAV header (44 bytes), so
        # max_bytes=45 with sample_width=2 silently produced empty chunks
        # when asserts were stripped (python -O).
        for sample_width in (1, 2, 3, 4):
            payload = b"\x00" * (sample_width * 100)
            audio = sr.AudioData(
                payload, sample_rate=16000, sample_width=sample_width
            )
            min_required = sr.AudioData._WAV_HEADER_OVERHEAD + sample_width
            with self.assertRaises(ValueError):
                audio.split(max_bytes=min_required - 1)
            with self.assertRaises(ValueError):
                audio.split(
                    max_bytes=min_required - 1, silence_aware=True
                )
            # boundary: exact minimum must NOT raise; should produce chunks
            chunks = audio.split(max_bytes=min_required)
            self.assertGreater(len(chunks), 0)

    def test_fixed_split_chunks_fit_within_max_bytes(self):
        payload = b"\x00\x01" * 5_000
        audio = sr.AudioData(payload, sample_rate=16000, sample_width=2)
        max_bytes = 2_048
        chunks = audio.split(max_bytes=max_bytes)

        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk.get_wav_data()), max_bytes)

        joined = b"".join(c.frame_data for c in chunks)
        self.assertEqual(joined, payload)

        for chunk in chunks:
            self.assertEqual(chunk.sample_rate, 16000)
            self.assertEqual(chunk.sample_width, 2)

    def test_fixed_split_aligns_to_sample_boundary(self):
        payload = b"\x00\x00\x01\x00\x02\x00\x03\x00" * 1_000
        audio = sr.AudioData(payload, sample_rate=8000, sample_width=2)
        chunks = audio.split(max_bytes=200)
        for chunk in chunks:
            self.assertEqual(len(chunk.frame_data) % 2, 0)

    def test_silence_aware_raises_setup_error_without_librosa(self):
        # Pre-load numpy so mock.patch.dict's exit-time restore does not
        # remove a freshly-imported numpy entry; numpy 2.x refuses to
        # re-initialize once unloaded mid-process.
        try:
            import numpy  # noqa: F401
        except ImportError:
            pass

        payload = b"\x00\x01" * 5_000
        audio = sr.AudioData(payload, sample_rate=16000, sample_width=2)
        with mock.patch.dict(
            sys.modules,
            {"librosa": None, "librosa.effects": None},
        ):
            with self.assertRaises(SetupError):
                audio.split(max_bytes=2_048, silence_aware=True)

    def test_silence_aware_translates_call_time_errors_to_setup_error(self):
        # Regression: even after the dependency import succeeds, librosa's
        # numba-backed implementation can raise mid-call (e.g. cache
        # creation failures in read-only environments). Those must also
        # surface as SetupError, not as a raw RuntimeError, so users get a
        # single actionable failure mode.
        try:
            import numpy  # noqa: F401
            import librosa.effects  # noqa: F401
        except ImportError:
            self.skipTest("librosa not installed; cannot exercise call-time error path")

        payload = b"\x00\x01" * 5_000
        audio = sr.AudioData(payload, sample_rate=16000, sample_width=2)

        def _boom(*args, **kwargs):
            raise RuntimeError("simulated numba JIT failure")

        with mock.patch("librosa.effects.split", side_effect=_boom):
            with self.assertRaises(SetupError):
                audio.split(max_bytes=2_048, silence_aware=True)

    def test_silence_aware_translates_lazy_runtime_errors_to_setup_error(self):
        # Regression: previously librosa.effects.split was looked up lazily
        # at call time, so numba/librosa lazy-import RuntimeErrors escaped
        # the SetupError guard. Now the dependency is force-loaded inside
        # the guard, so any initialization-time error becomes SetupError.
        try:
            import numpy  # noqa: F401
        except ImportError:
            pass

        payload = b"\x00\x01" * 5_000
        audio = sr.AudioData(payload, sample_rate=16000, sample_width=2)

        import types

        class _RaisingEffects(types.ModuleType):
            def __getattr__(self, name):
                raise RuntimeError("simulated lazy load failure")

        fake_librosa = types.ModuleType("librosa")
        fake_effects = _RaisingEffects("librosa.effects")
        fake_librosa.effects = fake_effects
        with mock.patch.dict(
            sys.modules,
            {"librosa": fake_librosa, "librosa.effects": fake_effects},
        ):
            with self.assertRaises(SetupError):
                audio.split(max_bytes=2_048, silence_aware=True)


class TestAudioDataSplitSilenceAware(unittest.TestCase):
    def setUp(self):
        # Probe the exact callable used at runtime so this also skips when
        # librosa is installed but its numba-backed initialization fails
        # (e.g., read-only cache directory).
        try:
            import numpy  # noqa: F401
            from librosa.effects import split as _librosa_split  # noqa: F401
        except Exception as exc:
            raise unittest.SkipTest(
                "silence-aware split tests require a functional librosa "
                f"and numpy: {exc}"
            )

    def test_to_float_ndarray_normalizes_each_sample_width(self):
        import numpy as np

        # Build payloads as explicit little-endian bytes so the assertions
        # are independent of host byte order (WAV PCM is little-endian).
        cases = {
            1: bytes([0, 128, 255, 64]),  # WAV unsigned 8-bit
            2: b"".join(
                int(v).to_bytes(2, "little", signed=True)
                for v in (0, 32767, -32768, 100)
            ),
            4: b"".join(
                int(v).to_bytes(4, "little", signed=True)
                for v in (0, (1 << 31) - 1, -(1 << 31), 1000)
            ),
        }
        for sw, payload in cases.items():
            audio = sr.AudioData(payload, sample_rate=16000, sample_width=sw)
            arr = audio._to_float_ndarray(np)
            self.assertEqual(arr.dtype, np.float32)
            self.assertTrue(np.all(np.abs(arr) <= 1.0 + 1e-6), f"sw={sw}")

    def test_to_float_ndarray_decodes_little_endian_regardless_of_host(self):
        import numpy as np

        # Hand-built little-endian byte sequences with known values; the
        # test fails on big-endian hosts if dtype lacks an explicit `<`.
        payload_16 = b"\x01\x00" + b"\xff\xff"  # +1, -1
        audio16 = sr.AudioData(payload_16, sample_rate=16000, sample_width=2)
        arr16 = audio16._to_float_ndarray(np)
        self.assertAlmostEqual(float(arr16[0]), 1 / 32768.0, places=6)
        self.assertAlmostEqual(float(arr16[1]), -1 / 32768.0, places=6)

        payload_32 = b"\x01\x00\x00\x00" + b"\xff\xff\xff\xff"  # +1, -1
        audio32 = sr.AudioData(payload_32, sample_rate=16000, sample_width=4)
        arr32 = audio32._to_float_ndarray(np)
        self.assertAlmostEqual(float(arr32[0]), 1 / (1 << 31), places=10)
        self.assertAlmostEqual(float(arr32[1]), -1 / (1 << 31), places=10)

    def test_to_float_ndarray_24bit_sign_extension(self):
        import numpy as np

        positive = (0x123456).to_bytes(3, "little", signed=False)
        negative = (-0x123456).to_bytes(3, "little", signed=True)
        zero = b"\x00\x00\x00"
        payload = positive + negative + zero
        audio = sr.AudioData(payload, sample_rate=16000, sample_width=3)
        arr = audio._to_float_ndarray(np)
        self.assertEqual(arr.shape, (3,))
        self.assertGreater(arr[0], 0)
        self.assertLess(arr[1], 0)
        self.assertEqual(arr[2], 0.0)
        self.assertTrue(np.all(np.abs(arr) <= 1.0 + 1e-6))

    def test_silence_aware_uses_single_nonsilent_range_boundary(self):
        import numpy as np

        sample_rate = 16000
        silence = np.zeros(int(sample_rate * 1.5))
        tone = (
            np.sin(2 * np.pi * 440 * np.arange(int(sample_rate * 3)) / sample_rate)
            * 0.5
        )
        more_silence = np.zeros(int(sample_rate * 1.0))
        combined = np.concatenate([silence, tone, more_silence, tone])
        pcm = (combined * 32767).astype(np.int16).tobytes()
        audio = sr.AudioData(pcm, sample_rate=sample_rate, sample_width=2)

        target_seconds = 2.5
        max_bytes = (
            int(target_seconds * sample_rate * 2) + sr.AudioData._WAV_HEADER_OVERHEAD
        )
        chunks = audio.split(max_bytes=max_bytes, silence_aware=True)

        self.assertGreater(len(chunks), 1)
        # First chunk boundary must land on a silence sample (not mid-tone).
        # The first silence ends near sample 24000 (1.5s); the cut should fall
        # at or before that, so the last sample of chunk[0] is silence (≈0).
        first_chunk_samples = np.frombuffer(
            chunks[0].frame_data, dtype=np.int16
        )
        self.assertLess(abs(int(first_chunk_samples[-1])), 1000)

        joined = b"".join(c.frame_data for c in chunks)
        self.assertEqual(joined, pcm)

    def test_silence_aware_respects_byte_budget_strictly(self):
        # Regression: max_bytes must be a hard ceiling for silence-aware
        # mode, not a soft target. The search window is now constrained to
        # the look-back side of the target, so chunks cannot exceed the cap.
        import numpy as np

        sample_rate = 16000
        sample_width = 2
        silence = np.zeros(int(sample_rate * 5))
        pcm = silence.astype(np.int16).tobytes()
        audio = sr.AudioData(
            pcm, sample_rate=sample_rate, sample_width=sample_width
        )

        max_bytes = 200
        chunks = audio.split(max_bytes=max_bytes, silence_aware=True)

        for chunk in chunks:
            self.assertLessEqual(len(chunk.get_wav_data()), max_bytes)

        joined = b"".join(c.frame_data for c in chunks)
        self.assertEqual(joined, pcm)

    def test_silence_aware_respects_byte_budget_on_realistic_audio(self):
        # Same strict-cap invariant against audio that contains both
        # speech-like and silence segments so the boundary search exercises
        # the librosa path.
        import numpy as np

        sample_rate = 16000
        sample_width = 2
        tone_a = (
            np.sin(2 * np.pi * 440 * np.arange(int(sample_rate * 2.0)) / sample_rate)
            * 0.5
        )
        silence = np.zeros(int(sample_rate * 1.5))
        tone_b = (
            np.sin(2 * np.pi * 440 * np.arange(int(sample_rate * 2.0)) / sample_rate)
            * 0.5
        )
        combined = np.concatenate([tone_a, silence, tone_b])
        pcm = (combined * 32767).astype(np.int16).tobytes()
        audio = sr.AudioData(pcm, sample_rate=sample_rate, sample_width=2)

        target_seconds = 2.5
        max_bytes = (
            int(target_seconds * sample_rate * 2)
            + sr.AudioData._WAV_HEADER_OVERHEAD
        )
        chunks = audio.split(max_bytes=max_bytes, silence_aware=True)
        for chunk in chunks:
            self.assertLessEqual(len(chunk.get_wav_data()), max_bytes)

    def test_silence_aware_snaps_to_speech_end_within_lookback(self):
        # Regression: the boundary search must consider the end of a
        # nonsilent range (speech-to-silence transition), not just the
        # start. When the most recent speech ends shortly before the
        # target, the cleanest cut is at that speech end (which is also
        # the start of trailing silence) — strictly before the target so
        # the chunk stays within the byte budget.
        import numpy as np

        sample_rate = 16000
        # 2.0s tone, then 1.5s silence, then 2.0s tone. Target ~2.5s, so the
        # target falls inside the silence right after the first tone ends.
        tone_a = (
            np.sin(2 * np.pi * 440 * np.arange(int(sample_rate * 2.0)) / sample_rate)
            * 0.5
        )
        silence = np.zeros(int(sample_rate * 1.5))
        tone_b = (
            np.sin(2 * np.pi * 440 * np.arange(int(sample_rate * 2.0)) / sample_rate)
            * 0.5
        )
        combined = np.concatenate([tone_a, silence, tone_b])
        pcm = (combined * 32767).astype(np.int16).tobytes()
        audio = sr.AudioData(pcm, sample_rate=sample_rate, sample_width=2)

        target_seconds = 2.5
        max_bytes = (
            int(target_seconds * sample_rate * 2) + sr.AudioData._WAV_HEADER_OVERHEAD
        )
        chunks = audio.split(max_bytes=max_bytes, silence_aware=True)

        self.assertGreater(len(chunks), 1)
        # The first chunk should end inside the silence region (sample range
        # ~32000-56000), not mid-speech in tone_b.
        first_chunk_end_sample = len(chunks[0].frame_data) // 2
        self.assertGreaterEqual(first_chunk_end_sample, int(sample_rate * 2.0) - 200)
        self.assertLessEqual(first_chunk_end_sample, int(sample_rate * 3.5) + 200)

        joined = b"".join(c.frame_data for c in chunks)
        self.assertEqual(joined, pcm)


    def test_silence_aware_splits_at_silence_boundary(self):
        import numpy as np

        sample_rate = 16000
        tone = (
            np.sin(2 * np.pi * 440 * np.arange(int(sample_rate * 2)) / sample_rate)
            * 0.5
        )
        silence = np.zeros(int(sample_rate * 1.5))
        combined = np.concatenate([tone, silence, tone, silence, tone])
        pcm = (combined * 32767).astype(np.int16).tobytes()
        audio = sr.AudioData(pcm, sample_rate=sample_rate, sample_width=2)

        target_seconds = 2.5
        max_bytes = (
            int(target_seconds * sample_rate * 2) + sr.AudioData._WAV_HEADER_OVERHEAD
        )
        chunks = audio.split(max_bytes=max_bytes, silence_aware=True)

        self.assertGreater(len(chunks), 1)
        joined = b"".join(c.frame_data for c in chunks)
        self.assertEqual(joined, pcm)


if __name__ == "__main__":
    unittest.main()
