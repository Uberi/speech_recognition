import speech_recognition as sr

r = sr.Recognizer()
m = sr.Microphone()

try:
    print("A moment of silence, please...")
    with m as source:
        r.adjust_for_ambient_noise(source)
        print("Set minimum energy threshold to {}".format(r.energy_threshold))
        while True:
            print("Say something!")
            audio = r.listen(source)
            print("Got it! Now to recognize it...")
            try:
                value = r.recognize(audio)
                if str is bytes: # this version of Python uses bytes for strings (Python 2)
                    print(u"You said {}".format(value).encode("utf-8"))
                else: # this version of Python uses unicode for strings (Python 3+)
                    print("You said {}".format(value))
            except LookupError:
                print("Oops! Didn't catch that")
except KeyboardInterrupt:
    pass
