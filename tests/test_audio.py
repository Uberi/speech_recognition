#!/usr/bin/env python3

import unittest
from os import path

import speech_recognition as sr


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


if __name__ == "__main__":
    unittest.main()
