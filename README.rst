SpeechRecognition
=================

.. image:: https://img.shields.io/pypi/v/SpeechRecognition.svg
    :target: https://pypi.python.org/pypi/SpeechRecognition/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/SpeechRecognition.svg
    :target: https://pypi.python.org/pypi/SpeechRecognition/
    :alt: Development Status

.. image:: https://img.shields.io/pypi/pyversions/SpeechRecognition.svg
    :target: https://pypi.python.org/pypi/SpeechRecognition/
    :alt: Supported Python Versions

.. image:: https://img.shields.io/pypi/l/SpeechRecognition.svg
    :target: https://pypi.python.org/pypi/SpeechRecognition/
    :alt: License

.. image:: https://api.travis-ci.org/Uberi/speech_recognition.svg?branch=master
    :target: https://travis-ci.org/Uberi/speech_recognition
    :alt: Continuous Integration Test Results

Library for performing speech recognition, with support for several engines and APIs, online and offline.

**UPDATE 2022-02-09**: Hey everyone! This project started as a tech demo, but these days it needs more time than I have to keep up with all the PRs and issues. Therefore, I'd like to put out an **open invite for collaborators** - just reach out at me@anthonyz.ca if you're interested!

Speech recognition engine/API support:

* `CMU Sphinx <http://cmusphinx.sourceforge.net/wiki/>`__ (works offline)
* Google Speech Recognition
* `Google Cloud Speech API <https://cloud.google.com/speech/>`__
* `Wit.ai <https://wit.ai/>`__
* `Microsoft Azure Speech <https://azure.microsoft.com/en-us/services/cognitive-services/speech/>`__
* `Microsoft Bing Voice Recognition (Deprecated) <https://www.microsoft.com/cognitive-services/en-us/speech-api>`__
* `Houndify API <https://houndify.com/>`__
* `IBM Speech to Text <http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/speech-to-text.html>`__
* `Snowboy Hotword Detection <https://snowboy.kitt.ai/>`__ (works offline)
* `Tensorflow <https://www.tensorflow.org/>`__
* `Vosk API <https://github.com/alphacep/vosk-api/>`__ (works offline)
* `OpenAI whisper <https://github.com/openai/whisper>`__ (works offline)
* `OpenAI Whisper API <https://platform.openai.com/docs/guides/speech-to-text>`__
* `Groq Whisper API <https://console.groq.com/docs/speech-text>`__

**Quickstart:** ``pip install SpeechRecognition``. See the "Installing" section for more details.

To quickly try it out, run ``python -m speech_recognition`` after installing.

Project links:

-  `PyPI <https://pypi.python.org/pypi/SpeechRecognition/>`__
-  `Source code <https://github.com/Uberi/speech_recognition>`__
-  `Issue tracker <https://github.com/Uberi/speech_recognition/issues>`__

Library Reference
-----------------

The `library reference <https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst>`__ documents every publicly accessible object in the library. This document is also included under ``reference/library-reference.rst``.

See `Notes on using PocketSphinx <https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst>`__ for information about installing languages, compiling PocketSphinx, and building language packs from online resources. This document is also included under ``reference/pocketsphinx.rst``.

You have to install Vosk models for using Vosk. `Here <https://alphacephei.com/vosk/models>`__ are models avaiable. You have to place them in models folder of your project, like "your-project-folder/models/your-vosk-model"

Examples
--------

See the ``examples/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/examples>`__ in the repository root for usage examples:

-  `Recognize speech input from the microphone <https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py>`__
-  `Transcribe an audio file <https://github.com/Uberi/speech_recognition/blob/master/examples/audio_transcribe.py>`__
-  `Save audio data to an audio file <https://github.com/Uberi/speech_recognition/blob/master/examples/write_audio.py>`__
-  `Show extended recognition results <https://github.com/Uberi/speech_recognition/blob/master/examples/extended_results.py>`__
-  `Calibrate the recognizer energy threshold for ambient noise levels <https://github.com/Uberi/speech_recognition/blob/master/examples/calibrate_energy_threshold.py>`__ (see ``recognizer_instance.energy_threshold`` for details)
-  `Listening to a microphone in the background <https://github.com/Uberi/speech_recognition/blob/master/examples/background_listening.py>`__
-  `Various other useful recognizer features <https://github.com/Uberi/speech_recognition/blob/master/examples/special_recognizer_features.py>`__

Installing
----------

First, make sure you have all the requirements listed in the "Requirements" section. 

The easiest way to install this is using ``pip install SpeechRecognition``.

Otherwise, download the source distribution from `PyPI <https://pypi.python.org/pypi/SpeechRecognition/>`__, and extract the archive.

In the folder, run ``python setup.py install``.

Requirements
------------

To use all of the functionality of the library, you should have:

* **Python** 3.9+ (required)
* **PyAudio** 0.2.11+ (required only if you need to use microphone input, ``Microphone``)
* **PocketSphinx** (required only if you need to use the Sphinx recognizer, ``recognizer_instance.recognize_sphinx``)
* **Google API Client Library for Python** (required only if you need to use the Google Cloud Speech API, ``recognizer_instance.recognize_google_cloud``)
* **FLAC encoder** (required only if the system is not x86-based Windows/Linux/OS X)
* **Vosk** (required only if you need to use Vosk API speech recognition ``recognizer_instance.recognize_vosk``)
* **Whisper** (required only if you need to use Whisper ``recognizer_instance.recognize_whisper``)
* **Faster Whisper** (required only if you need to use Faster Whisper ``recognizer_instance.recognize_faster_whisper``)
* **openai** (required only if you need to use OpenAI Whisper API speech recognition ``recognizer_instance.recognize_openai``)
* **groq** (required only if you need to use Groq Whisper API speech recognition ``recognizer_instance.recognize_groq``)

The following requirements are optional, but can improve or extend functionality in some situations:

* If using CMU Sphinx, you may want to `install additional language packs <https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst#installing-other-languages>`__ to support languages like International French or Mandarin Chinese.

The following sections go over the details of each requirement.

Python
~~~~~~

The first software requirement is `Python 3.9+ <https://www.python.org/downloads/>`__. This is required to use the library.

PyAudio (for microphone users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`PyAudio <http://people.csail.mit.edu/hubert/pyaudio/#downloads>`__ is required if and only if you want to use microphone input (``Microphone``). PyAudio version 0.2.11+ is required, as earlier versions have known memory management bugs when recording from microphones in certain situations.

If not installed, everything in the library will still work, except attempting to instantiate a ``Microphone`` object will raise an ``AttributeError``.

The installation instructions on the PyAudio website are quite good - for convenience, they are summarized below:

* On Windows, install with PyAudio using `Pip <https://pip.readthedocs.org/>`__: execute ``pip install SpeechRecognition[audio]`` in a terminal.
* On Debian-derived Linux distributions (like Ubuntu and Mint), install PyAudio using `APT <https://wiki.debian.org/Apt>`__: execute ``sudo apt-get install python-pyaudio python3-pyaudio`` in a terminal.
    * If the version in the repositories is too old, install the latest release using Pip: execute ``sudo apt-get install portaudio19-dev python-all-dev python3-all-dev && sudo pip install SpeechRecognition[audio]`` (replace ``pip`` with ``pip3`` if using Python 3).
* On OS X, install PortAudio using `Homebrew <http://brew.sh/>`__: ``brew install portaudio``. Then, install with PyAudio using `Pip <https://pip.readthedocs.org/>`__: ``pip install SpeechRecognition[audio]``.
* On other POSIX-based systems, install the ``portaudio19-dev`` and ``python-all-dev`` (or ``python3-all-dev`` if using Python 3) packages (or their closest equivalents) using a package manager of your choice, and then install with PyAudio using `Pip <https://pip.readthedocs.org/>`__: ``pip install SpeechRecognition[audio]`` (replace ``pip`` with ``pip3`` if using Python 3).

PyAudio `wheel packages <https://pypi.python.org/pypi/wheel>`__ for common 64-bit Python versions on Windows and Linux are included for convenience, under the ``third-party/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/third-party>`__ in the repository root. To install, simply run ``pip install wheel`` followed by ``pip install ./third-party/WHEEL_FILENAME`` (replace ``pip`` with ``pip3`` if using Python 3) in the repository `root directory <https://github.com/Uberi/speech_recognition>`__.

PocketSphinx-Python (for Sphinx users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`PocketSphinx-Python <https://github.com/bambocher/pocketsphinx-python>`__ is **required if and only if you want to use the Sphinx recognizer** (``recognizer_instance.recognize_sphinx``).

PocketSphinx-Python `wheel packages <https://pypi.python.org/pypi/wheel>`__ for 64-bit Python 3.4, and 3.5 on Windows are included for convenience, under the ``third-party/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/third-party>`__. To install, simply run ``pip install wheel`` followed by ``pip install ./third-party/WHEEL_FILENAME`` (replace ``pip`` with ``pip3`` if using Python 3) in the SpeechRecognition folder.

On Linux and other POSIX systems (such as OS X), run ``pip install SpeechRecognition[pocketsphinx]``. Follow the instructions under "Building PocketSphinx-Python from source" in `Notes on using PocketSphinx <https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst>`__ for installation instructions.

Note that the versions available in most package repositories are outdated and will not work with the bundled language data. Using the bundled wheel packages or building from source is recommended.

See `Notes on using PocketSphinx <https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst>`__ for information about installing languages, compiling PocketSphinx, and building language packs from online resources. This document is also included under ``reference/pocketsphinx.rst``.

Vosk (for Vosk users)
~~~~~~~~~~~~~~~~~~~~~
Vosk API is **required if and only if you want to use Vosk recognizer** (``recognizer_instance.recognize_vosk``).

You can install it with ``python3 -m pip install vosk``.

You also have to install Vosk Models:

`Here <https://alphacephei.com/vosk/models>`__ are models avaiable for download. You have to place them in models folder of your project, like "your-project-folder/models/your-vosk-model"

Google Cloud Speech Library for Python (for Google Cloud Speech-to-Text API users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The library `google-cloud-speech <https://pypi.org/project/google-cloud-speech/>`__ is **required if and only if you want to use Google Cloud Speech-to-Text API** (``recognizer_instance.recognize_google_cloud``).
You can install it with ``python3 -m pip install SpeechRecognition[google-cloud]``.
(ref: `official installation instructions <https://cloud.google.com/speech-to-text/docs/transcribe-client-libraries#client-libraries-install-python>`__)

**Prerequisite**: Create local authentication credentials for your Google account

* Digest: `Before you begin (Transcribe speech to text by using client libraries) <https://cloud.google.com/speech-to-text/docs/transcribe-client-libraries#before-you-begin>`__
* `Set up Speech-to-Text <https://cloud.google.com/speech-to-text/docs/before-you-begin>`__
* `User credentials (Set up ADC for a local development environment) <https://cloud.google.com/docs/authentication/set-up-adc-local-dev-environment#local-user-cred>`__

Currently only `V1 <https://cloud.google.com/speech-to-text/docs/quickstart>`__ is supported. (`V2 <https://cloud.google.com/speech-to-text/v2/docs/quickstart>`__ is not supported)

FLAC (for some systems)
~~~~~~~~~~~~~~~~~~~~~~~

A `FLAC encoder <https://xiph.org/flac/>`__ is required to encode the audio data to send to the API. If using Windows (x86 or x86-64), OS X (Intel Macs only, OS X 10.6 or higher), or Linux (x86 or x86-64), this is **already bundled with this library - you do not need to install anything**.

Otherwise, ensure that you have the ``flac`` command line tool, which is often available through the system package manager. For example, this would usually be ``sudo apt-get install flac`` on Debian-derivatives, or ``brew install flac`` on OS X with Homebrew.

Whisper (for Whisper users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Whisper is **required if and only if you want to use whisper** (``recognizer_instance.recognize_whisper``).

You can install it with ``python3 -m pip install SpeechRecognition[whisper-local]``.

Faster Whisper (for Faster Whisper users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The library `faster-whisper <https://pypi.org/project/faster-whisper/>`__ is **required if and only if you want to use Faster Whisper** (``recognizer_instance.recognize_faster_whisper``).

You can install it with ``python3 -m pip install SpeechRecognition[faster-whisper]``.

OpenAI Whisper API (for OpenAI Whisper API users) 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The library `openai <https://pypi.org/project/openai/>`__ is **required if and only if you want to use OpenAI Whisper API** (``recognizer_instance.recognize_openai``).

You can install it with ``python3 -m pip install SpeechRecognition[openai]``.

Please set the environment variable ``OPENAI_API_KEY`` before calling ``recognizer_instance.recognize_openai``.

Groq Whisper API (for Groq Whisper API users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The library `groq <https://pypi.org/project/groq/>`__ is **required if and only if you want to use Groq Whisper API** (``recognizer_instance.recognize_groq``).

You can install it with ``python3 -m pip install SpeechRecognition[groq]``.

Please set the environment variable ``GROQ_API_KEY`` before calling ``recognizer_instance.recognize_groq``.

Troubleshooting
---------------

The recognizer tries to recognize speech even when I'm not speaking, or after I'm done speaking.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try increasing the ``recognizer_instance.energy_threshold`` property. This is basically how sensitive the recognizer is to when recognition should start. Higher values mean that it will be less sensitive, which is useful if you are in a loud room.

This value depends entirely on your microphone or audio data. There is no one-size-fits-all value, but good values typically range from 50 to 4000.

Also, check on your microphone volume settings. If it is too sensitive, the microphone may be picking up a lot of ambient noise. If it is too insensitive, the microphone may be rejecting speech as just noise.

The recognizer can't recognize speech right after it starts listening for the first time.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``recognizer_instance.energy_threshold`` property is probably set to a value that is too high to start off with, and then being adjusted lower automatically by dynamic energy threshold adjustment. Before it is at a good level, the energy threshold is so high that speech is just considered ambient noise.

The solution is to decrease this threshold, or call ``recognizer_instance.adjust_for_ambient_noise`` beforehand, which will set the threshold to a good value automatically.

The recognizer doesn't understand my particular language/dialect.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try setting the recognition language to your language/dialect. To do this, see the documentation for ``recognizer_instance.recognize_sphinx``, ``recognizer_instance.recognize_google``, ``recognizer_instance.recognize_wit``, ``recognizer_instance.recognize_bing``, ``recognizer_instance.recognize_api``, ``recognizer_instance.recognize_houndify``, and ``recognizer_instance.recognize_ibm``.

For example, if your language/dialect is British English, it is better to use ``"en-GB"`` as the language rather than ``"en-US"``.

The recognizer hangs on ``recognizer_instance.listen``; specifically, when it's calling ``Microphone.MicrophoneStream.read``.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This usually happens when you're using a Raspberry Pi board, which doesn't have audio input capabilities by itself. This causes the default microphone used by PyAudio to simply block when we try to read it. If you happen to be using a Raspberry Pi, you'll need a USB sound card (or USB microphone).

Once you do this, change all instances of ``Microphone()`` to ``Microphone(device_index=MICROPHONE_INDEX)``, where ``MICROPHONE_INDEX`` is the hardware-specific index of the microphone.

To figure out what the value of ``MICROPHONE_INDEX`` should be, run the following code:

.. code:: python

    import speech_recognition as sr
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))

This will print out something like the following:

::

    Microphone with name "HDA Intel HDMI: 0 (hw:0,3)" found for `Microphone(device_index=0)`
    Microphone with name "HDA Intel HDMI: 1 (hw:0,7)" found for `Microphone(device_index=1)`
    Microphone with name "HDA Intel HDMI: 2 (hw:0,8)" found for `Microphone(device_index=2)`
    Microphone with name "Blue Snowball: USB Audio (hw:1,0)" found for `Microphone(device_index=3)`
    Microphone with name "hdmi" found for `Microphone(device_index=4)`
    Microphone with name "pulse" found for `Microphone(device_index=5)`
    Microphone with name "default" found for `Microphone(device_index=6)`

Now, to use the Snowball microphone, you would change ``Microphone()`` to ``Microphone(device_index=3)``.

Calling ``Microphone()`` gives the error ``IOError: No Default Input Device Available``.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As the error says, the program doesn't know which microphone to use.

To proceed, either use ``Microphone(device_index=MICROPHONE_INDEX, ...)`` instead of ``Microphone(...)``, or set a default microphone in your OS. You can obtain possible values of ``MICROPHONE_INDEX`` using the code in the troubleshooting entry right above this one.

The program doesn't run when compiled with `PyInstaller <https://github.com/pyinstaller/pyinstaller/wiki>`__.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of PyInstaller version 3.0, SpeechRecognition is supported out of the box. If you're getting weird issues when compiling your program using PyInstaller, simply update PyInstaller.

You can easily do this by running ``pip install --upgrade pyinstaller``.

On Ubuntu/Debian, I get annoying output in the terminal saying things like "bt_audio_service_open: [...] Connection refused" and various others.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The "bt_audio_service_open" error means that you have a Bluetooth audio device, but as a physical device is not currently connected, we can't actually use it - if you're not using a Bluetooth microphone, then this can be safely ignored. If you are, and audio isn't working, then double check to make sure your microphone is actually connected. There does not seem to be a simple way to disable these messages.

For errors of the form "ALSA lib [...] Unknown PCM", see `this StackOverflow answer <http://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time>`__. Basically, to get rid of an error of the form "Unknown PCM cards.pcm.rear", simply comment out ``pcm.rear cards.pcm.rear`` in ``/usr/share/alsa/alsa.conf``, ``~/.asoundrc``, and ``/etc/asound.conf``.

For "jack server is not running or cannot be started" or "connect(2) call to /dev/shm/jack-1000/default/jack_0 failed (err=No such file or directory)" or "attempt to connect to server failed", these are caused by ALSA trying to connect to JACK, and can be safely ignored. I'm not aware of any simple way to turn those messages off at this time, besides `entirely disabling printing while starting the microphone <https://github.com/Uberi/speech_recognition/issues/182#issuecomment-266256337>`__.

On OS X, I get a ``ChildProcessError`` saying that it couldn't find the system FLAC converter, even though it's installed.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installing `FLAC for OS X <https://xiph.org/flac/download.html>`__ directly from the source code will not work, since it doesn't correctly add the executables to the search path.

Installing FLAC using `Homebrew <http://brew.sh/>`__ ensures that the search path is correctly updated. First, ensure you have Homebrew, then run ``brew install flac`` to install the necessary files.

Developing
----------

To hack on this library, first make sure you have all the requirements listed in the "Requirements" section.

-  Most of the library code lives in ``speech_recognition/__init__.py``.
-  Examples live under the ``examples/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/examples>`__, and the demo script lives in ``speech_recognition/__main__.py``.
-  The FLAC encoder binaries are in the ``speech_recognition/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/speech_recognition>`__.
-  Documentation can be found in the ``reference/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/reference>`__.
-  Third-party libraries, utilities, and reference material are in the ``third-party/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/third-party>`__.

To install/reinstall the library locally, run ``python -m pip install -e .[dev]`` in the project `root directory <https://github.com/Uberi/speech_recognition>`__.

Before a release, the version number is bumped in ``README.rst`` and ``speech_recognition/__init__.py``. Version tags are then created using ``git config gpg.program gpg2 && git config user.signingkey DB45F6C431DE7C2DCD99FF7904882258A4063489 && git tag -s VERSION_GOES_HERE -m "Version VERSION_GOES_HERE"``.

Releases are done by running ``make-release.sh VERSION_GOES_HERE`` to build the Python source packages, sign them, and upload them to PyPI.

Testing
~~~~~~~

Prerequisite: `Install pipx <https://pipx.pypa.io/stable/installation/>`__.

To run all the tests:

.. code:: bash

    python -m unittest discover --verbose

To run static analysis:

.. code:: bash

    make lint

To ensure RST is well-formed:

.. code:: bash

    make rstcheck

Testing is also done automatically by GitHub Actions, upon every push.

FLAC Executables
~~~~~~~~~~~~~~~~

The included ``flac-win32`` executable is the `official FLAC 1.3.2 32-bit Windows binary <http://downloads.xiph.org/releases/flac/flac-1.3.2-win.zip>`__.

The included ``flac-linux-x86`` and ``flac-linux-x86_64`` executables are built from the `FLAC 1.3.2 source code <http://downloads.xiph.org/releases/flac/flac-1.3.2.tar.xz>`__ with `Manylinux <https://github.com/pypa/manylinux>`__ to ensure that it's compatible with a wide variety of distributions.

The built FLAC executables should be bit-for-bit reproducible. To rebuild them, run the following inside the project directory on a Debian-like system:

.. code:: bash

    # download and extract the FLAC source code
    cd third-party
    sudo apt-get install --yes docker.io

    # build FLAC inside the Manylinux i686 Docker image
    tar xf flac-1.3.2.tar.xz
    sudo docker run --tty --interactive --rm --volume "$(pwd):/root" quay.io/pypa/manylinux1_i686:latest bash
        cd /root/flac-1.3.2
        ./configure LDFLAGS=-static # compiler flags to make a static build
        make
    exit
    cp flac-1.3.2/src/flac/flac ../speech_recognition/flac-linux-x86 && sudo rm -rf flac-1.3.2/

    # build FLAC inside the Manylinux x86_64 Docker image
    tar xf flac-1.3.2.tar.xz
    sudo docker run --tty --interactive --rm --volume "$(pwd):/root" quay.io/pypa/manylinux1_x86_64:latest bash
        cd /root/flac-1.3.2
        ./configure LDFLAGS=-static # compiler flags to make a static build
        make
    exit
    cp flac-1.3.2/src/flac/flac ../speech_recognition/flac-linux-x86_64 && sudo rm -r flac-1.3.2/

The included ``flac-mac`` executable is extracted from `xACT 2.39 <http://xact.scottcbrown.org/>`__, which is a frontend for FLAC 1.3.2 that conveniently includes binaries for all of its encoders. Specifically, it is a copy of ``xACT 2.39/xACT.app/Contents/Resources/flac`` in ``xACT2.39.zip``.

Authors
-------

::

    Uberi <me@anthonyz.ca> (Anthony Zhang)
    bobsayshilol
    arvindch <achembarpu@gmail.com> (Arvind Chembarpu)
    kevinismith <kevin_i_smith@yahoo.com> (Kevin Smith)
    haas85
    DelightRun <changxu.mail@gmail.com>
    maverickagm
    kamushadenes <kamushadenes@hyadesinc.com> (Kamus Hadenes)
    sbraden <braden.sarah@gmail.com> (Sarah Braden)
    tb0hdan (Bohdan Turkynewych)
    Thynix <steve@asksteved.com> (Steve Dougherty)
    beeedy <broderick.carlin@gmail.com> (Broderick Carlin)

Please report bugs and suggestions at the `issue tracker <https://github.com/Uberi/speech_recognition/issues>`__!

How to cite this library (APA style):

    Zhang, A. (2017). Speech Recognition (Version 3.11) [Software]. Available from https://github.com/Uberi/speech_recognition#readme.

How to cite this library (Chicago style):

    Zhang, Anthony. 2017. *Speech Recognition* (version 3.11).

Also check out the `Python Baidu Yuyin API <https://github.com/DelightRun/PyBaiduYuyin>`__, which is based on an older version of this project, and adds support for `Baidu Yuyin <http://yuyin.baidu.com/>`__. Note that Baidu Yuyin is only available inside China.

License
-------

Copyright 2014- `Anthony Zhang (Uberi) <http://anthonyz.ca/>`__. The source code for this library is available online at `GitHub <https://github.com/Uberi/speech_recognition>`__.

SpeechRecognition is made available under the 3-clause BSD license. See ``LICENSE.txt`` in the project's `root directory <https://github.com/Uberi/speech_recognition>`__ for more information.

For convenience, all the official distributions of SpeechRecognition already include a copy of the necessary copyright notices and licenses. In your project, you can simply **say that licensing information for SpeechRecognition can be found within the SpeechRecognition README, and make sure SpeechRecognition is visible to users if they wish to see it**.

SpeechRecognition distributes source code, binaries, and language files from `CMU Sphinx <http://cmusphinx.sourceforge.net/>`__. These files are BSD-licensed and redistributable as long as copyright notices are correctly retained. See ``speech_recognition/pocketsphinx-data/*/LICENSE*.txt`` and ``third-party/LICENSE-Sphinx.txt`` for license details for individual parts.

SpeechRecognition distributes source code and binaries from `PyAudio <http://people.csail.mit.edu/hubert/pyaudio/>`__. These files are MIT-licensed and redistributable as long as copyright notices are correctly retained. See ``third-party/LICENSE-PyAudio.txt`` for license details.

SpeechRecognition distributes binaries from `FLAC <https://xiph.org/flac/>`__ - ``speech_recognition/flac-win32.exe``, ``speech_recognition/flac-linux-x86``, and ``speech_recognition/flac-mac``. These files are GPLv2-licensed and redistributable, as long as the terms of the GPL are satisfied. The FLAC binaries are an `aggregate <https://www.gnu.org/licenses/gpl-faq.html#MereAggregation>`__ of `separate programs <https://www.gnu.org/licenses/gpl-faq.html#NFUseGPLPlugins>`__, so these GPL restrictions do not apply to the library or your programs that use the library, only to FLAC itself. See ``LICENSE-FLAC.txt`` for license details.
