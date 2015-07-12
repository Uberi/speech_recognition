import speech_recognition as sr

r = sr.Recognizer()
m = sr.Microphone()

print("A moment of silence, please...")
with m as source:
    r.adjust_for_ambient_noise(source)
    print("Set minimum energy threshold to {}".format(r.energy_threshold))
    while True:
        print("Say something!")
        audio = r.listen(source)
        print("Got it! Now to recognize it...")
        try:
            print("You said " + r.recognize(audio))
        except LookupError:
            print("Oops! Didn't catch that")
