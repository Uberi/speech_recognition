#!/usr/bin/env python3

import os
import unittest

import speech_recognition as sr

class TestRecognition(unittest.TestCase):
    def setUp(self):
        self.AUDIO_FILE_EN = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "examples", "english.wav")

    def test_sphinx(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_sphinx(audio), "wanted to three")

    def test_google(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_google(audio), "one two three")

    @unittest.skipUnless("WIT_AI_KEY" in os.environ, "requires Wit.ai key to be specified in WIT_AI_KEY environment variable")
    def test_wit(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_wit(audio, key=os.environ["WIT_AI_KEY"]), "one two three")

    @unittest.skipUnless("BING_KEY" in os.environ, "requires Microsoft Bing Voice Recognition key to be specified in BING_KEY environment variable")
    def test_bing(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_bing(audio, key=os.environ["BING_KEY"]), "one two three")

    @unittest.skipUnless("HOUNDIFY_CLIENT_ID" in os.environ and "HOUNDIFY_CLIENT_KEY" in os.environ, "requires Houndify client ID and client key to be specified in HOUNDIFY_CLIENT_ID and HOUNDIFY_CLIENT_KEY environment variables")
    def test_houndify(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_houndify(audio, client_id=os.environ["HOUNDIFY_CLIENT_ID"], client_key=os.environ["HOUNDIFY_CLIENT_KEY"]), "one two three")

    @unittest.skipUnless("IBM_USERNAME" in os.environ and "IBM_PASSWORD" in os.environ, "requires IBM Speech to Text username and password to be specified in IBM_USERNAME and IBM_PASSWORD environment variables")
    def test_ibm(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_ibm(audio, username=os.environ["IBM_USERNAME"], password=os.environ["IBM_PASSWORD"]), "one two three ")

if __name__ == "__main__":
    unittest.main()
