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

Library for performing speech recognition with support for Google Speech Recognition, `Wit.ai <https://wit.ai/>`__, `IBM Speech to Text <http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/speech-to-text.html>`__, and `AT&T Speech to Text <http://developer.att.com/apis/speech>`__.

Links:

-  `PyPI <https://pypi.python.org/pypi/SpeechRecognition/>`__
-  `GitHub <https://github.com/Uberi/speech_recognition>`__

Quickstart: ``pip install SpeechRecognition``. See the "Installing" section for more details.

To quickly try it out, run ``python -m speech_recognition`` after installing.

How to cite this library (APA style):

    Zhang, A. (2016). Speech Recognition (Version 3.1) [Software]. Available from https://github.com/Uberi/speech_recognition#readme.

How to cite this library (Chicago style):

    Zhang, Anthony. 2016. *Speech Recognition* (version 3.1).

Also check out the `Python Baidu Yuyin API <https://github.com/DelightRun/PyBaiduYuyin>`__, which is based on an older version of this project, and adds support for `Baidu Yuyin <http://yuyin.baidu.com/>`__.

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

Python
~~~~~~

The first software requirement is `Python 2.6, 2.7, or Python 3.3+ <https://www.python.org/download/releases/>`__. This is required to use the library.

PyAudio (for microphone users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to use audio input from microphones, `PyAudio <http://people.csail.mit.edu/hubert/pyaudio/#downloads>`__ is also necessary. If not installed, the library will still work, but ``Microphone`` will not be defined.

The installation instructions are quite good as of PyAudio v0.2.9. For convenience, they are summarized below:

* On Windows, install PyAudio using `Pip <https://pip.readthedocs.org/>`__: execute ``pip install pyaudio`` in a terminal.
* On Debian-derived Linux distributions (like Ubuntu and Mint), install PyAudio using `APT <https://wiki.debian.org/Apt>`__: execute ``sudo apt-get install python-pyaudio python3-pyaudio`` in a terminal.
    * If you want to use the latest version of PyAudio rather than the version in the repositories, you can install the latest release using Pip: execute ``sudo apt-get install portaudio19-dev python-all-dev python3-all-dev && pip install pyaudio`` (replace ``pip`` with ``pip3`` if using Python 3).
* On OS X, install PortAudio using `Homebrew <http://brew.sh/>`__: ``brew install portaudio``. Then, install PyAudio using `Pip <https://pip.readthedocs.org/>`__: ``pip install pyaudio``.
* On other POSIX-based systems, install the ``portaudio19-dev`` and ``python-all-dev`` (or ``python3-all-dev`` if using Python 3) packages (or their closest equivalents) using a package manager of your choice, and then install PyAudio using `Pip <https://pip.readthedocs.org/>`__: ``pip install pyaudio`` (replace ``pip`` with ``pip3`` if using Python 3).

PyAudio `wheel packages <https://pypi.python.org/pypi/wheel>`__ for 64-bit Python 2.7, 3.4, and 3.5 on Windows and Linux are included for convenience, under the ``third-party/`` directory. To install, simply run ``pip install wheel`` followed by ``pip install ./third-party/WHEEL_FILENAME`` (replace ``pip`` with ``pip3`` if using Python 3) in the SpeechRecognition folder.

PocketSphinx-Python (for Sphinx users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`PocketSphinx-Python <https://github.com/bambocher/pocketsphinx-python>`__ is required if and only if you want to use the Sphinx recognizer (``recognizer_instance.recognize_sphinx``).

PocketSphinx-Python `wheel packages <https://pypi.python.org/pypi/wheel>`__ for 64-bit Python 2.7, 3.4, and 3.5 on Windows and Linux are included for convenience, under the ``third-party/`` directory. To install, simply run ``pip install wheel`` followed by ``pip install ./third-party/WHEEL_FILENAME`` (replace ``pip`` with ``pip3`` if using Python 3) in the SpeechRecognition folder.

Note that the versions available in most package repositories are outdated and will not work with the bundled language data. Using the bundled wheel packages or building from source is recommended.

Installing other languages
^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, SpeechRecognition's Sphinx functionality supports only US English. Additional language packs are also available, but not included due to the files being too large:

* `Metropolitan French <https://db.tt/tVNcZXao>`__
* `Mandarin Chinese <https://db.tt/2YQVXmEk>`__

To install a language pack, download the ZIP archives and extract them directly into the module install directory (you can find the module install directory by running ``python -c "import speech_recognition as sr, os.path as p; print(p.dirname(sr.__file__))"``).

Once installed, you can simply specify the language using the ``language`` parameter of ``recognizer_instance.recognize_sphinx``. For example, French would be specified with ``"fr-FR"`` and Mandarin with ``"zh-CN"``.

Building PocketSphinx-Python from source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* On Windows:
    1. Install `Python <https://www.python.org/downloads/>`__, `Pip <https://pip.pypa.io/en/stable/installing/>`__, `SWIG <http://www.swig.org/download.html>`__, and `Git <https://git-scm.com/downloads>`__, preferably using a package manager.
    2. Install the necessary `compilers suite <http://blog.ionelmc.ro/2014/12/21/compiling-python-extensions-on-windows/>`__ (`here's a PDF version <third-party/Compiling Python extensions on Windows.pdf>`__ in case the link goes down) for compiling modules for your particular Python version:
        * `Microsoft Visual C++ Compiler for Python 2.7 <http://www.microsoft.com/en-us/download/details.aspx?id=44266>`__ for Python 2.7.
        * `Visual Studio 2015 Community Edition <https://www.visualstudio.com/downloads/download-visual-studio-vs>`__ for Python 3.5.
        * The installation process for Python 3.4 is outlined in the article above
    3. Add the folders containing the Python, SWIG, and Git binaries to your ``PATH`` environment variable.
    4. Reboot to apply changes.
    5. If not using Python 2.7, install PocketSphinx using Pip: execute ``pip install pocketsphinx`` in a terminal. Otherwise:
        1. Download the full PocketSphinx-Python source code by running ``git clone --recursive https://github.com/bambocher/pocketsphinx-python``.
        2. Download [msinttypes](https://code.google.com/archive/p/msinttypes/) and copy ``inttypes.h`` and ``stdint.h`` from it into the ``sphinxbase/include/sphinxbase`` folder under the project root folder. This is necessary because the MSVC compiler version used for Python 2.7 is missing a lot of C99 features; msinttypes implements the important ones that Sphinx needs.
        3. Run ``python setup.py install`` to compile and install PocketSphinx.
* On any Debian-derived Linux distributions (like Ubuntu and Mint):
    1. Run ``sudo apt-get install python python-all-dev python-pip build-essential swig git`` for Python 2, or ``sudo apt-get install python3 python3-all-dev python3-pip build-essential swig git`` for Python 3.
    2. Run ``pip install pocketsphinx`` for Python 2, or ``pip3 install pocketsphinx`` for Python 3.
* On other POSIX-based systems:
    1. Install `Python <https://www.python.org/downloads/>`__, `Pip <https://pip.pypa.io/en/stable/installing/>`__, `SWIG <http://www.swig.org/download.html>`__, and `Git <https://git-scm.com/downloads>`__, preferably using a package manager.
    2. Install PocketSphinx-Python using Pip: ``pip install pocketsphinx``.

To build an installable `wheel package <https://pypi.python.org/pypi/wheel>`__ (like the ones included with this project) instead of just installing, run ``git clone --recursive https://github.com/bambocher/pocketsphinx-python && cd pocketsphinx-python && python setup.py bdist_wheel`` instead of ``pip install pocketsphinx``/``python setup.py install``. The resulting Wheel will be found in the ``dist`` folder of the PocketSphinx-Python project directory.

Notes on the structure of the language data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Every language has its own folder under ``/speech_recognition/pocketsphinx-data/LANGUAGE_NAME/``, where ``LANGUAGE_NAME`` is the IETF language tag, like ``"en-US"`` (US English) or ``"en-GB"`` (UK English).
    * For example, the US English data is stored in ``/speech_recognition/pocketsphinx-data/en-US/``.
    * The ``language`` parameter of ``recognizer_instance.recognize_sphinx`` simply chooses the folder with the given name.
* Languages are composed of 3 parts:
    * An acoustic model ``/speech_recognition/pocketsphinx-data/LANGUAGE_NAME/acoustic-model/``, which describes how to interpret audio data.
        * Acoustic models can be downloaded from the `CMU Sphinx files <http://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/>`__. These are pretty disorganized, but instructions for cleaning up specific versions are listed below.
        * All of these should be 16 kHz (broadband) models, since that's what the library will assume is being used.
    * A language model ``/speech_recognition/pocketsphinx-data/LANGUAGE_NAME/language-model.lm.bin`` (in `CMU binary format <http://cmusphinx.sourceforge.net/wiki/tutoriallm#language_models>`__).
    * A pronounciation dictionary ``/speech_recognition/pocketsphinx-data/LANGUAGE_NAME/pronounciation-dictionary.dict``, which describes how words in the language are pronounced.

Notes on building the language data from source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* All of the following points assume a Debian-derived Linux Distibution (like Ubuntu or Mint).
* To work with any complete, real-world languages, you will need quite a bit of RAM (16 GB recommended) and a fair bit of disk space (20 GB recommended).
* `SphinxBase <https://github.com/cmusphinx/sphinxbase>`__ is needed for all language model file format conversions. We use it to convert between ``*.dmp`` DMP files (an obselete Sphinx binary format), ``*.lm`` ARPA files, and Sphinx binary ``*.lm.bin`` files:
    * Install all the SphinxBase build dependencies with ``sudo apt-get install build-essential automake autotools-dev autoconf libtool``.
    * Download and extract the `SphinxBase source code <https://github.com/cmusphinx/sphinxbase/archive/master.zip>`__.
    * Follow the instructions in the README to install SphinxBase. Basically, run ``sh autogen.sh --force && ./configure && make && sudo make install`` in the SphinxBase folder.
* Pruning (getting rid of less important information) is useful if language model files are too large. We can do this using `IRSTLM <https://github.com/irstlm-team/irstlm>`__:
    * Install all the IRSTLM build dependencies with ``sudo apt-get install build-essential automake autotools-dev autoconf libtool``
    * Download and extract the `IRSTLM source code <https://github.com/irstlm-team/irstlm/archive/master.zip>`__.
    * Follow the instructions in the README to install IRSTLM. Basically, run ``sh regenerate-makefiles.sh --force && ./configure && make && sudo make install`` in the IRSTLM folder.
    * If the language model is not in ARPA format, convert it to the ARPA format. To do this, ensure that SphinxBase is installed and run ``sphinx_lm_convert -i LANGUAGE_MODEL_FILE_GOES_HERE -o language-model.lm -ofmt arpa``.
    * Prune the model using IRSTLM: run ``prune-lm --threshold=1e-8 t.lm pruned.lm`` to prune with a threshold of 0.00000001. The higher the threshold, the smaller the resulting file.
    * Convert the model back into binary format if it was originally not in ARPA format. To do this, ensure that SphinxBase is installed and run ``sphinx_lm_convert -i language-model.lm -o LANGUAGE_MODEL_FILE_GOES_HERE``.
* US English: ``/speech_recognition/pocketsphinx-data/en-US/`` is taken directly from the contents of `PocketSphinx's US English model <https://github.com/cmusphinx/pocketsphinx/tree/master/model/en-us>`__.
* Metropolitan French: ``/speech_recognition/pocketsphinx-data/fr-FR/``:
    * ``/speech_recognition/pocketsphinx-data/fr-FR/language-model.lm.bin`` is ``fr-small.lm.bin`` from the `Sphinx French language model <http://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/French%20Language%20Model/>`__.
    * ``/speech_recognition/pocketsphinx-data/fr-FR/pronounciation-dictionary.dict`` is ``fr.dict`` from the `Sphinx French language model <http://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/French%20Language%20Model/>`__.
    * ``/speech_recognition/pocketsphinx-data/fr-FR/acoustic-model/`` is extracted from ``cmusphinx-fr-5.2.tar.gz`` in the `Sphinx French acoustic model <http://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/French/>`__.
    * To get better French recognition accuracy at the expense of higher disk space and RAM usage:
        1. Download ``fr.lm.gmp`` from the `Sphinx French language model <http://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/French%20Language%20Model/>`__.
        2. Convert from DMP (an obselete Sphinx binary format) to ARPA format: ``sphinx_lm_convert -i fr.lm.gmp -o french.lm.bin``.
        3. Replace ``/speech_recognition/pocketsphinx-data/fr-FR/language-model.lm.bin`` with ``french.lm.bin`` created in the previous step.
* Mandarin Chinese: ``/speech_recognition/pocketsphinx-data/zh-CN/``:
    * ``/speech_recognition/pocketsphinx-data/zh-CN/language-model.lm.bin`` is generated as follows:
        1. Download ``zh_broadcastnews_64000_utf8.DMP`` from the `Sphinx Mandarin language model <http://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Mandarin%20Language%20Model/>`__.
        2. Convert from DMP (an obselete Sphinx binary format) to ARPA format: ``sphinx_lm_convert -i zh_broadcastnews_64000_utf8.DMP -o chinese.lm -ofmt arpa``.
        3. Prune with a threshold of 0.00000004 using ``prune-lm --threshold=4e-8 chinese.lm chinese.lm``.
        4. Convert from ARPA format to Sphinx binary format: ``sphinx_lm_convert -i chinese.lm -o chinese.lm.bin``.
        5. Replace ``/speech_recognition/pocketsphinx-data/zh-CN/language-model.lm.bin`` with ``chinese.lm.bin`` created in the previous step.
    * ``/speech_recognition/pocketsphinx-data/zh-CN/pronounciation-dictionary.dict`` is ``zh_broadcastnews_utf8.dic`` from the `Sphinx Mandarin language model <http://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Mandarin%20Language%20Model/>`__.
    * ``/speech_recognition/pocketsphinx-data/zh-CN/acoustic-model/`` is extracted from ``zh_broadcastnews_16k_ptm256_8000.tar.bz2`` in the `Sphinx Mandarin acoustic model <http://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Mandarin%20Broadcast%20News%20acoustic%20models/>`__.
    * To get better Chinese recognition accuracy at the expense of higher disk space and RAM usage, simply skip step 3 when preparing ``zh_broadcastnews_64000_utf8.DMP``.

FLAC (for some systems)
~~~~~~~~~~~~~~~~~~~~~~~

A FLAC encoder is required to encode the audio data to send to the API. If using Windows, OS X, or Linux on an i385-compatible architecture, the encoder is already bundled with this library - you do not need to install anything else.

Otherwise, ensure that you have the ``flac`` command line tool, which is often available through the system package manager.

In summary, this library requires:

* Python 2.6, 2.7, or 3.3+
* PyAudio (required only if you need to use microphone input)
* PocketSphinx (required only if you need to use the Sphinx recognizer)
* FLAC encoder (required only if the system is not x86-based Windows/Linux/OS X)

Troubleshooting
---------------

The ``Microphone`` class is missing/not defined!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This class is not defined when PyAudio is not available.

Make sure you have PyAudio installed, and make sure you can import it correctly. Test this out by opening a Python console (make sure to use the same version you're running your program with!) and typing in ``import pyaudio``. If you get an error, PyAudio is not installed or not configured correctly.

See the "Requirements" section for more information about installing PyAudio.

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

Reference
---------

``Microphone(device_index = None, sample_rate = 16000, chunk_size = 1024)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is available if PyAudio is available, and is undefined otherwise.

Creates a new ``Microphone`` instance, which represents a physical microphone on the computer. Subclass of ``AudioSource``.

If ``device_index`` is unspecified or ``None``, the default microphone is used as the audio source. Otherwise, ``device_index`` should be the index of the device to use for audio input.

A device index is an integer between 0 and ``pyaudio.get_device_count() - 1`` (assume we have used ``import pyaudio`` beforehand) inclusive. It represents an audio device such as a microphone or speaker. See the `PyAudio documentation <http://people.csail.mit.edu/hubert/pyaudio/docs/>`__ for more details.

The microphone audio is recorded in chunks of ``chunk_size`` samples, at a rate of ``sample_rate`` samples per second (Hertz).

Higher ``sample_rate`` values result in better audio quality, but also more bandwidth (and therefore, slower recognition). Additionally, some machines, such as some Raspberry Pi models, can't keep up if this value is too high.

Higher ``chunk_size`` values help avoid triggering on rapidly changing ambient noise, but also makes detection less sensitive. This value, generally, should be left at its default.

Instances of this class are context managers, and are designed to be used with ``with`` statements:

.. code:: python

    with Microphone() as source:    # open the microphone and start recording
        pass                        # do things here - ``source`` is the Microphone instance created above
                                    # the microphone is automatically released at this point

``Microphone.list_microphone_names()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a list of the names of all available microphones. For microphones where the name can't be retrieved, the list entry contains ``None`` instead.

The index of each microphone's name is the same as its device index when creating a ``Microphone`` instance - indices in this list can be used as values of ``device_index``.

To create a ``Microphone`` instance by name:

.. code:: python

    m = None
    for microphone_name in Microphone.list_microphone_names():
        if microphone_name == "HDA Intel HDMI: 0 (hw:0,3)":
            m = Microphone(i)

``WavFile(filename_or_fileobject)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creates a new ``WavFile`` instance given a WAV audio file ``filename_or_fileobject``. Subclass of ``AudioSource``.

If ``filename_or_fileobject`` is a string, then it is interpreted as a path to a WAV audio file (mono or stereo) on the filesystem. Otherwise, ``filename_or_fileobject`` should be a file-like object such as ``io.BytesIO`` or similar.

Note that the WAV file must be in PCM/LPCM format; WAVE_FORMAT_EXTENSIBLE and compressed WAV are not supported and may result in undefined behaviour.

Instances of this class are context managers, and are designed to be used with ``with`` statements:

.. code:: python

    import speech_recognition as sr
    with sr.WavFile("SOMETHING.wav") as source:    # open the WAV file for reading
        pass                                       # do things here - ``source`` is the WavFile instance created above

``wavfile_instance.DURATION``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Represents the length of the audio stored in the WAV file in seconds. This property is only available when inside a context - essentially, that means it should only be accessed inside a ``with wavfile_instance ...`` statement. Outside of contexts, this property is ``None``.

This is useful when combined with the ``offset`` parameter of ``recognizer_instance.record``, since when together it is possible to perform speech recognition in chunks.

However, note that recognizing speech in multiple chunks is not the same as recognizing the whole thing at once. If spoken words appear on the boundaries that we split the audio into chunks on, each chunk only gets part of the word, which may result in inaccurate results.

``Recognizer()``
~~~~~~~~~~~~~~~~

Creates a new ``Recognizer`` instance, which represents a collection of speech recognition settings and functionality.

``recognizer_instance.energy_threshold = 300``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Represents the energy level threshold for sounds. Values below this threshold are considered silence, and values above this threshold are considered speech. Can be changed.

This is adjusted automatically if dynamic thresholds are enabled (see ``recognizer_instance.dynamic_energy_threshold``). A good starting value will generally allow the automatic adjustment to reach a good value faster.

This threshold is associated with the perceived loudness of the sound, but it is a nonlinear relationship. The actual energy threshold you will need depends on your microphone sensitivity or audio data. Typical values for a silent room are 0 to 100, and typical values for speaking are between 150 and 3500. Ambient (non-speaking) noise has a significant impact on what values will work best.

If you're having trouble with the recognizer trying to recognize words even when you're not speaking, try tweaking this to a higher value. If you're having trouble with the recognizer not recognizing your words when you are speaking, try tweaking this to a lower value. For example, a sensitive microphone or microphones in louder rooms might have a ambient energy level of up to 4000:

.. code:: python

    import speech_recognition as sr
    r = sr.Recognizer()
    r.energy_threshold = 4000
    # rest of your code goes here

The dynamic energy threshold setting can mitigate this by increasing or decreasing this automatically to account for ambient noise. However, this takes time to adjust, so it is still possible to get the false positive detections before the threshold settles into a good value.

To avoid this, use ``recognizer_instance.adjust_for_ambient_noise(source, duration = 1)`` to calibrate the level to a good value. Alternatively, simply set this property to a high value initially (4000 works well), so the threshold is always above ambient noise levels: over time, it will be automatically decreased to account for ambient noise levels.

``recognizer_instance.dynamic_energy_threshold = True``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Represents whether the energy level threshold (see ``recognizer_instance.energy_threshold``) for sounds should be automatically adjusted based on the currently ambient noise level while listening. Can be changed.

Recommended for situations where the ambient noise level is unpredictable, which seems to be the majority of use cases. If the ambient noise level is strictly controlled, better results might be achieved by setting this to ``False`` to turn it off.

``recognizer_instance.dynamic_energy_adjustment_damping = 0.15``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the dynamic energy threshold setting is enabled (see ``recognizer_instance.dynamic_energy_threshold``), represents approximately the fraction of the current energy threshold that is retained after one second of dynamic threshold adjustment. Can be changed (not recommended).

Lower values allow for faster adjustment, but also make it more likely to miss certain phrases (especially those with slowly changing volume). This value should be between 0 and 1. As this value approaches 1, dynamic adjustment has less of an effect over time. When this value is 1, dynamic adjustment has no effect.

``recognizer_instance.dynamic_energy_adjustment_ratio = 1.5``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the dynamic energy threshold setting is enabled (see ``recognizer_instance.dynamic_energy_threshold``), represents the minimum factor by which speech is louder than ambient noise. Can be changed (not recommended).

For example, the default value of 1.5 means that speech is at least 1.5 times louder than ambient noise. Smaller values result in more false positives (but fewer false negatives) when ambient noise is loud compared to speech.

``recognizer_instance.pause_threshold = 0.8``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Represents the minimum length of silence (in seconds) that will register as the end of a phrase. Can be changed.

Smaller values result in the recognition completing more quickly, but might result in slower speakers being cut off.

``recognizer_instance.record(source, duration = None, offset = None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Records up to ``duration`` seconds of audio from ``source`` (an ``AudioSource`` instance) starting at ``offset`` (or at the beginning if not specified) into an ``AudioData`` instance, which it returns.

If ``duration`` is not specified, then it will record until there is no more audio input.

``recognizer_instance.adjust_for_ambient_noise(source, duration = 1)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adjusts the energy threshold dynamically using audio from ``source`` (an ``AudioSource`` instance) to account for ambient noise.

Intended to calibrate the energy threshold with the ambient energy level. Should be used on periods of audio without speech - will stop early if any speech is detected.

The ``duration`` parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning. This value should be at least 0.5 in order to get a representative sample of the ambient noise.

``recognizer_instance.listen(source, timeout = None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.

This is done by waiting until the audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking), and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of non-speaking or there is no more audio input. The ending silence is not included.

The ``timeout`` parameter is the maximum number of seconds that it will wait for a phrase to start before giving up and throwing an ``speech_recognition.WaitTimeoutError`` exception. If ``timeout`` is ``None``, it will wait indefinitely.

``recognizer_instance.listen_in_background(source, callback)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Spawns a thread to repeatedly record phrases from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance and call ``callback`` with that ``AudioData`` instance as soon as each phrase are detected.

Returns a function object that, when called, requests that the background listener thread stop, and waits until it does before returning. The background thread is a daemon and will not stop the program from exiting if there are no other non-daemon threads.

Phrase recognition uses the exact same mechanism as ``recognizer_instance.listen(source)``.

The ``callback`` parameter is a function that should accept two parameters - the ``recognizer_instance``, and an ``AudioData`` instance representing the captured audio. Note that ``callback`` function will be called from a non-main thread.

``recognizer_instance.recognize_sphinx(audio_data, language = "en-US", show_all = False)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using CMU Sphinx.

The recognition language is determined by ``language``, an IETF language tag like ``"en-US"`` or ``"en-GB"``, defaulting to US English. Out of the box, only ``en-US`` is supported. See the "Installing other languages" section in the README for information about additional language packs.

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the Sphinx ``pocketsphinx.pocketsphinx.Hypothesis`` object generated by Sphinx.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if there are any issues with the Sphinx installation.

``recognizer_instance.recognize_google(audio_data, key = None, language = "en-US", show_all = False)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Google Speech Recognition API.

The Google Speech Recognition API key is specified by ``key``. If not specified, it uses a generic key that works out of the box. This should generally be used for personal or testing purposes only, as it **may be revoked by Google at any time**.

To obtain your own API key, simply follow the steps on the `API Keys <http://www.chromium.org/developers/how-tos/api-keys>`__ page at the Chromium Developers site. In the Google Developers Console, Google Speech Recognition is listed as "Speech API". Note that **the API quota for your own keys is 50 requests per day**, and there is currently no way to raise this limit.

The recognition language is determined by ``language``, an IETF language tag like ``"en-US"`` or ``"en-GB"``, defaulting to US English. A list of supported language codes can be found `here <http://stackoverflow.com/questions/14257598/>`__. Basically, language codes can be just the language (``en``), or a language with a dialect (``en-US``).

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the raw API response as a JSON dictionary.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the key isn't valid, the quota for the key is maxed out, or there is no internet connection.

``recognizer_instance.recognize_wit(audio_data, key, show_all = False)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Wit.ai API.

The Wit.ai API key is specified by ``key``. Unfortunately, these are not available without `signing up for an account <https://wit.ai/getting-started>`__ and creating an app. You will need to add at least one intent (recognizable sentence) before the API key can be accessed, though the actual intent values don't matter.

To get the API key for a Wit.ai app, go to the app settings, go to the section titled "API Details", and look for "Server Access Token" or "Client Access Token". If the desired field is blank, click on the "Reset token" button on the right of the field. Wit.ai API keys are 32-character uppercase alphanumeric strings.

Though Wit.ai is designed to be used with a fixed set of phrases, it still provides services for general-purpose speech recognition.

The recognition language is configured in the Wit.ai app settings.

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <https://wit.ai/docs/http/20141022#get-intent-via-text-link>`__ as a JSON dictionary.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the key isn't valid, the quota for the key is maxed out, or there is no internet connection.

``recognizer_instance.recognize_ibm(audio_data, username, password, language = "en-US", show_all = False)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the IBM Speech to Text API.

The IBM Speech to Text username and password are specified by ``username`` and ``password``, respectively. Unfortunately, these are not available without an account. IBM has published instructions for obtaining these credentials in the `IBM Watson Developer Cloud documentation <https://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/doc/getting_started/gs-credentials.shtml>`__.

The recognition language is determined by ``language``, an IETF language tag with a dialect like ``"en-US"`` or ``"es-ES"``, defaulting to US English. At the moment, this supports the tags ``"en-US"`` and ``"es-ES"``.

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/speech-to-text/api/v1/#recognize>`__ as a JSON dictionary.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if an error occurred, such as an invalid key, or a broken internet connection.

``recognizer_instance.recognize_att(audio_data, app_key, app_secret, language = "en-US", show_all = False)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the AT&T Speech to Text API.

The AT&T Speech to Text app key and app secret are specified by ``app_key`` and ``app_secret``, respectively. Unfortunately, these are not available without `signing up for an account <http://developer.att.com/apis/speech>`__ and creating an app.

To get the app key and app secret for an AT&T app, go to the `My Apps page <https://matrix.bf.sl.attcompute.com/apps>`__ and look for "APP KEY" and "APP SECRET". AT&T app keys and app secrets are 32-character lowercase alphanumeric strings.

The recognition language is determined by ``language``, an IETF language tag with a dialect like ``"en-US"`` or ``"es-ES"``, defaulting to US English. At the moment, this supports the tags ``"en-US"`` and ``"es-ES"``.

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <https://developer.att.com/apis/speech/docs#resources-speech-to-text>`__ as a JSON dictionary.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the key isn't valid, or there is no internet connection.

``AudioSource``
~~~~~~~~~~~~~~~

Base class representing audio sources. Do not instantiate.

Instances of subclasses of this class, such as ``Microphone`` and ``WavFile``, can be passed to things like ``recognizer_instance.record`` and ``recognizer_instance.listen``.

``AudioData``
~~~~~~~~~~~~~

Storage class for audio data. Do not instantiate.

Instances of this class are returned from ``recognizer_instance.record`` and ``recognizer_instance.listen``, and are passed to callbacks of ``recognizer_instance.listen_in_background``.

``audiodata_instance.get_raw_data(convert_rate = None, convert_width = None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a byte string representing the raw frame data for the audio represented by the ``AudioData`` instance.

If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

Writing these bytes directly to a file results in a valid `RAW/PCM audio file <https://en.wikipedia.org/wiki/Raw_audio_format>`__.

``audiodata_instance.get_wav_data(convert_rate = None, convert_width = None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a byte string representing the contents of a WAV file containing the audio represented by the ``AudioData`` instance.

If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

Writing these bytes directly to a file results in a valid `WAV file <https://en.wikipedia.org/wiki/WAV>`__.

``audiodata_instance.get_flac_data(convert_rate = None, convert_width = None)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a byte string representing the contents of a FLAC file containing the audio represented by the ``AudioData`` instance.

If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

Writing these bytes directly to a file results in a valid `FLAC file <https://en.wikipedia.org/wiki/FLAC>`__.

Developing
----------

To hack on this library, first make sure you have all the requirements listed in the "Requirements" section.

-  Most of the library code lives in ``speech_recognition/__init__.py``.
-  Examples live under the ``examples/`` directory, and the demo script lives in ``speech_recognition/__main__.py``.
-  The FLAC encoder binaries are in the ``speech_recognition/`` directory.

To install/reinstall the library locally, run ``python setup.py install`` in the project root directory.

Releases are done by running either ``build.sh`` or ``build.bat``. These are bash and batch scripts, respectively, that build Python source packages and `Python Wheels <http://pythonwheels.com/>`__, then upload them to PyPI.

Features and bugfixes should be tested, at minimum, on Python 2.7 and a recent version of Python 3. It is highly recommended to test features on Python 2.6, 2.7, 3.3, and the latest version of Python 3.

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

License
-------

Copyright 2014-2016 `Anthony Zhang (Uberi) <https://uberi.github.io>`__.

The source code is available online at `GitHub <https://github.com/Uberi/speech_recognition>`__.

This program is made available under the 3-clause BSD license. See ``LICENSE.txt`` in the project's root directory for more information.

This program distributes source code, binaries, and language files from `CMU Sphinx <http://cmusphinx.sourceforge.net/>`__. These files are BSD-licensed and redistributable as long as copyright notices are correctly retained. See ``speech_recognition/pocketsphinx-data/*/LICENSE*.txt`` and ``third-party/LICENSE-Sphinx.txt`` for details concerning individual files.

This program distributes source code and binaries from `PyAudio <http://people.csail.mit.edu/hubert/pyaudio/>`__. These files are MIT-licensed and redistributable as long as copyright notices are correctly retained. See license files inside ``third-party/LICENSE-PyAudio.txt`` for details concerning individual files.
