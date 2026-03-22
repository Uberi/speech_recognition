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

### ~~1.3 OpenAI Whisper (local model)~~ ✅ DONE

~~Python uses `openai-whisper` and `faster-whisper` (CTranslate2).  Both
require heavy ML dependencies unlikely to have pure-Perl equivalents.~~

**Implemented** in `Speech::Recognition::Recognizer::Whisper`.  Shells out to
the `whisper` CLI (openai-whisper) or `whisper-cpp` binary.  No Python
dependency at runtime.  Throws `SetupError` with installation instructions if
neither binary is found.  Use via `$r->recognize_whisper_local($audio, ...)`.

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

## 3. ~~Snowboy Hotword Detection~~ — DROPPED

~~Python integrates with Snowboy, a C library with Python bindings.~~

Snowboy is **unmaintained** (the company dissolved ~2020) and the binaries are
outdated.  This item is dropped.  Modern alternatives:

- **openWakeWord** — https://github.com/dscripka/openWakeWord
- **Porcupine** (Picovoice) — https://github.com/Picovoice/porcupine

---

## ~~4. AssemblyAI Backend~~ ✅ DONE

**Implemented** in `Speech::Recognition::Recognizer::AssemblyAI`.  Matches the
Python `recognize_assemblyai` behaviour: the first call uploads audio and
throws `TranscriptionNotReady` (with `job_name` set to the transcription ID);
subsequent calls with `audio_data => undef, job_name => $id` poll status,
returning the transcript when complete, re-throwing `TranscriptionNotReady`
while processing, or throwing `TranscriptionFailed` on error.

Use via `$r->recognize_assemblyai($audio, api_token => $token)`.

---

## 5. Amazon Lex / Amazon Transcribe

Python uses `boto3` (AWS SDK).

- CPAN has `Paws` (the Perl AWS SDK).
- **Path forward**: Implement `Speech::Recognition::Recognizer::Amazon` using
  `Paws::TranscribeService` and `Paws::Lex`.

---

## ~~6. IBM Watson – URL~~ ✅ DONE

~~The IBM Watson Speech-to-Text endpoint URL changed after the Python library
was written.  The current Perl implementation uses the `us-south` service URL.
A future improvement should accept the instance URL as an argument (it varies
per IBM account).~~

**Fixed.**  `Speech::Recognition::Recognizer::IBM` now accepts an `endpoint`
argument (default: `https://api.us-south.speech-to-text.watson.cloud.ibm.com`).
Pass your own instance URL to override.

---

## ~~7. Google Cloud Speech API~~ ✅ DONE

~~Python uses the `google-cloud-speech` SDK, which wraps gRPC.~~

**Implemented** in `Speech::Recognition::Recognizer::GoogleCloud`.  Uses the
Speech-to-Text V1 REST API with OAuth2 service-account authentication (RS256
JWT — requires `Crypt::OpenSSL::RSA`).  Supports `language`, `model`,
`use_enhanced`, `preferred_phrases`, `show_all`.

Use via `$r->recognize_google_cloud($audio, credentials_json => $path_or_json)`.

---

## ~~8. High-Quality Sample-Rate Conversion~~ ✅ DONE

~~The current pure-Perl `_ratecv` function uses linear interpolation.  For
production use this may introduce audible artifacts.~~

**Fixed.**  `AudioData::_ratecv` now checks for `sox` on `$PATH` and delegates
resampling to it when available.  Falls back to pure-Perl linear interpolation
when `sox` is absent.

---

## 9. Windows Support

- FLAC encoding/decoding relies on the `flac` command.  The original Python
  library bundles `flac-win32.exe`; this Perl port does not.
- Microphone capture currently only supports ALSA/SoX.

---

## ~~10. Tests for Online Backends~~ ✅ DONE

~~The test suite (`t/`) does not include integration tests for online backends
(they require real API keys and network access).  Consider adding mock-based
tests using `Test::LWP::UserAgent` or similar.~~

**Implemented** in `t/20-backends-mock.t`.  Uses `Test::LWP::UserAgent` to
mock HTTP at the LWP level.  Covers Google, Wit.ai, IBM Watson (including
custom endpoint), OpenAI Whisper, AssemblyAI (submit + poll + error paths),
and Groq — testing success, `show_all`, request errors, and
`UnknownValueError` paths without any real network traffic.

---

## 11. Transcription Output Formats (SRT, VTT, Text)

### ~~11.1 OpenAI Whisper API~~ ✅ DONE

The OpenAI and Groq API backends already accepted `response_format` but the
supported values (C<srt>, C<vtt>, C<verbose_json>) were not documented.
Documentation now explicitly lists all supported values.

### ~~11.2 Local Whisper (openai-whisper / whisper-cpp)~~ ✅ DONE

**Implemented.** `Speech::Recognition::Recognizer::Whisper` now accepts a
`response_format` argument with values `json` (default, backward compatible),
`verbose_json`, `text`, `srt`, and `vtt`.  Both the openai-whisper and
whisper-cpp binaries are fully supported for all formats.

### ~~11.3 Yap (macOS on-device)~~ ✅ DONE

**Implemented.** See section 12 below.

---

## ~~12. Yap — macOS On-Device Transcription~~ ✅ DONE

**Implemented** in `Speech::Recognition::Recognizer::Yap`.  Uses the
[Yap CLI tool](https://github.com/finnvoor/yap) (`brew install yap`) to
transcribe audio entirely on-device via Apple's Speech framework — no API key
or internet connection required.

Supports `response_format` (C<text>, C<srt>, C<vtt>, C<json>, C<verbose_json>)
and `language` (BCP-47 locale string such as C<en-US>).

SRT and VTT output include timestamps, satisfying the downstream consumer that
needs timestamps for paragraph formatting.

Use via `$r->recognize_yap($audio, response_format => 'srt')`.

---


_If you pick this up, please update this file and the `Changes` file as you
complete items._
