#!/usr/bin/env python3

"""Library for performing speech recognition with the Google Speech Recognition API."""

__author__ = "Anthony Zhang (Uberi)"
__version__ = "1.2.3"
__license__ = "BSD"

import io, os, subprocess, wave
import math, audioop, collections
import json

try: # try to use python2 module
    from urllib2 import Request, urlopen, URLError
except ImportError: # otherwise, use python3 module
    from urllib.request import Request, urlopen
    from urllib.error import URLError

#wip: filter out clicks and other too short parts

class AudioSource(object):
    def __init__(self):
        raise NotImplementedError("this is an abstract class")

    def __enter__(self):
        raise NotImplementedError("this is an abstract class")

    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError("this is an abstract class")

try:
    import pyaudio
    class Microphone(AudioSource):
        """
        This is available if PyAudio is available, and is undefined otherwise.

        Creates a new ``Microphone`` instance, which represents a physical microphone on the computer. Subclass of ``AudioSource``.

        If ``device_index`` is unspecified or ``None``, the default microphone is used as the audio source. Otherwise, ``device_index`` should be the index of the device to use for audio input.
        """
        def __init__(self, device_index = None):
            assert device_index is None or isinstance(device_index, int), "Device index must be None or an integer"
            self.device_index = device_index
            self.format = pyaudio.paInt16 # 16-bit int sampling
            self.SAMPLE_WIDTH = pyaudio.get_sample_size(self.format)
            self.RATE = 16000 # sampling rate in Hertz
            self.CHANNELS = 1 # mono audio
            self.CHUNK = 1024 # number of frames stored in each buffer

            self.audio = None
            self.stream = None

        def __enter__(self):
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                input_device_index = self.device_index,
                format = self.format, rate = self.RATE, channels = self.CHANNELS, frames_per_buffer = self.CHUNK,
                input = True, # stream is an input stream
            )
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.audio.terminate()
except ImportError:
    pass

class WavFile(AudioSource):
    """
    Creates a new ``WavFile`` instance, which represents a WAV audio file. Subclass of ``AudioSource``.

    If ``filename_or_fileobject`` is a string, then it is interpreted as a path to a WAV audio file on the filesystem. Otherwise, ``filename_or_fileobject`` should be a file-like object such as ``io.BytesIO`` or similar. In either case, the specified file is used as the audio source.
    """

    def __init__(self, filename_or_fileobject):
        if isinstance(filename_or_fileobject, str):
            self.filename = filename_or_fileobject
        else:
            assert filename_or_fileobject.read, "Given WAV file must be a filename string or a file object"
            self.filename = None
            self.wav_file = filename_or_fileobject
        self.stream = None

    def __enter__(self):
        if self.filename: self.wav_file = open(self.filename, "rb")
        self.wav_reader = wave.open(self.wav_file, "rb")
        self.SAMPLE_WIDTH = self.wav_reader.getsampwidth()
        self.RATE = self.wav_reader.getframerate()
        self.CHANNELS = self.wav_reader.getnchannels()
        assert self.CHANNELS == 1 # audio must be mono
        self.CHUNK = 4096
        self.stream = WavFile.WavStream(self.wav_reader)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filename: self.wav_file.close()
        self.stream = None

    class WavStream(object):
        def __init__(self, wav_reader):
            self.wav_reader = wav_reader

        def read(self, size = -1):
            if size == -1:
                return self.wav_reader.readframes(self.wav_reader.getnframes())
            return self.wav_reader.readframes(size)

class AudioData(object):
    def __init__(self, rate, data):
        self.rate = rate
        self.data = data

class Recognizer(AudioSource):
    def __init__(self, language = "en-US", key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"):
        """
        Creates a new ``Recognizer`` instance, which represents a collection of speech recognition functionality.

        The language is determined by ``language``, a standard language code like `"en-US"` or `"en-GB"`, and defaults to US English. A list of supported language codes can be found `here <http://stackoverflow.com/questions/14257598/>`__. Basically, language codes can be just the language (``en``), or a language with a dialect (``en-US``).

        The Google Speech Recognition API key is specified by ``key``. If not specified, it uses a generic key that works out of the box.
        """
        assert isinstance(language, str), "Language code must be a string"
        assert isinstance(key, str), "Key must be a string"
        self.key = key
        self.language = language

        self.energy_threshold = 100 # minimum audio energy to consider for recording
        self.pause_threshold = 0.8 # seconds of quiet time before a phrase is considered complete
        self.quiet_duration = 0.5 # amount of quiet time to keep on both sides of the recording

    def samples_to_flac(self, source, frame_data):
        assert isinstance(source, AudioSource), "Source must be an audio source"
        import platform, os, stat
        with io.BytesIO() as wav_file:
            with wave.open(wav_file, "wb") as wav_writer:
                wav_writer.setsampwidth(source.SAMPLE_WIDTH)
                wav_writer.setnchannels(source.CHANNELS)
                wav_writer.setframerate(source.RATE)
                wav_writer.writeframes(frame_data)
            wav_data = wav_file.getvalue()

        # determine which converter executable to use
        system = platform.system()
        path = os.path.dirname(os.path.abspath(__file__)) # directory of the current module file, where all the FLAC bundled binaries are stored
        flac_converter = shutil_which("flac") # check for installed version first
        if flac_converter is None: # flac utility is not installed
            if system == "Windows" and platform.machine() in ["i386", "x86", "x86_64", "AMD64"]: # Windows NT, use the bundled FLAC conversion utility
                flac_converter = os.path.join(path, "flac-win32.exe")
            elif system == "Linux" and platform.machine() in ["i386", "x86", "x86_64", "AMD64"]:
                flac_converter = os.path.join(path, "flac-linux-i386")
            else:
                raise ChildProcessError("FLAC conversion utility not available - consider installing the FLAC command line application using brew install flac")

        # mark covnerter as executable
        try:
            stat_info = os.stat(flac_converter)
            os.chmod(flac_converter, stat_info.st_mode | stat.S_IEXEC)
        except OSError: pass

        process = subprocess.Popen("\"%s\" --stdout --totally-silent --best -" % flac_converter, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        flac_data, stderr = process.communicate(wav_data)
        return flac_data

    def record(self, source, duration = None):
        """
        Records up to ``duration`` seconds of audio from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.

        If ``duration`` is not specified, then it will record until there is no more audio input.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"

        frames = io.BytesIO()
        seconds_per_buffer = (source.CHUNK + 0.0) / source.RATE
        elapsed_time = 0
        while True: # loop for the total number of chunks needed
            elapsed_time += seconds_per_buffer
            if duration and elapsed_time > duration: break

            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0: break
            frames.write(buffer)

        frame_data = frames.getvalue()
        frames.close()
        return AudioData(source.RATE, self.samples_to_flac(source, frame_data))

    def listen(self, source, timeout = None):
        """
        Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.

        This is done by waiting until the audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking), and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of silence or there is no more audio input. The ending silence is not included.

        The ``timeout`` parameter is the maximum number of seconds that it will wait for a phrase to start before giving up and throwing a ``TimeoutException`` exception. If ``None``, it will wait indefinitely.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"

        # record audio data as raw samples
        frames = collections.deque()
        assert self.pause_threshold >= self.quiet_duration >= 0
        seconds_per_buffer = (source.CHUNK + 0.0) / source.RATE
        pause_buffer_count = int(math.ceil(self.pause_threshold / seconds_per_buffer)) # number of buffers of quiet audio before the phrase is complete
        quiet_buffer_count = int(math.ceil(self.quiet_duration / seconds_per_buffer)) # maximum number of buffers of quiet audio to retain before and after
        elapsed_time = 0

        # store audio input until the phrase starts
        while True:
            elapsed_time += seconds_per_buffer
            if timeout and elapsed_time > timeout: # handle timeout if specified
                raise TimeoutError("listening timed out")

            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0: break # reached end of the stream
            frames.append(buffer)

            # check if the audio input has stopped being quiet
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH) # energy of the audio signal
            if energy > self.energy_threshold:
                break

            if len(frames) > quiet_buffer_count: # ensure we only keep the needed amount of quiet buffers
                frames.popleft()

        # read audio input until the phrase ends
        pause_count = 0
        while True:
            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0: break # reached end of the stream
            frames.append(buffer)

            # check if the audio input has gone quiet for longer than the pause threshold
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH) # energy of the audio signal
            if energy > self.energy_threshold:
                pause_count = 0
            else:
                pause_count += 1
            if pause_count > pause_buffer_count: # end of the phrase
                break

         # obtain frame data
        for i in range(quiet_buffer_count, pause_count): frames.pop() # remove extra quiet frames at the end
        frame_data = b"".join(list(frames))
        
        return AudioData(source.RATE, self.samples_to_flac(source, frame_data))

    def recognize(self, audio_data, show_all = False):
        """
        Performs speech recognition, using the Google Speech Recognition API, on ``audio_data`` (an ``AudioData`` instance).

        Returns the most likely transcription if ``show_all`` is ``False``, otherwise it returns a ``dict`` of all possible transcriptions and their confidence levels.

        Note: confidence is set to 0 if it isn't given by Google

        Also raises a ``LookupError`` exception if the speech is unintelligible, a ``KeyError`` if the key isn't valid or the quota for the key has been maxed out, and ``IndexError`` if there is no internet connection.
        """
        assert isinstance(audio_data, AudioData), "Data must be audio data"

        url = "http://www.google.com/speech-api/v2/recognize?client=chromium&lang=%s&key=%s" % (self.language, self.key)
        self.request = Request(url, data = audio_data.data, headers = {"Content-Type": "audio/x-flac; rate=%s" % audio_data.rate})
        
        # check for invalid key response from the server
        try:
            response = urlopen(self.request)
        except URLError:
            raise IndexError("No internet connection available to transfer audio data")
        except:
            raise KeyError("Server wouldn't respond (invalid key or quota has been maxed out)")
        response_text = response.read().decode("utf-8")

        # ignore any blank blocks
        actual_result = []
        for line in response_text.split("\n"):
            if not line: continue
            result = json.loads(line)["result"]
            if len(result) != 0:
                actual_result = result[0]

        # make sure we have a list of transcriptions
        if "alternative" not in actual_result:
            raise LookupError("Speech is unintelligible")

        # return the best guess unless told to do otherwise
        if not show_all:
            for prediction in actual_result["alternative"]:
                if "confidence" in prediction:
                    return prediction["transcript"]
            raise LookupError("Speech is unintelligible")

        spoken_text = []

        # check to see if Google thinks it's 100% correct
        default_confidence = 0
        if len(actual_result["alternative"])==1: default_confidence = 1

        # return all the possibilities
        for prediction in actual_result["alternative"]:
            if "confidence" in prediction:
                spoken_text.append({"text":prediction["transcript"],"confidence":prediction["confidence"]})
            else:
                spoken_text.append({"text":prediction["transcript"],"confidence":default_confidence})
        return spoken_text
    
    def listen_in_background(self, source, callback):
        """
        Spawns a thread to repeatedly record phrases from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance and call ``callback`` with that ``AudioData`` instance as soon as each phrase are detected.

        Returns the thread (a ``threading.Thread`` instance) immediately, while the background thread continues to run in parallel.

        Phrase recognition uses the exact same mechanism as ``recognizer_instance.listen(source)``.

        The ``callback`` parameter is a function that should accept two parameters - the ``recognizer_instance``, and an ``AudioData`` instance representing the captured audio. Note that this function will be called from a non-main thread.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"
        import threading
        def threaded_listen():
            while True:
                with source as s: audio = self.listen(s)
                callback(self, audio)
        listener_thread = threading.Thread(target=threaded_listen)
        listener_thread.start()
        return listener_thread

def shutil_which(pgm):
    """
    python2 backport of python3's shutil.which()
    """
    path = os.getenv('PATH')
    for p in path.split(os.path.pathsep):
        p = os.path.join(p, pgm)
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p

if __name__ == "__main__":
    r = Recognizer()
    m = Microphone()

    while True:
        print("Say something!")
        with m as source:
            audio = r.listen(source)
        print("Got it! Now to recognize it...")
        try:
            print("You said " + r.recognize(audio))
        except LookupError:
            print("Oops! Didn't catch that")
