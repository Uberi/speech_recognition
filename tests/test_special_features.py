#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest

import speech_recognition as sr


class TestSpecialFeatures(unittest.TestCase):
    def setUp(self):
        self.AUDIO_FILE_EN = os.path.join(os.path.dirname(os.path.realpath(__file__)), "english.wav")

    def test_sphinx_keywords(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE_EN) as source: audio = r.record(source)
        self.assertEqual(r.recognize_sphinx(audio, keyword_entries=[("one", 1.0), ("two", 1.0), ("three", 1.0)]), "three  two  two  one ")
        self.assertEqual(r.recognize_sphinx(audio, keyword_entries=[("wan", 0.95), ("too", 1.0), ("tree", 1.0)]), "tree  too  wan  too  wan ")
        self.assertEqual(r.recognize_sphinx(audio, keyword_entries=[("un", 0.95), ("to", 1.0), ("tee", 1.0)]), "tee  to  un  to  un  un  un ")


if __name__ == "__main__":
    unittest.main()
