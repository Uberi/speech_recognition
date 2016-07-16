#!/usr/bin/env python3

import speech_recognition as sr

import sys

# NB: long_interview_example.aif was too large; download https://db.tt/OTBQaC8o

# NB: intended to run from terminal and works for short interview, but not long
# (speech)[502] examples% python audio_transcribe.py short_interview_example.aif
# transcribed to: short_interview_example__sphinx.txt
# (speech)[503] examples%
# (speech)[503] examples% python audio_transcribe.py long_interview_example.aif

args = sys.argv[1:]

if not args:
    print 'usage: <file.aif> (to transcribe)'
    sys.exit(1)

read_path = args[0]

write_path = read_path.replace(r'.aif', '')

# obtain path to "english.wav" in the same folder as this script
from os import path
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), path.join(read_path))
#AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "french.aiff")
#AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "chinese.flac")

# use the audio file as the audio source
r = sr.Recognizer()

with sr.AudioFile(AUDIO_FILE) as source:
    for i in range(2):
        audio = r.listen(source, timeout=10) # read the entire audio file

        # recognize speech using Sphinx
        try:
            text = r.recognize_sphinx(audio)
            # print("Sphinx thinks you said " + r.recognize_sphinx(audio))
        except sr.UnknownValueError:
            text = "Sphinx could not understand audio"
        except sr.RequestError as e:
            text = "Sphinx error; {0}".format(e)
        except Error as e:
            text = e

        full_write_path = write_path + '__sphinx.txt'
        with open(full_write_path, 'wb') as f:
            f.write(text)
print "transcribed to: {}".format(full_write_path)

# # recognize speech using Google Speech Recognition
# try:
#     # for testing purposes, we're just using the default API key
#     # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
#     # instead of `r.recognize_google(audio)`
#     print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
# except sr.UnknownValueError:
#     print("Google Speech Recognition could not understand audio")
# except sr.RequestError as e:
#     print("Could not request results from Google Speech Recognition service; {0}".format(e))

# # recognize speech using Wit.ai
# WIT_AI_KEY = "INSERT WIT.AI API KEY HERE" # Wit.ai keys are 32-character uppercase alphanumeric strings
# try:
#     print("Wit.ai thinks you said " + r.recognize_wit(audio, key=WIT_AI_KEY))
# except sr.UnknownValueError:
#     print("Wit.ai could not understand audio")
# except sr.RequestError as e:
#     print("Could not request results from Wit.ai service; {0}".format(e))
#
# # recognize speech using Microsoft Bing Voice Recognition
# BING_KEY = "INSERT BING API KEY HERE" # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
# try:
#     print("Microsoft Bing Voice Recognition thinks you said " + r.recognize_bing(audio, key=BING_KEY))
# except sr.UnknownValueError:
#     print("Microsoft Bing Voice Recognition could not understand audio")
# except sr.RequestError as e:
#     print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))
#
# # recognize speech using api.ai
# API_AI_CLIENT_ACCESS_TOKEN = "INSERT API.AI API KEY HERE" # api.ai keys are 32-character lowercase hexadecimal strings
# try:
#     print("api.ai thinks you said " + r.recognize_api(audio, client_access_token=API_AI_CLIENT_ACCESS_TOKEN))
# except sr.UnknownValueError:
#     print("api.ai could not understand audio")
# except sr.RequestError as e:
#     print("Could not request results from api.ai service; {0}".format(e))
#
# # recognize speech using IBM Speech to Text
# IBM_USERNAME = "INSERT IBM SPEECH TO TEXT USERNAME HERE" # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
# IBM_PASSWORD = "INSERT IBM SPEECH TO TEXT PASSWORD HERE" # IBM Speech to Text passwords are mixed-case alphanumeric strings
# try:
#     print("IBM Speech to Text thinks you said " + r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD))
# except sr.UnknownValueError:
#     print("IBM Speech to Text could not understand audio")
# except sr.RequestError as e:
#     print("Could not request results from IBM Speech to Text service; {0}".format(e))
