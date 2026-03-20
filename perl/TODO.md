# TODO – Unimplemented Features (Perl Port)

This document summarises the features from the original Python
`SpeechRecognition` library that are **not yet implemented** in this Perl
port, along with guidance for a future contributor or agent.

---

## 1. Offline Recognition Backends

### 1.1 CMU PocketSphinx

Python uses the `pocketsphinx` PyPI package.  In Perl:

- CPAN has no maintained binding for PocketSphinx 5.x.
- **Path forward**: Use `Inline::C` or `FFI::Platypus` to bind against the
  `libpocketsphinx` C library directly.
- Alternatively, shell out to the `pocketsphinx_continuous` command-line tool
  and parse its output.

### 1.2 Vosk

Python uses the `vosk` PyPI package, which wraps `libvosk`.

- CPAN has no Vosk binding.
- **Path forward**: Use `FFI::Platypus` to bind `libvosk.so`, or shell out to
  the `vosk-transcriber` CLI (requires installing the Python `vosk` package
  separately).

### 1.3 OpenAI Whisper (local model)

Python uses `openai-whisper` and `faster-whisper` (CTranslate2).  Both
require heavy ML dependencies unlikely to have pure-Perl equivalents.

- **Path forward**: Shell out to a Python script that runs the model, or use
  the OpenAI/Groq *API* backends (already implemented) instead.

---

## 2. Microphone Improvements

The current `Microphone` implementation shells out to `arecord` (Linux/ALSA)
or `sox rec`.

- **Device selection by index** is not implemented.
- **Windows support** is missing.  Consider using `Audio::PortAudio` from
  CPAN if it is updated to work with modern PortAudio, or shell out to
  PowerShell's `WaveIn` API.
- **macOS support**: `rec` from SoX works on macOS.  Needs testing.

---

## 3. Snowboy Hotword Detection

Python integrates with Snowboy, a C library with Python bindings.

- No CPAN binding exists.
- **Path forward**: Snowboy is largely unmaintained (the company closed).
  Consider using `FFI::Platypus` against the Snowboy `.so`, or replace with
  an alternative wake-word detector.

---

## 4. AssemblyAI Backend

Python's `recognize_assemblyai` uploads a file, starts an async job, and
polls for the result.

- **Status**: Stubbed out; the HTTP mechanics are straightforward using LWP.
- **Path forward**: Implement `Speech::Recognition::Recognizer::AssemblyAI`
  following the same pattern as the other backends.  The polling loop should
  `die` with `TranscriptionNotReady` until the job completes, matching the
  Python behaviour.

---

## 5. Amazon Lex / Amazon Transcribe

Python uses `boto3` (AWS SDK).

- CPAN has `Paws` (the Perl AWS SDK).
- **Path forward**: Implement `Speech::Recognition::Recognizer::Amazon` using
  `Paws::TranscribeService` and `Paws::Lex`.

---

## 6. IBM Watson – URL

The IBM Watson Speech-to-Text endpoint URL changed after the Python library
was written.  The current Perl implementation uses the `us-south` service URL.
A future improvement should accept the instance URL as an argument (it varies
per IBM account).

---

## 7. Google Cloud Speech API

Python uses the `google-cloud-speech` SDK, which wraps gRPC.

- CPAN has no maintained Google Cloud Speech binding.
- **Path forward**: Use the REST API directly with LWP.  The REST endpoint is
  documented at
  https://cloud.google.com/speech-to-text/docs/reference/rest/v1/speech/recognize.
  Authentication requires a service-account JSON key and the `googleapis` OAuth
  flow (implement with LWP + JSON).

---

## 8. High-Quality Sample-Rate Conversion

The current pure-Perl `_ratecv` function uses linear interpolation.  For
production use this may introduce audible artifacts.

- **Path forward**: Shell out to `sox` for resampling, or bind to
  `libsamplerate` via `FFI::Platypus`.

---

## 9. Windows Support

- FLAC encoding/decoding relies on the `flac` command.  The original Python
  library bundles `flac-win32.exe`; this Perl port does not.
- Microphone capture currently only supports ALSA/SoX.

---

## 10. Tests for Online Backends

The test suite (`t/`) does not include integration tests for online backends
(they require real API keys and network access).  Consider adding mock-based
tests using `Test::LWP::UserAgent` or similar.

---

_If you pick this up, please update this file and the `Changes` file as you
complete items._
