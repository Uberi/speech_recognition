#!/usr/bin/env python3

import speech_recognition as sr

from os import path
AUDIO_FILE_EN = path.join(path.dirname(path.realpath(__file__)), "english.wav")
AUDIO_FILE_FR = path.join(path.dirname(path.realpath(__file__)), "french.aiff")

# use the audio file as the audio source
r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE_EN) as source:
    audio_en = r.record(source)  # read the entire audio file
with sr.AudioFile(AUDIO_FILE_FR) as source:
    audio_fr = r.record(source)  # read the entire audio file

# recognize keywords using Sphinx
try:
    print("Sphinx recognition for \"one two three\" with different sets of keywords:")
    print(r.recognize_sphinx(audio_en, keyword_entries=[("one", 1.0), ("two", 1.0), ("three", 1.0)]))
    print(r.recognize_sphinx(audio_en, keyword_entries=[("wan", 0.95), ("too", 1.0), ("tree", 1.0)]))
    print(r.recognize_sphinx(audio_en, keyword_entries=[("un", 0.95), ("to", 1.0), ("tee", 1.0)]))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))

# grammar example using Sphinx
try:
    print("Sphinx recognition for \"one two three\" for counting grammar:")
    print(r.recognize_sphinx(audio_en, grammar='counting.gram'))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))


# recognize preferred phrases using Google Cloud Speech
GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""INSERT THE CONTENTS OF THE GOOGLE CLOUD SPEECH JSON CREDENTIALS FILE HERE"""
try:
    print("Google Cloud Speech recognition for \"numero\" with different sets of preferred phrases:")
    print(r.recognize_google_cloud(audio_fr, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, preferred_phrases=["noomarow"]))
    print(r.recognize_google_cloud(audio_fr, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, preferred_phrases=["newmarrow"]))
except sr.UnknownValueError:
    print("Google Cloud Speech could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Cloud Speech service; {0}".format(e))
