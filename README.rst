Speech::Recognition — Perl Library
===================================

A CPAN-compliant Perl library for performing speech recognition, with support
for cloud APIs, local CLI tools, and on-device inference.

This is a fork of `Uberi/speech_recognition <https://github.com/Uberi/speech_recognition>`_,
reimplemented in Perl.  The Perl library in ``perl/`` is the primary focus of
this repository.  The original Python source is preserved in ``python/`` for
reference; see `Differences from the Python original`_ below.

Quick Start
-----------

.. code-block:: perl

    use Speech::Recognition::Recognizer;
    use Speech::Recognition::AudioFile;

    my $r = Speech::Recognition::Recognizer->new;

    my $audio;
    Speech::Recognition::AudioFile->new(filename => 'speech.wav')->with(sub ($src) {
        $audio = $r->record($src);
    });

    # Free Google Speech API (no key required for light use)
    print $r->recognize_google($audio), "\n";

    # OpenAI Whisper API
    print $r->recognize_openai($audio, api_key => $ENV{OPENAI_API_KEY}), "\n";

    # On-device transcription (macOS only, no key or network required)
    print $r->recognize_yap($audio), "\n";

Installation
------------

.. code-block:: bash

    cd perl
    perl Makefile.PL
    make
    make test
    make install

Requires Perl 5.36+.  The only mandatory non-core dependency is
`LWP::UserAgent <https://metacpan.org/pod/LWP::UserAgent>`__ (for HTTP
backends).  Individual backends may require additional modules or system tools
as noted below.

Supported Backends
------------------

Cloud APIs
~~~~~~~~~~

- `Google Speech API v2 <https://cloud.google.com/speech-to-text>`__ — legacy,
  no key required for light use (``recognize_google``)
- `Google Cloud Speech-to-Text <https://cloud.google.com/speech-to-text>`__ —
  paid, higher accuracy, requires a service-account JSON key
  (``recognize_google_cloud``; requires
  `Crypt::OpenSSL::RSA <https://metacpan.org/pod/Crypt::OpenSSL::RSA>`__)
- `Wit.ai <https://wit.ai/>`__ — free with sign-up (``recognize_wit``)
- `Microsoft Azure Speech <https://azure.microsoft.com/en-us/products/ai-services/speech-to-text>`__ (``recognize_azure``)
- `Microsoft Bing Speech <https://www.microsoft.com/cognitive-services/en-us/speech-api>`__ — legacy, deprecated (``recognize_bing``)
- `Houndify <https://houndify.com/>`__ (``recognize_houndify``)
- `IBM Watson Speech to Text <https://www.ibm.com/products/speech-to-text>`__ (``recognize_ibm``)
- `OpenAI Whisper API <https://platform.openai.com/docs/guides/speech-to-text>`__ —
  ``whisper-1``, ``gpt-4o-transcribe``, ``gpt-4o-mini-transcribe``
  (``recognize_openai``; key via ``OPENAI_API_KEY``)
- `Groq Whisper API <https://console.groq.com/docs/speech-to-text>`__ —
  fast inference for ``whisper-large-v3-turbo`` and ``whisper-large-v3``
  (``recognize_groq``; key via ``GROQ_API_KEY``)
- `AssemblyAI <https://www.assemblyai.com/>`__ — async upload-and-poll
  (``recognize_assemblyai``; key via ``api_token`` argument)

Local / Offline
~~~~~~~~~~~~~~~

- `OpenAI Whisper CLI <https://github.com/openai/whisper>`__ — ``pip install openai-whisper``
  (``recognize_whisper_local``)
- `whisper.cpp <https://github.com/ggerganov/whisper.cpp>`__ — C++ reimplementation,
  no Python required; Metal/CUDA acceleration supported
  (``recognize_whisper_local``, auto-detected alongside the Python CLI)
- `Yap <https://github.com/finnvoor/yap>`__ — **macOS only**; uses Apple's
  on-device Speech framework via the Neural Engine; no API key or network
  connection required.  ``brew install yap``  (``recognize_yap``)

Response Formats
----------------

The local backends (Whisper CLI, Yap) and the OpenAI/Groq cloud APIs all
accept a ``response_format`` argument using the OpenAI API vocabulary:

=============================  ================================================
``json`` (default for Whisper) JSON object with a ``text`` field
``verbose_json``               JSON with per-segment timestamps and metadata
``text``                       Plain transcript string (default for Yap)
``srt``                        SubRip subtitle file with timestamps
``vtt``                        WebVTT subtitle file with timestamps
=============================  ================================================

.. code-block:: perl

    # SRT captions from local Whisper
    my $srt = $r->recognize_whisper_local($audio,
        model           => 'base',
        response_format => 'srt',
    );

    # SRT captions on-device via Yap (macOS)
    my $srt = $r->recognize_yap($audio,
        response_format => 'srt',
        language        => 'en-US',
    );

Audio Sources
-------------

- ``Speech::Recognition::AudioFile`` — WAV (PCM), AIFF/AIFF-C, and FLAC files.
  Stereo is automatically downmixed to mono.  FLAC requires the ``flac``
  command-line tool (``apt-get install flac`` / ``brew install flac``).
- ``Speech::Recognition::Microphone`` — live microphone input via ``arecord``
  (Linux/ALSA) or ``rec`` from `SoX <https://sox.sourceforge.net/>`__.

Sample-rate conversion uses ``sox`` when available, falling back to pure-Perl
linear interpolation.

Example Audio Files
-------------------

``examples/english.wav``, ``examples/french.aiff``, and ``examples/chinese.flac``
are included.  To run a live transcription demo against all three::

    cd perl
    perl try_transcribe.pl

Tests
-----

.. code-block:: bash

    cd perl
    prove -l t/

The test suite includes unit tests for audio parsing, mock-HTTP tests for all
cloud backends (using ``Test::LWP::UserAgent``), and local-backend tests that
stub the CLI layer.  No API keys or network access are required to run the
suite.

Differences from the Python Original
-------------------------------------

This Perl port diverges from the upstream Python library in the following ways:

**Added**

- ``recognize_yap`` — macOS on-device transcription via
  `Yap <https://github.com/finnvoor/yap>`__ (Apple Speech framework).
  There is no Python equivalent.
- ``response_format`` parameter for local backends (``recognize_whisper_local``,
  ``recognize_yap``) supporting ``json``, ``verbose_json``, ``text``, ``srt``,
  ``vtt``.
- ``recognize_assemblyai`` — AssemblyAI async upload-and-poll backend.
- ``recognize_google_cloud`` — Google Cloud Speech-to-Text V1 REST backend
  with JWT/OAuth2 authentication (no ``google-cloud-speech`` SDK dependency).

**Not yet implemented**

- CMU PocketSphinx offline recognition — no maintained Perl binding exists;
  see ``perl/TODO.md`` for the planned ``FFI::Platypus`` path.
- Vosk offline recognition — same situation.
- Snowboy hotword detection — the Snowboy project is unmaintained.
- Faster-Whisper (``recognize_faster_whisper``) — CTranslate2 has no Perl path;
  use ``recognize_whisper_local`` with ``whisper-cpp`` for comparable speed.
- Windows microphone support.

**Changed**

- FLAC encoding always uses the system ``flac`` binary; no bundled executables.
- Microphone capture shells out to ``arecord`` or ``sox rec`` instead of PyAudio.
- Sample-rate conversion delegates to ``sox`` when present instead of
  ``audioop``.
- Python 3.13 removed the ``aifc`` stdlib module, breaking AIFF support in
  current ``SpeechRecognition`` releases.  This Perl port parses AIFF natively
  and is unaffected.

Original Python Library
-----------------------

The upstream Python ``SpeechRecognition`` library was created by
`Anthony Zhang (Uberi) <https://github.com/Uberi>`__ and is available at
`github.com/Uberi/speech_recognition <https://github.com/Uberi/speech_recognition>`__.

The Python source is preserved in ``python/`` for reference.

License
-------

BSD 3-Clause License.  See ``LICENSE.txt``.

The Perl port is based on the Python ``SpeechRecognition`` library,
copyright 2014– Anthony Zhang (Uberi).
