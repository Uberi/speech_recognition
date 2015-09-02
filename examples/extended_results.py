#!/usr/bin/env python3

import speech_recognition as sr

# obtain path to "test.wav" in the same folder as this script
from os import path
WAV_FILE = path.join(path.dirname(path.realpath(__file__)), "test.wav")

# use "test.wav" as the audio source
r = sr.Recognizer()
with sr.WavFile(WAV_FILE) as source:
    audio = r.record(source) # read the entire WAV file

# recognize speech using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY", show_all=True)`
    # instead of `r.recognize_google(audio, show_all=True)`
    from pprint import pprint
    print("Google Speech Recognition results:")
    pprint(r.recognize_google(audio, show_all=True)) # pretty-print the recognition result
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError:
    print("Could not request results from Google Speech Recognition service")

# recognize speech using Wit.ai
WIT_AI_KEY = "INSERT WIT.AI API KEY HERE" # Wit.ai keys are 32-character uppercase alphanumeric strings
try:
    from pprint import pprint
    print("Wit.ai recognition results:")
    pprint(r.recognize_wit(audio, key=WIT_AI_KEY, show_all=True)) # pretty-print the recognition result
except sr.UnknownValueError:
    print("Wit.ai could not understand audio")
except sr.RequestError:
    print("Could not request results from Wit.ai service")

# recognize speech using IBM Speech to Text
IBM_USERNAME = "INSERT IBM SPEECH TO TEXT USERNAME HERE" # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
IBM_PASSWORD = "INSERT IBM SPEECH TO TEXT PASSWORD HERE" # IBM Speech to Text passwords are mixed-case alphanumeric strings
try:
    from pprint import pprint
    print("IBM Speech to Text results:")
    pprint(r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD, show_all=True)) # pretty-print the recognition result
except sr.UnknownValueError:
    print("IBM Speech to Text could not understand audio")
except sr.RequestError:
    print("Could not request results from IBM Speech to Text service")

# recognize speech using AT&T Speech to Text
ATT_APP_KEY = "INSERT AT&T SPEECH TO TEXT APP KEY HERE" # AT&T Speech to Text app keys are 32-character lowercase alphanumeric strings
ATT_APP_SECRET = "INSERT AT&T SPEECH TO TEXT APP SECRET HERE" # AT&T Speech to Text app secrets are 32-character lowercase alphanumeric strings
try:
    print("AT&T Speech to Text thinks you said " + r.recognize_att(audio, app_key=ATT_APP_KEY, app_secret=ATT_APP_SECRET))
except sr.UnknownValueError:
    print("AT&T Speech to Text could not understand audio")
except sr.RequestError:
    print("Could not request results from AT&T Speech to Text service")
