#!/usr/bin/env python3

import speech_recognition as sr
import sys
from time import strftime

# NB: long_interview_example.aif was too large; download https://db.tt/OTBQaC8o

# NB: intended to run from terminal and works for short interview, but not long
# (speech)[502] examples% python audio_transcribe.py short_interview_example.aif
# transcribed to: short_interview_example__google.txt
# (speech)[503] examples%
# (speech)[503] examples% python audio_transcribe.py long_interview_example.aif

args = sys.argv[1:]

if not args:
    print 'usage: <file.aif> (to transcribe) <phrase_timeout> (in seconds)'
    sys.exit(1)

read_path = args[0]
phrase_timeout = float(args[1])
print type(phrase_timeout)

write_path = read_path.replace(r'.aif', '')

# obtain path to "english.wav" in the same folder as this script
from os import path
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), path.join(read_path))
#AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "french.aiff")
#AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "chinese.flac")

# use the audio file as the audio source
r = sr.Recognizer()


full_write_path = write_path + '__google.txt'
with open(full_write_path, 'wb') as f:
    with sr.AudioFile(AUDIO_FILE) as source:
        timed_out = False
        loop_count = 0
        while not timed_out:
            try:
                audio = r.listen(source, phrase_timeout) # read the entire audio file
            except sr.WaitTimeoutError:
                timed_out = True

            loop_count = loop_count + 1
            print "time: {}, loop_count: {}".format(strftime('%H:%M.%S'), loop_count)
            # recognize speech using google
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
            try:
                text = r.recognize_google(audio)
                # print("google thinks you said " + r.recognize_google(audio))
            except sr.UnknownValueError:
                text = "google could not understand audio"
            except sr.RequestError as e:
                text = "google error; {0}".format(e)
            except BaseException as e:
                text = e
            print text
            f.write(' ' + str(text))

print "transcribed to: {}".format(full_write_path)
