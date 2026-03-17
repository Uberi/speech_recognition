# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "SpeechRecognition[audio,openai]>=3.15.1",
#     "pynput>=1.8.1",
# ]
# ///

from __future__ import annotations

import os
import queue
import signal
import sys
import threading
from dataclasses import dataclass

import speech_recognition as sr
from pynput import keyboard

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True, write_through=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True, write_through=True)

SAMPLE_RATE = 16_000
CHUNK_SIZE = 1_024
MIN_DURATION_SECONDS = 1.0
MIN_LIVE_SEGMENT_SECONDS = 0.8
LIVE_SEGMENT_SECONDS = 2.5
SEGMENT_POLL_SECONDS = 0.2
MODEL = "gpt-4o-mini-transcribe"


@dataclass
class TranscriptionJob:
    frame_data: bytes
    sample_rate: int
    sample_width: int


class SpacebarLiveTranscriber:
    def __init__(self) -> None:
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set")

        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recording = False
        self._frames = bytearray()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._capture_thread: threading.Thread | None = None
        self._segment_thread: threading.Thread | None = None
        self._source_cm: sr.Microphone | None = None
        self._source: sr.Microphone | None = None
        self._processed_bytes = 0
        self._live_segments: list[str] = []
        self._job_queue: queue.Queue[TranscriptionJob | None] = queue.Queue()
        self._worker_thread = threading.Thread(
            target=self._transcription_worker,
            daemon=True,
        )
        self._worker_thread.start()

    def _capture_loop(self) -> None:
        assert self._source is not None
        while not self._stop_event.is_set():
            try:
                chunk = self._source.stream.read(self._source.CHUNK)
            except Exception as e:  # noqa: BLE001
                print(f"[audio] {e}", file=sys.stderr)
                break
            with self._lock:
                self._frames.extend(chunk)

    def _segment_loop(self) -> None:
        assert self._source is not None
        bytes_per_second = self._source.SAMPLE_RATE * self._source.SAMPLE_WIDTH
        segment_bytes = int(bytes_per_second * LIVE_SEGMENT_SECONDS)

        while not self._stop_event.wait(SEGMENT_POLL_SECONDS):
            while True:
                with self._lock:
                    available = len(self._frames) - self._processed_bytes
                    if available < segment_bytes:
                        break
                    start = self._processed_bytes
                    end = start + segment_bytes
                    segment = bytes(self._frames[start:end])
                    self._processed_bytes = end

                self._job_queue.put(
                    TranscriptionJob(
                        frame_data=segment,
                        sample_rate=self._source.SAMPLE_RATE,
                        sample_width=self._source.SAMPLE_WIDTH,
                    )
                )

    def _recognize(self, frame_data: bytes, sample_rate: int, sample_width: int) -> str:
        audio = sr.AudioData(frame_data, sample_rate, sample_width)
        return self.recognizer.recognize_openai(audio, model=MODEL).strip()

    def _transcription_worker(self) -> None:
        while True:
            job = self._job_queue.get()
            try:
                if job is None:
                    return

                duration = len(job.frame_data) / (job.sample_rate * job.sample_width)
                if duration < MIN_LIVE_SEGMENT_SECONDS:
                    continue

                try:
                    text = self._recognize(
                        job.frame_data,
                        job.sample_rate,
                        job.sample_width,
                    )
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"❌ live transcription failed: {e}", file=sys.stderr)
                    continue

                if not text:
                    continue

                self._live_segments.append(text)
                print(f"\rLive: {' '.join(self._live_segments)}", end="")
            finally:
                self._job_queue.task_done()

    def start_recording(self) -> None:
        with self._lock:
            if self.recording:
                return
            self._source_cm = sr.Microphone(
                sample_rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE
            )
            self._source = self._source_cm.__enter__()
            self._frames.clear()
            self._processed_bytes = 0
            self._live_segments.clear()
            self._stop_event.clear()
            self.recording = True
            self._capture_thread = threading.Thread(
                target=self._capture_loop, daemon=True
            )
            self._segment_thread = threading.Thread(
                target=self._segment_loop, daemon=True
            )
            self._capture_thread.start()
            self._segment_thread.start()
        print("\n🎙️ Recording... (release space to stop)")

    def stop_recording(self) -> None:
        with self._lock:
            if not self.recording or self._source is None or self._source_cm is None:
                return
            self.recording = False
            self._stop_event.set()
            capture_thread = self._capture_thread
            segment_thread = self._segment_thread
            source_cm = self._source_cm
            source = self._source
            self._capture_thread = None
            self._segment_thread = None
            self._source_cm = None
            self._source = None

        if capture_thread is not None:
            capture_thread.join(timeout=1.0)
        if segment_thread is not None:
            segment_thread.join(timeout=1.0)
        source_cm.__exit__(None, None, None)

        with self._lock:
            frame_data = bytes(self._frames)
            remainder = frame_data[self._processed_bytes :]

        total_seconds = len(frame_data) / (source.SAMPLE_RATE * source.SAMPLE_WIDTH)
        if total_seconds < MIN_DURATION_SECONDS:
            print(
                f"\n⏹️ Recording too short ({total_seconds:.2f}s < {MIN_DURATION_SECONDS:.2f}s)."
            )
            return

        bytes_per_second = source.SAMPLE_RATE * source.SAMPLE_WIDTH
        remainder_seconds = (
            len(remainder) / bytes_per_second if bytes_per_second else 0.0
        )
        if remainder_seconds >= MIN_LIVE_SEGMENT_SECONDS:
            self._job_queue.put(
                TranscriptionJob(
                    frame_data=remainder,
                    sample_rate=source.SAMPLE_RATE,
                    sample_width=source.SAMPLE_WIDTH,
                )
            )
        self._job_queue.join()

        final_text = " ".join(self._live_segments).strip()
        if final_text:
            print(f"\n✅ Final: {final_text}\n")

    def shutdown(self) -> None:
        self.stop_recording()
        self._job_queue.put(None)
        if self._worker_thread.is_alive():
            self._worker_thread.join()


def main() -> int:
    print("Press Space to record, release to stop. Press Ctrl+C or Esc to exit.")
    transcriber = SpacebarLiveTranscriber()
    stop_requested = threading.Event()
    ctrl_down = False

    def request_stop() -> None:
        if stop_requested.is_set():
            return
        stop_requested.set()
        transcriber.shutdown()

    def on_press(key) -> None:
        nonlocal ctrl_down
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            ctrl_down = True
            return
        if ctrl_down and getattr(key, "char", None) == "c":
            request_stop()
            return
        if key == keyboard.Key.space:
            transcriber.start_recording()

    def on_release(key):
        nonlocal ctrl_down
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            ctrl_down = False
            return None
        if key == keyboard.Key.space:
            transcriber.stop_recording()
        if key == keyboard.Key.esc:
            request_stop()
            return False
        return None

    def handle_sigint(signum, frame) -> None:
        del signum, frame
        request_stop()

    previous_sigint_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, handle_sigint)

    kwargs = {"on_press": on_press, "on_release": on_release, "suppress": True}
    try:
        listener = keyboard.Listener(**kwargs)
    except TypeError:
        kwargs.pop("suppress")
        print(
            "⚠️ keyboard suppress is unavailable, so pressed spaces may appear in the terminal.",
            file=sys.stderr,
        )
        listener = keyboard.Listener(**kwargs)

    with listener:
        try:
            while listener.is_alive() and not stop_requested.wait(0.1):
                pass
        except KeyboardInterrupt:
            request_stop()
        finally:
            listener.stop()
            signal.signal(signal.SIGINT, previous_sigint_handler)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
