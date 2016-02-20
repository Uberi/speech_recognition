Speech Recognition
==================

.. image:: https://img.shields.io/pypi/dm/SpeechRecognition.svg
    :target: https://pypi.python.org/pypi/SpeechRecognition/
    :alt: Downloads

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

Library for performing speech recognition with support for `CMU Sphinx <http://cmusphinx.sourceforge.net/wiki/>`__, Google Speech Recognition, `Wit.ai <https://wit.ai/>`__, `IBM Speech to Text <http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/speech-to-text.html>`__, and `AT&T Speech to Text <http://developer.att.com/apis/speech>`__.

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

Examples
--------

See the ``examples/`` directory for usage examples:

-  `Recognize speech input from the microphone <https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py>`__
-  `Transcribe a WAV audio file <https://github.com/Uberi/speech_recognition/blob/master/examples/wav_transcribe.py>`__
-  `Save audio data to a WAV file <https://github.com/Uberi/speech_recognition/blob/master/examples/write_audio.py>`__
-  `Show extended recognition results <https://github.com/Uberi/speech_recognition/blob/master/examples/extended_results.py>`__
-  `Calibrate the recognizer energy threshold for ambient noise levels <https://github.com/Uberi/speech_recognition/blob/master/examples/calibrate_energy_threshold.py>`__ (see ``recognizer_instance.energy_threshold`` for details)
-  `Listening to a microphone in the background <https://github.com/Uberi/speech_recognition/blob/master/examples/background_listening.py>`__

Installing
----------

First, make sure you have all the requirements listed in the "Requirements" section.

The easiest way to install this is using ``pip install SpeechRecognition``.

Otherwise, download the source distribution from `PyPI <https://pypi.python.org/pypi/SpeechRecognition/>`__, and extract the archive.

In the folder, run ``python setup.py install``.

Requirements
------------

In summary, this library requires:

* **Python** 2.6, 2.7, or 3.3+
* **PyAudio** 0.2.9+ (required only if you need to use microphone input)
* **PocketSphinx** (required only if you need to use the Sphinx recognizer)
* **FLAC encoder** (required only if the system is not x86-based Windows/Linux/OS X)

Python
~~~~~~

The first software requirement is `Python 2.6, 2.7, or Python 3.3+ <https://www.python.org/download/releases/>`__. This is required to use the library.

PyAudio (for microphone users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to use audio input from microphones, `PyAudio <http://people.csail.mit.edu/hubert/pyaudio/#downloads>`__ is also necessary. Version 0.2.9+ is required in order to avoid overflow issues with recording on certain machines.

If not installed, everything in the library will still work, except attempting to instantiate a ``Microphone`` object will throw an ``AttributeError``.

The installation instructions are quite good as of PyAudio v0.2.9. For convenience, they are summarized below:

* On Windows, install PyAudio using `Pip <https://pip.readthedocs.org/>`__: execute ``pip install pyaudio`` in a terminal.
* On Debian-derived Linux distributions (like Ubuntu and Mint), install PyAudio using `APT <https://wiki.debian.org/Apt>`__: execute ``sudo apt-get install python-pyaudio python3-pyaudio`` in a terminal.
    * If the version in the repositories is too old, install the latest release using Pip: execute ``sudo apt-get install portaudio19-dev python-all-dev python3-all-dev && sudo pip install pyaudio`` (replace ``pip`` with ``pip3`` if using Python 3).
* On OS X, install PortAudio using `Homebrew <http://brew.sh/>`__: ``brew install portaudio``. Then, install PyAudio using `Pip <https://pip.readthedocs.org/>`__: ``pip install pyaudio``.
* On other POSIX-based systems, install the ``portaudio19-dev`` and ``python-all-dev`` (or ``python3-all-dev`` if using Python 3) packages (or their closest equivalents) using a package manager of your choice, and then install PyAudio using `Pip <https://pip.readthedocs.org/>`__: ``pip install pyaudio`` (replace ``pip`` with ``pip3`` if using Python 3).

PyAudio `wheel packages <https://pypi.python.org/pypi/wheel>`__ for 64-bit Python 2.7, 3.4, and 3.5 on Windows and Linux are included for convenience, under the ``third-party/`` directory. To install, simply run ``pip install wheel`` followed by ``pip install ./third-party/WHEEL_FILENAME`` (replace ``pip`` with ``pip3`` if using Python 3) in the project root directory.

PocketSphinx-Python (for Sphinx users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`PocketSphinx-Python <https://github.com/bambocher/pocketsphinx-python>`__ is required if and only if you want to use the Sphinx recognizer (``recognizer_instance.recognize_sphinx``).

PocketSphinx-Python `wheel packages <https://pypi.python.org/pypi/wheel>`__ for 64-bit Python 2.7, 3.4, and 3.5 on Windows and Linux are included for convenience, under the ``third-party/`` directory. To install, simply run ``pip install wheel`` followed by ``pip install ./third-party/WHEEL_FILENAME`` (replace ``pip`` with ``pip3`` if using Python 3) in the SpeechRecognition folder.

Note that the versions available in most package repositories are outdated and will not work with the bundled language data. Using the bundled wheel packages or building from source is recommended.

See `Notes on using PocketSphinx <https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst>`__ for information about installing languages, compiling PocketSphinx, and building language packs from online resources. This document is also included under ``reference/pocketsphinx.rst``.

FLAC (for some systems)
~~~~~~~~~~~~~~~~~~~~~~~

A FLAC encoder is required to encode the audio data to send to the API. If using Windows, OS X, or Linux on an i385-compatible architecture, the encoder is already bundled with this library - you do not need to install anything else.

Otherwise, ensure that you have the ``flac`` command line tool, which is often available through the system package manager.

Troubleshooting
---------------

The recognizer tries to recognize speech even when I'm not speaking.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try increasing the ``recognizer_instance.energy_threshold`` property. This is basically how sensitive the recognizer is to when recognition should start. Higher values mean that it will be less sensitive, which is useful if you are in a loud room.

This value depends entirely on your microphone or audio data. There is no one-size-fits-all value, but good values typically range from 50 to 4000.

The recognizer can't recognize speech right after it starts listening for the first time.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``recognizer_instance.energy_threshold`` property is probably set to a value that is too high to start off with, and then being adjusted lower automatically by dynamic energy threshold adjustment. Before it is at a good level, the energy threshold is so high that speech is just considered ambient noise.

The solution is to decrease this threshold, or call ``recognizer_instance.adjust_for_ambient_noise`` beforehand, which will set the threshold to a good value automatically.

The recognizer doesn't understand my particular language/dialect.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try setting the recognition language to your language/dialect. To do this, see the documentation for ``recognizer_instance.recognize_sphinx``, ``recognizer_instance.recognize_google``, ``recognizer_instance.recognize_wit``, ``recognizer_instance.recognize_ibm``, and ``recognizer_instance.recognize_att``.

For example, if your language/dialect is British English, it is better to use ``"en-GB"`` as the language rather than ``"en-US"``.

The code examples throw ``UnicodeEncodeError: 'ascii' codec can't encode character`` when run.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you're using Python 2, and your language uses non-ASCII characters, and the terminal or file-like object you're printing to only supports ASCII, an error is thrown when trying to write non-ASCII characters.

This is because in Python 2, ``recognizer_instance.recognize_sphinx``, ``recognizer_instance.recognize_google``, ``recognizer_instance.recognize_wit``, ``recognizer_instance.recognize_ibm``, and ``recognizer_instance.recognize_att`` return unicode strings (``u"something"``) rather than byte strings (``"something"``). In Python 3, all strings are unicode strings.

To make printing of unicode strings work in Python 2 as well, replace all print statements in your code of the following form:

    .. code:: python

        print SOME_UNICODE_STRING

With the following:

    .. code:: python

        print SOME_UNICODE_STRING.encode("utf8")

This change, however, will prevent the code from working in Python 3.

The program doesn't run when compiled with `PyInstaller <https://github.com/pyinstaller/pyinstaller/wiki>`__.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of PyInstaller version 3.0, SpeechRecognition is supported out of the box. If you're getting weird issues when compiling your program using PyInstaller, simply update PyInstaller.

You can easily do this by running ``pip install --upgrade pyinstaller``.

On Ubuntu/Debian, I get errors like "jack server is not running or cannot be started" or "Cannot lock down [...] byte memory area (Cannot allocate memory)".
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Linux audio stack is pretty fickle. There are a few things that can cause these issues.

First, make sure JACK is installed - to install it, run ``sudo apt-get install multimedia-jack``

You will then want to configure the JACK daemon correctly to avoid that "Cannot allocate memory" error. Run ``sudo dpkg-reconfigure -p high jackd2`` and select "Yes" to do so.

Now, you will want to make sure your current user is in the ``audio`` group. You can add your current user to this group by running ``sudo adduser $(whoami) audio``.

Unfortunately, these changes will require you to reboot before they take effect.

After rebooting, run ``pulseaudio --kill``, followed by ``jack_control start``, to fix the "jack server is not running or cannot be started" error.

On Ubuntu/Debian, I get annoying output in the terminal saying things like "bt_audio_service_open: [...] Connection refused" and various others.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The "bt_audio_service_open" error means that you have a Bluetooth audio device, but as a physical device is not currently connected, we can't actually use it - if you're not using a Bluetooth microphone, then this can be safely ignored. If you are, and audio isn't working, then double check to make sure your microphone is actually connected. There does not seem to be a simple way to disable these messages.

For errors of the form "ALSA lib [...] Unknown PCM", see `this StackOverflow answer <http://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time>`__. Basically, to get rid of an error of the form "Unknown PCM cards.pcm.rear", simply comment out ``pcm.rear cards.pcm.rear`` in ``/usr/share/alsa/alsa.conf``, ``~/.asoundrc``, and ``/etc/asound.conf``.

On OS X, I get a ``ChildProcessError`` saying that it couldn't find the system FLAC converter, even though it's installed.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installing [FLAC for OS X](https://xiph.org/flac/download.html) directly from the source code will not work, since it doesn't correctly add the executables to the search path.

Installing FLAC using [Homebrew](http://brew.sh/) ensures that the search path is correctly updated. First, ensure you have Homebrew, then run ``brew install flac`` to install the necessary files.

Developing
----------

To hack on this library, first make sure you have all the requirements listed in the "Requirements" section.

-  Most of the library code lives in ``speech_recognition/__init__.py``.
-  Examples live under the ``examples/`` directory, and the demo script lives in ``speech_recognition/__main__.py``.
-  The FLAC encoder binaries are in the ``speech_recognition/`` directory.
-  Documentation can be found in the ``reference/`` directory.
-  Third-party libraries, utilities, and reference material are in the ``third-party/`` directory.

To install/reinstall the library locally, run ``python setup.py install`` in the project root directory.

Releases are done by running either ``build.sh`` or ``build.bat``. These are bash and batch scripts, respectively, that automatically build Python source packages and `Python Wheels <http://pythonwheels.com/>`__, then upload them to PyPI.

Features and bugfixes should be tested, at minimum, on Python 2.7 and a recent version of Python 3. It is highly recommended to test new features on Python 2.6, 2.7, 3.3, and the latest version of Python 3.

Authors
-------

::

    Uberi <azhang9@gmail.com> (Anthony Zhang)
    bobsayshilol
    arvindch <achembarpu@gmail.com> (Arvind Chembarpu)
    kevinismith <kevin_i_smith@yahoo.com> (Kevin Smith)
    haas85
    DelightRun <changxu.mail@gmail.com>
    maverickagm

Please report bugs and suggestions at the `issue tracker <https://github.com/Uberi/speech_recognition/issues>`__!

How to cite this library (APA style):

    Zhang, A. (2016). Speech Recognition (Version 3.2) [Software]. Available from https://github.com/Uberi/speech_recognition#readme.

How to cite this library (Chicago style):

    Zhang, Anthony. 2016. *Speech Recognition* (version 3.2).

Also check out the `Python Baidu Yuyin API <https://github.com/DelightRun/PyBaiduYuyin>`__, which is based on an older version of this project, and adds support for `Baidu Yuyin <http://yuyin.baidu.com/>`__.

License
-------

Copyright 2014-2016 `Anthony Zhang (Uberi) <https://uberi.github.io>`__.

The source code is available online at `GitHub <https://github.com/Uberi/speech_recognition>`__.

This program is made available under the 3-clause BSD license. See ``LICENSE.txt`` in the project's root directory for more information.

This program distributes source code, binaries, and language files from `CMU Sphinx <http://cmusphinx.sourceforge.net/>`__. These files are BSD-licensed and redistributable as long as copyright notices are correctly retained. See ``speech_recognition/pocketsphinx-data/*/LICENSE*.txt`` and ``third-party/LICENSE-Sphinx.txt`` for details concerning individual files.

This program distributes source code and binaries from `PyAudio <http://people.csail.mit.edu/hubert/pyaudio/>`__. These files are MIT-licensed and redistributable as long as copyright notices are correctly retained. See license files inside ``third-party/LICENSE-PyAudio.txt`` for details concerning individual files.
