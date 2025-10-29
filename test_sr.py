from speech_recognition import Recognizer, Microphone

r = Recognizer()

with Microphone() as source:
    print("Say something...")
    audio = r.listen(source)

print("Got it! Now recognizing...")

try:
    text = r.recognize_google(audio)
    print("You said:", text)
except Exception as e:
    print("Error:", e)
