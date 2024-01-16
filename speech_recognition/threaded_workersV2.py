#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

from threading import Thread
try:
    from queue import Queue  # Python 3 import
except ImportError:
    from Queue import Queue  # Python 2 import

import speech_recognition as sr


r = sr.Recognizer()
audio_queue = Queue()



r.energy_threshold = 300  # minimum audio energy to consider for recording
r.dynamic_energy_threshold = True
r.dynamic_energy_adjustment_damping = 0.5
r.dynamic_energy_ratio = 1.5
r.pause_threshold = 0.05  # seconds of non-speaking audio before a phrase is considered complete
r.operation_timeout = None  # seconds after an internal operation (e.g., an API request) starts before it times out, or ``None`` for no timeout

r.phrase_threshold = 0.1  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
r.non_speaking_duration = 0.025  # seconds of non-speaking audio to keep on both sides of the recording


myDecoder =r.get_sphinx_decoder(grammar='counting.gram');

j=0
def recognize_worker():
    # this runs in a background thread
    global j,myDecoder;
    while True:
        audio = audio_queue.get()  # retrieve the next audio processing job from the main thread
        if audio is None: break  # stop processing if the main thread is done
        """
        # received audio data, now we'll recognize it using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            print("Calling Google API")
            print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        """
        try:
            print("Sphinx recognition for \"one two three\" for counting grammar:")
            #print(r.recognize_sphinx(audio, grammar='counting.gram'))
            print(r.recognize_sphinx_byDecoder(myDecoder,audio));
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
            

        with open("microphone-results{0}.wav".format(j), "wb") as f:
            j=j+1
            #f.write(audio.get_wav_data())
            
        audio_queue.task_done()  # mark the audio processing job as completed in the queue


# start a new thread to recognize audio, while this thread focuses on listening
recognize_thread = Thread(target=recognize_worker)
recognize_thread.daemon = True
recognize_thread.start()
with sr.Microphone() as source:
    try:
        while True:  # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
            audio_queue.put(r.listen(source))
    except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
        pass

audio_queue.join()  # block until all current audio processing jobs are done
audio_queue.put(None)  # tell the recognize_thread to stop
recognize_thread.join()  # wait for the recognize_thread to actually stop







