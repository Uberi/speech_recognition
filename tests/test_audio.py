#!/usr/bin/env python3

import os
import wave
import aifc
import io
import subprocess
import unittest

import speech_recognition as sr


class TestAudioFile(unittest.TestCase):
    def setUp(self):
        self.AUDIO_FILE_WAV = os.path.join(os.path.dirname(os.path.realpath(__file__)), "english.wav")
        self.AUDIO_FILE_AIFF = os.path.join(os.path.dirname(os.path.realpath(__file__)), "french.aiff")
        self.AUDIO_FILE_FLAC = os.path.join(os.path.dirname(os.path.realpath(__file__)), "chinese.flac")

    def test_wav_load(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_WAV) as source: audio = r.record(source)
        self.assertIsInstance(audio, sr.AudioData)
        audio_reader = wave.open(self.AUDIO_FILE_WAV, "rb")
        self.assertEqual(audio.sample_rate, audio_reader.getframerate())
        self.assertEqual(audio.sample_width, audio_reader.getsampwidth())
        self.assertEqual(audio.get_raw_data(), audio_reader.readframes(audio_reader.getnframes()))
        audio_reader.close()
        

    def test_aiff_load(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_AIFF) as source: audio = r.record(source)
        self.assertIsInstance(audio, sr.AudioData)
        audio_reader = aifc.open(self.AUDIO_FILE_AIFF, "rb")
        self.assertEqual(audio.sample_rate, audio_reader.getframerate())
        self.assertEqual(audio.sample_width, audio_reader.getsampwidth())
        aiff_data = audio_reader.readframes(audio_reader.getnframes())
        aiff_data_little_endian = aiff_data[1::-1] + b"".join(aiff_data[i + 2:i:-1] for i in range(1, len(aiff_data), 2))
        self.assertEqual(audio.get_raw_data(), aiff_data_little_endian)
        audio_reader.close()

    def test_flac_load(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_FLAC) as source: audio = r.record(source)
        self.assertIsInstance(audio, sr.AudioData)
        process = subprocess.Popen([sr.get_flac_converter(), "--stdout", "--totally-silent", "--decode", "--force-aiff-format", self.AUDIO_FILE_FLAC], stdout=subprocess.PIPE)
        aiff_data, _ = process.communicate()
        aiff_file = io.BytesIO(aiff_data)
        audio_reader = aifc.open(aiff_file, "rb")
        self.assertEqual(audio.sample_rate, audio_reader.getframerate())
        self.assertEqual(audio.sample_width, audio_reader.getsampwidth())
        aiff_data = audio_reader.readframes(audio_reader.getnframes())
        aiff_data_little_endian = aiff_data[1::-1] + b"".join(aiff_data[i + 2:i:-1] for i in range(1, len(aiff_data), 2))
        self.assertEqual(audio.get_raw_data(), aiff_data_little_endian)
        audio_reader.close()
        aiff_file.close()


if __name__ == "__main__":
    unittest.main()
