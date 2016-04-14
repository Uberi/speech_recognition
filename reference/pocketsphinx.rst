Notes on using PocketSphinx
===========================

Installing other languages
--------------------------

By default, SpeechRecognition's Sphinx functionality supports only US English. Additional language packs are also available, but not included due to the files being too large:

* `International French <https://db.tt/tVNcZXao>`__
* `Mandarin Chinese <https://db.tt/2YQVXmEk>`__

To install a language pack, download the ZIP archives and extract them directly into the module install directory (you can find the module install directory by running ``python -c "import speech_recognition as sr, os.path as p; print(p.dirname(sr.__file__))"``).

Here is a simple Bash script to install all of them:

.. code:: bash

    #!/usr/bin/env bash
    SR_LIB=$(python -c "import speech_recognition as sr, os.path as p; print(p.dirname(sr.__file__))")
    sudo apt-get install --yes wget unzip
    sudo wget https://db.tt/tVNcZXao -O "$SR_LIB/fr-FR.zip"
    sudo unzip -o "$SR_LIB/fr-FR.zip" -d "$SR_LIB"
    sudo chmod --recursive a+r "$SR_LIB/fr-FR/"
    sudo wget https://db.tt/2YQVXmEk -O "$SR_LIB/zh-CN.zip"
    sudo unzip -o "$SR_LIB/zh-CN.zip" -d "$SR_LIB"
    sudo chmod --recursive a+r "$SR_LIB/zh-CN/"

Once installed, you can simply specify the language using the ``language`` parameter of ``recognizer_instance.recognize_sphinx``. For example, French would be specified with ``"fr-FR"`` and Mandarin with ``"zh-CN"``.

Building PocketSphinx-Python from source
----------------------------------------

For Windows, it is recommended to install the precompiled Wheel packages. These are provided because building Pocketsphinx on Windows requires a lot of work, and can take hours to download and install all the surrounding software.

For Linux and other POSIX systems (like OS X), you'll want to build from source. It should take less than two minutes on a fast machine.

* On any Debian-derived Linux distributions (like Ubuntu and Mint):
    1. Run ``sudo apt-get install python python-all-dev python-pip build-essential swig git`` for Python 2, or ``sudo apt-get install python3 python3-all-dev python3-pip build-essential swig git`` for Python 3.
    2. Run ``pip install pocketsphinx`` for Python 2, or ``pip3 install pocketsphinx`` for Python 3.
* On OS X:
    1. Run ``brew install swig git python`` for Python 2, or ``brew install swig git python3`` for Python 3.
    2. Install PocketSphinx-Python using Pip: ``pip install pocketsphinx``.
        * If this gives errors when importing the library in your program, try running ``brew link --overwrite python``.
* On other POSIX-based systems:
    1. Install `Python <https://www.python.org/downloads/>`__, `Pip <https://pip.pypa.io/en/stable/installing/>`__, `SWIG <http://www.swig.org/download.html>`__, and `Git <https://git-scm.com/downloads>`__, preferably using a package manager.
    2. Install PocketSphinx-Python using Pip: ``pip install pocketsphinx``.
* On Windows:
    1. Install `Python <https://www.python.org/downloads/>`__, `Pip <https://pip.pypa.io/en/stable/installing/>`__, `SWIG <http://www.swig.org/download.html>`__, and `Git <https://git-scm.com/downloads>`__, preferably using a package manager.
    2. Install the necessary `compilers suite <http://blog.ionelmc.ro/2014/12/21/compiling-python-extensions-on-windows/>`__ (`here's a PDF version <https://github.com/Uberi/speech_recognition/blob/master/third-party/Compiling%20Python%20extensions%20on%20Windows.pdf>`__ in case the link goes down) for compiling modules for your particular Python version:
        * `Microsoft Visual C++ Compiler for Python 2.7 <http://www.microsoft.com/en-us/download/details.aspx?id=44266>`__ for Python 2.7.
        * `Visual Studio 2015 Community Edition <https://www.visualstudio.com/downloads/download-visual-studio-vs>`__ for Python 3.5.
        * The installation process for Python 3.4 is outlined in the article above.
    3. Add the folders containing the Python, SWIG, and Git binaries to your ``PATH`` environment variable.
        * My ``PATH`` environment variable looks something like: ``C:\Users\Anthony\Desktop\swigwin-3.0.8;C:\Program Files\Git\cmd;(A BUNCH OF OTHER PATHS)``.
    4. Reboot to apply changes.
    5. Download the full PocketSphinx-Python source code by running ``git clone --recursive --depth 1 https://github.com/cmusphinx/pocketsphinx-python`` (downloading the ZIP archive from GitHub will not work).
    6. Run ``python setup.py install`` in the PocketSphinx-Python source code folder to compile and install PocketSphinx.
    7. Side note: when I build the precompiled Wheel packages, I skip steps 5 and 6 and do the following instead:
        * For Python 2.7: ``C:\Python27\python.exe setup.py bdist_wheel``.
        * For Python 3.4: ``C:\Python34\python.exe setup.py bdist_wheel``.
        * For Python 3.5: ``C:\Users\Anthony\AppData\Local\Programs\Python\Python35\python.exe setup.py bdist_wheel``.
        * The resulting packages are located in the ``dist`` folder of the PocketSphinx-Python project directory.

Notes on the structure of the language data
-------------------------------------------

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
-----------------------------------------------

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
* International French: ``/speech_recognition/pocketsphinx-data/fr-FR/``:
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