#!/usr/bin/env python3

"""Library for performing speech recognition with the Google Speech Recognition API."""

__author__ = "Anthony Zhang (Uberi)"
__version__ = "2.2.0"
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

        A device index is an integer between 0 and ``pyaudio.get_device_count() - 1`` (assume we have used ``import pyaudio`` beforehand) inclusive. It represents an audio device such as a microphone or speaker. See the `PyAudio documentation <http://people.csail.mit.edu/hubert/pyaudio/docs/>`__ for more details.

        The microphone audio is recorded in chunks of ``chunk_size`` samples, at a rate of ``sample_rate`` samples per second (Hertz).

        Higher ``sample_rate`` values result in better audio quality, but also more bandwidth (and therefore, slower recognition). Additionally, some machines, such as some Raspberry Pi models, can't keep up if this value is too high.

        Higher ``chunk_size`` values help avoid triggering on rapidly changing ambient noise, but also makes detection less sensitive. This value, generally, should be left at its default.
        """
        def __init__(self, device_index = None, sample_rate = 16000, chunk_size = 1024):
            assert device_index is None or isinstance(device_index, int), "Device index must be None or an integer"
            if device_index is not None: # ensure device index is in range
                audio = pyaudio.PyAudio(); count = audio.get_device_count(); audio.terminate() # obtain device count
                assert 0 <= device_index < count, "Device index out of range"
            assert isinstance(sample_rate, int) and sample_rate > 0, "Sample rate must be a positive integer"
            assert isinstance(chunk_size, int) and chunk_size > 0, "Chunk size must be a positive integer"
            self.device_index = device_index
            self.format = pyaudio.paInt16 # 16-bit int sampling
            self.SAMPLE_WIDTH = pyaudio.get_sample_size(self.format) # size of each sample
            self.SAMPLE_RATE = sample_rate # sampling rate in Hertz
            self.CHANNELS = 1 # mono audio
            self.CHUNK = chunk_size # number of frames stored in each buffer

            self.audio = None
            self.stream = None

        def __enter__(self):
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                input_device_index = self.device_index,
                format = self.format, rate = self.SAMPLE_RATE, channels = self.CHANNELS, frames_per_buffer = self.CHUNK,
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

    If ``filename_or_fileobject`` is a string, then it is interpreted as a path to a WAV audio file (mono or stereo) on the filesystem. Otherwise, ``filename_or_fileobject`` should be a file-like object such as ``io.BytesIO`` or similar. In either case, the specified file is used as the audio source.
    """

    def __init__(self, filename_or_fileobject):
        if isinstance(filename_or_fileobject, str):
            self.filename = filename_or_fileobject
        else:
            assert filename_or_fileobject.read, "Given WAV file must be a filename string or a file object"
            self.filename = None
            self.wav_file = filename_or_fileobject
        self.stream = None
        self.DURATION = None

    def __enter__(self):
        if self.filename: self.wav_file = open(self.filename, "rb")
        self.wav_reader = wave.open(self.wav_file, "rb")
        self.SAMPLE_WIDTH = self.wav_reader.getsampwidth()
        self.SAMPLE_RATE = self.wav_reader.getframerate()
        self.CHANNELS = self.wav_reader.getnchannels()
        assert self.CHANNELS == 1 or self.CHANNELS == 2, "Audio must be mono or stereo"
        self.CHUNK = 4096
        self.FRAME_COUNT = self.wav_reader.getnframes()
        self.DURATION = self.FRAME_COUNT / float(self.SAMPLE_RATE)
        self.stream = WavFile.WavStream(self.wav_reader)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.filename: self.wav_file.close()
        self.stream = None
        self.DURATION = None

    class WavStream(object):
        def __init__(self, wav_reader):
            self.wav_reader = wav_reader

        def read(self, size = -1):
            buffer = self.wav_reader.readframes(self.wav_reader.getnframes() if size == -1 else size)
            if self.wav_reader.getnchannels() != 1: # stereo audio
                buffer = audioop.tomono(buffer, self.wav_reader.getsampwidth(), 1, 1) # convert stereo audio data to mono
            return buffer

class AudioData(object):
    def __init__(self, sample_rate, data):
        self.sample_rate = sample_rate
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

        self.energy_threshold = 300 # minimum audio energy to consider for recording
        self.dynamic_energy_threshold = True
        self.dynamic_energy_adjustment_damping = 0.15
        self.dynamic_energy_ratio = 1.5
        self.pause_threshold = 0.8 # seconds of quiet time before a phrase is considered complete
        self.quiet_duration = 0.5 # amount of quiet time to keep on both sides of the recording

    def samples_to_flac(self, source, frame_data):
        assert isinstance(source, AudioSource), "Source must be an audio source"
        import platform, os, stat
        with io.BytesIO() as wav_file:
            wav_writer = wave.open(wav_file, "wb")
            try: # note that we can't use context manager due to Python 2 not supporting it
                wav_writer.setsampwidth(source.SAMPLE_WIDTH)
                wav_writer.setnchannels(source.CHANNELS)
                wav_writer.setframerate(source.SAMPLE_RATE)
                wav_writer.writeframes(frame_data)
            finally:  # make sure resources are cleaned up
                wav_writer.close()
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
            elif system == "Darwin" and platform.machine() in ["i386", "x86", "x86_64", "AMD64"]:
                flac_converter = os.path.join(path, "flac-mac")
            else:
                raise OSError("FLAC conversion utility not available - consider installing the FLAC command line application using `brew install flac` or your operating system's equivalent")

        # mark covnerter as executable
        try:
            stat_info = os.stat(flac_converter)
            os.chmod(flac_converter, stat_info.st_mode | stat.S_IEXEC)
        except OSError: pass

        process = subprocess.Popen("\"%s\" --stdout --totally-silent --best -" % flac_converter, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        flac_data, stderr = process.communicate(wav_data)
        return flac_data

    def record(self, source, duration = None, offset = None):
        """
        Records up to ``duration`` seconds of audio from ``source`` (an ``AudioSource`` instance) starting at ``offset`` (or at the beginning if not specified) into an ``AudioData`` instance, which it returns.

        If ``duration`` is not specified, then it will record until there is no more audio input.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"

        frames = io.BytesIO()
        seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
        elapsed_time = 0
        offset_time = 0
        offset_reached = False
        while True: # loop for the total number of chunks needed
            if offset and not offset_reached:
                offset_time += seconds_per_buffer
                if offset_time > offset:
                    offset_reached = True

            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0: break

            if offset_reached or not offset:
                elapsed_time += seconds_per_buffer
                if duration and elapsed_time > duration: break

                frames.write(buffer)

        frame_data = frames.getvalue()
        frames.close()
        return AudioData(source.SAMPLE_RATE, self.samples_to_flac(source, frame_data))

    def adjust_for_ambient_noise(self, source, duration = 1):
        """
        Adjusts the energy threshold dynamically using audio from ``source`` (an ``AudioSource`` instance) to account for ambient noise.

        Intended to calibrate the energy threshold with the ambient energy level. Should be used on periods of audio without speech - will stop early if any speech is detected.

        The ``duration`` parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning. This value should be at least 0.5 in order to get a representative sample of the ambient noise.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"

        seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
        elapsed_time = 0

        # adjust energy threshold until a phrase starts
        while True:
            elapsed_time += seconds_per_buffer
            if elapsed_time > duration: break
            buffer = source.stream.read(source.CHUNK)

            # check if the audio input has stopped being quiet
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH) # energy of the audio signal

            # dynamically adjust the energy threshold using assymmetric weighted average
            damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer # account for different chunk sizes and rates
            target_energy = energy * self.dynamic_energy_ratio
            self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)

    def listen(self, source, timeout = None):
        """
        Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.

        This is done by waiting until the audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking), and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of silence or there is no more audio input. The ending silence is not included.

        The ``timeout`` parameter is the maximum number of seconds that it will wait for a phrase to start before giving up and throwing an ``OSError`` exception. If ``None``, it will wait indefinitely.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"

        # record audio data as raw samples
        frames = collections.deque()
        assert self.pause_threshold >= self.quiet_duration >= 0
        seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
        pause_buffer_count = int(math.ceil(self.pause_threshold / seconds_per_buffer)) # number of buffers of quiet audio before the phrase is complete
        quiet_buffer_count = int(math.ceil(self.quiet_duration / seconds_per_buffer)) # maximum number of buffers of quiet audio to retain before and after
        elapsed_time = 0

        # store audio input until the phrase starts
        while True:
            elapsed_time += seconds_per_buffer
            if timeout and elapsed_time > timeout: # handle timeout if specified
                raise OSError("listening timed out")

            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0: break # reached end of the stream
            frames.append(buffer)

            # check if the audio input has stopped being quiet
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH) # energy of the audio signal
            if energy > self.energy_threshold: break

            # dynamically adjust the energy threshold using assymmetric weighted average
            if self.dynamic_energy_threshold:
                damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer # account for different chunk sizes and rates
                target_energy = energy * self.dynamic_energy_ratio
                self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)

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

        return AudioData(source.SAMPLE_RATE, self.samples_to_flac(source, frame_data))

    def recognize(self, audio_data, show_all = False):
        """
        Performs speech recognition, using the Google Speech Recognition API, on ``audio_data`` (an ``AudioData`` instance).

        Returns the most likely transcription if ``show_all`` is ``False``, otherwise it returns a ``dict`` of all possible transcriptions and their confidence levels.

        Note: confidence is set to 0 if it isn't given by Google

        Also raises a ``LookupError`` exception if the speech is unintelligible, a ``KeyError`` if the key isn't valid or the quota for the key has been maxed out, and ``IndexError`` if there is no internet connection.
        """
        assert isinstance(audio_data, AudioData), "Data must be audio data"

        url = "http://www.google.com/speech-api/v2/recognize?client=chromium&lang=%s&key=%s" % (self.language, self.key)
        self.request = Request(url, data = audio_data.data, headers = {"Content-Type": "audio/x-flac; rate=%s" % audio_data.sample_rate})

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
                break

        # make sure we have a list of transcriptions
        if "alternative" not in actual_result:
            raise LookupError("Speech is unintelligible")

        # return the best guess unless told to do otherwise
        if not show_all:
            for prediction in actual_result["alternative"]:
                if "transcript" in prediction:
                    return prediction["transcript"]
            raise LookupError("Speech is unintelligible")


        # return all the possibilities
        spoken_text = []
        for i, prediction in enumerate(actual_result["alternative"]):
            if "transcript" in prediction:
                spoken_text.append({"text": prediction["transcript"], "confidence": 1 if i == 0 else 0})
        return spoken_text

    def listen_in_background(self, source, callback):
        """
        Spawns a thread to repeatedly record phrases from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance and call ``callback`` with that ``AudioData`` instance as soon as each phrase are detected.

        Returns a function object that, when called, stops the background listener thread. The background thread is a daemon and will not stop the program from exiting if there are no other non-daemon threads.

        Phrase recognition uses the exact same mechanism as ``recognizer_instance.listen(source)``.

        The ``callback`` parameter is a function that should accept two parameters - the ``recognizer_instance``, and an ``AudioData`` instance representing the captured audio. Note that this function will be called from a non-main thread.
        """
        assert isinstance(source, AudioSource), "Source must be an audio source"
        import threading
        running = [True]
        def threaded_listen():
            with source as s:
                while running[0]:
                    try: # try to detect speech for only one second to do another check if running is enabled
                        audio = self.listen(s, 1)
                    except OSError:
                        pass
                    else:
                        if running[0]: callback(self, audio)
        def stopper():
            running[0] = False
        listener_thread = threading.Thread(target=threaded_listen)
        listener_thread.daemon = True
        listener_thread.start()
        return stopper

def shutil_which(pgm):
    """
    python2 backport of python3's shutil.which()
    """
    path = os.getenv('PATH')
    for p in path.split(os.path.pathsep):
        p = os.path.join(p, pgm)
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
