import io
import unittest
import wave

import speech_recognition as sr


class TestRecord(unittest.TestCase):
    def make_source(self, sample_rate=8000, sample_width=2, frame_count=64037):
        frames = b"".join(
            (i % 128).to_bytes(sample_width, "little")
            for i in range(frame_count)
        )
        wav_data = io.BytesIO()
        with wave.open(wav_data, "wb") as audio_file:
            audio_file.setnchannels(1)
            audio_file.setsampwidth(sample_width)
            audio_file.setframerate(sample_rate)
            audio_file.writeframes(frames)
        wav_data.seek(0)
        return sr.AudioFile(wav_data), frames

    def test_record_exact_offset_and_duration(self):
        # Neither the five-second offset nor the two-second duration is a
        # multiple of AudioFile.CHUNK (4096 frames) at 8 kHz.
        source, frames = self.make_source()
        with source:
            audio = sr.Recognizer().record(source, offset=5, duration=2)
        self.assertEqual(audio.frame_data, frames[40000 * 2:56000 * 2])

    def test_record_interval_shorter_than_one_buffer(self):
        for sample_width in (1, 2, 3, 4):
            for sample_rate in (8000, 16000, 44100):
                with self.subTest(sample_width=sample_width, sample_rate=sample_rate):
                    source, frames = self.make_source(sample_rate, sample_width)
                    with source:
                        audio = sr.Recognizer().record(source, offset=0.01, duration=0.02)
                    start = sample_rate // 100 * sample_width
                    end = start + sample_rate // 50 * sample_width
                    self.assertEqual(audio.frame_data, frames[start:end])
                    self.assertEqual(audio.sample_rate, sample_rate)
                    self.assertEqual(audio.sample_width, sample_width)

    def test_record_consecutive_calls_preserve_remaining_audio(self):
        source, frames = self.make_source()
        recognizer = sr.Recognizer()
        with source:
            first = recognizer.record(source, duration=0.75)
            second = recognizer.record(source, duration=0.75)
            remainder = recognizer.record(source)
        self.assertEqual(first.frame_data, frames[:12000])
        self.assertEqual(second.frame_data, frames[12000:24000])
        self.assertEqual(remainder.frame_data, frames[24000:])

    def test_record_offset_is_relative_to_current_position(self):
        source, frames = self.make_source()
        recognizer = sr.Recognizer()
        with source:
            recognizer.record(source, duration=0.5)
            audio = recognizer.record(source, offset=0.25, duration=0.5)
        self.assertEqual(audio.frame_data, frames[12000:20000])

    def test_record_zero_duration_does_not_consume_audio(self):
        source, frames = self.make_source()
        recognizer = sr.Recognizer()
        with source:
            audio = recognizer.record(source, duration=0)
            remainder = recognizer.record(source)
        self.assertEqual(audio.frame_data, b"")
        self.assertEqual(remainder.frame_data, frames)

    def test_record_rounds_fractional_samples_down(self):
        source, frames = self.make_source(sample_rate=100)
        with source:
            audio = sr.Recognizer().record(source, offset=0.015, duration=0.025)
        self.assertEqual(audio.frame_data, frames[2:6])

    def test_record_until_eof_preserves_final_partial_buffer(self):
        source, frames = self.make_source()
        with source:
            audio = sr.Recognizer().record(source)
        self.assertEqual(audio.frame_data, frames)

    def test_record_duration_past_eof_returns_available_audio(self):
        source, frames = self.make_source()
        with source:
            audio = sr.Recognizer().record(source, offset=8, duration=1)
        self.assertEqual(audio.frame_data, frames[128000:])

    def test_record_offset_past_eof_returns_empty_audio(self):
        source, _ = self.make_source()
        with source:
            audio = sr.Recognizer().record(source, offset=10)
        self.assertEqual(audio.frame_data, b"")

    def test_record_accounts_for_short_reads(self):
        source, frames = self.make_source(frame_count=37)
        with source:
            read = source.stream.read
            source.stream.read = lambda size: read(min(size, 3))
            audio = sr.Recognizer().record(source, offset=5 / 8000, duration=17 / 8000)
        self.assertEqual(audio.frame_data, frames[10:44])
