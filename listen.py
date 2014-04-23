import threading
from array import array
import Queue

import pyaudio

CHUNK_SIZE = 1024
MIN_VOLUME = 500
# if the recording thread can't consume fast enough, the listener will start discarding
BUF_MAX_SIZE = CHUNK_SIZE * 10


def main():
    stop_event = threading.Event()
    q = Queue.Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))

    listen_t = threading.Thread(target=listen, args=(stopped, q))
    listen_t.start()
    record_t = threading.Thread(target=record, args=(stopped, q))
    record_t.start()

    try:
        while True:
            listen_t.join(0.1)
            record_t.join(0.1)
    except KeyboardInterrupt:
        stop_event.set()

    listen_t.join()
    record_t.join()


def record(stop_event, q):
    while True:
        if stop_event.wait(timeout=0):
            break
        chunk = q.get()
        vol = max(chunk)
        if vol >= MIN_VOLUME:
            # TODO: write to file
            print "O",
        else:
            print "-",


def listen(stop_event, q):
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=2,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
    )

    while True:
        if stop_event.wait(timeout=0):
            break
        try:
            q.put(array('h', stream.read(CHUNK_SIZE)))
        except Queue.Full:
            pass