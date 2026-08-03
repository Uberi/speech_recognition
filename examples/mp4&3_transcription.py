import moviepy.editor
import speech_recognition as sr
from pydub import silence, AudioSegment
from pathlib import Path
import os

# mp4---> wav file
video=moviepy.editor.VideoFileClip('<file_name>.mp4')
audio=video.audio
audio.write_audiofile('<mp4_file_name>.wav') #creates a wav file in CWD

#mp3-->wav file
my_file = Path('<file_path>') # MP-3 file location
audio = AudioSegment.from_mp3(my_file)
audio.export("<mp3_file_name>.wav",format="wav") #Creates a processable wav file in CWD

#Code for recognizing mp3 or mp4 file
r = sr.Recognizer()

with sr.AudioFile('<MP3/MP4_path>.wav') as source: #Mention the Path of file to be read
  audio = r.listen(source)

#recognize using google_api(Google Speech Recognition)
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
    
 # recognize speech using Microsoft Azure Speech
AZURE_SPEECH_KEY = "INSERT AZURE SPEECH API KEY HERE"  # Microsoft Speech API keys 32-character lowercase hexadecimal strings
try:
    print("Microsoft Azure Speech thinks you said " + r.recognize_azure(audio, key=AZURE_SPEECH_KEY))
except sr.UnknownValueError:
    print("Microsoft Azure Speech could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Microsoft Azure Speech service; {0}".format(e))
