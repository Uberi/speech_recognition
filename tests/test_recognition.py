#!/usr/bin/env python3

import os
import unittest

import speech_recognition as sr

class TestRecognition(unittest.TestCase):
    def setUp(self):
        self.WIT_AI_KEY = os.environ["WIT_AI_KEY"]
        self.BING_KEY = os.environ["BING_KEY"]
        self.HOUNDIFY_CLIENT_ID = os.environ["HOUNDIFY_CLIENT_ID"]
        self.HOUNDIFY_CLIENT_KEY = os.environ["HOUNDIFY_CLIENT_KEY"]
        self.IBM_USERNAME = os.environ["IBM_USERNAME"]
        self.IBM_PASSWORD = os.environ["IBM_PASSWORD"]

        self.AUDIO_FILE_EN = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "examples", "english.wav")

    def test_sphinx(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_sphinx(audio), "wanted to three")

    def test_google(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_google(audio), "one two three")

    def test_wit(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_wit(audio, key=self.WIT_AI_KEY), "one two three")

    def test_bing(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_bing(audio, key=self.BING_KEY), "one two three")

    def test_houndify(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_houndify(audio, client_id=self.HOUNDIFY_CLIENT_ID, client_key=self.HOUNDIFY_CLIENT_KEY), "one two three")

    def test_ibm(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_ibm(audio, username=self.IBM_USERNAME, password=self.IBM_PASSWORD), "one two three ")

if __name__ == "__main__":
    unittest.main()
