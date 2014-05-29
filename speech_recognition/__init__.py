"""Library for performing speech recognition with the Google Speech Recognition API."""

__author__ = 'Anthony Zhang (Uberi)'
__version__ = '1.0.1'
__license__ = 'BSD'

import io, subprocess, wave, platform, shutil
import math, audioop, collections
import json, urllib.request

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
        def __init__(self, device_index = None):
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
    def __init__(self, filename_or_fileobject):
        if isinstance(filename_or_fileobject, str):
            self.filename = filename_or_fileobject
        else:
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
    def __init__(self, language = "en-US"):
        self.language = language

        self.energy_threshold = 100 # minimum audio energy to consider for recording
        self.pause_threshold = 0.8 # seconds of quiet time before a phrase is considered complete
        self.quiet_duration = 0.5 # amount of quiet time to keep on both sides of the recording

    def samples_to_flac(self, source, frame_data):
        with io.BytesIO() as wav_file:
            with wave.open(wav_file, "wb") as wav_writer:
                wav_writer.setsampwidth(source.SAMPLE_WIDTH)
                wav_writer.setnchannels(source.CHANNELS)
                wav_writer.setframerate(source.RATE)
                wav_writer.writeframes(frame_data)
            wav_data = wav_file.getvalue()

        # determine which converter executable to use
        system = platform.system()
        if system == "Windows": # Windows NT, use the bundled FLAC conversion utility
            flac_converter = "./flac-win32.exe"
        elif system == "Linux": # search for a built in FLAC utility
            flac_converter = "./flac-linux-i386"
        else:
            flac_converter = shutil.which("flac")
            if not flac_converter:
                raise ChildProcessError("FLAC conversion utility not available")
        process = subprocess.Popen("\"%s\" --stdout --totally-silent --best -" % flac_converter, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        flac_data, stderr = process.communicate(wav_data)
        return flac_data

    def record(self, source, duration = None):
        assert isinstance(source, AudioSource) and source.stream

        frames = io.BytesIO()
        seconds_per_buffer = source.CHUNK / source.RATE
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
        assert isinstance(source, AudioSource) and source.stream

        # record audio data as raw samples
        frames = collections.deque()
        assert self.pause_threshold >= self.quiet_duration >= 0
        seconds_per_buffer = source.CHUNK / source.RATE
        pause_buffer_count = math.ceil(self.pause_threshold / seconds_per_buffer) # number of buffers of quiet audio before the phrase is complete
        quiet_buffer_count = math.ceil(self.quiet_duration / seconds_per_buffer) # maximum number of buffers of quiet audio to retain before and after
        elapsed_time = 0

        # store audio input until the phrase starts
        while True:
            # handle timeout if specified
            elapsed_time += seconds_per_buffer
            if timeout and elapsed_time > timeout:
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
        for i in range(quiet_buffer_count, pause_buffer_count): frames.pop() # remove extra quiet frames at the end
        frame_data = b"".join(list(frames))

        return AudioData(source.RATE, self.samples_to_flac(source, frame_data))

    def recognize(self, audio_data):
        assert isinstance(audio_data, AudioData)

        url = "http://www.google.com/speech-api/v1/recognize?client=chromium&lang=%s&maxresults=2" % self.language
        self.request = urllib.request.Request(url, data = audio_data.data, headers = {"Content-Type": "audio/x-flac; rate=%s" % audio_data.rate})
        response = urllib.request.urlopen(self.request)
        response_text = response.read().decode("utf-8")
        result = json.loads(response_text)["hypotheses"]
        if len(result) == 0: # no matches found
            raise LookupError("speech is unintelligible")
        spoken_text = result[0]["utterance"]
        return spoken_text

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
