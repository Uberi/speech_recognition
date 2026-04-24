Contributing
============

To hack on this library, first make sure you have all the requirements listed in the "Requirements" section of the `README <https://github.com/Uberi/speech_recognition#readme>`__.

-  Most of the library code lives in ``speech_recognition/__init__.py``.
-  Examples live under the ``examples/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/examples>`__, and the demo script lives in ``speech_recognition/__main__.py``.
-  The FLAC encoder binaries are in the ``speech_recognition/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/speech_recognition>`__.
-  Documentation can be found in the ``reference/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/reference>`__.
-  Third-party libraries, utilities, and reference material are in the ``third-party/`` `directory <https://github.com/Uberi/speech_recognition/tree/master/third-party>`__.

To install/reinstall the library locally, run ``python -m pip install -e .[dev]`` in the project `root directory <https://github.com/Uberi/speech_recognition>`__.

Before a release, the version number is bumped in ``README.rst`` and ``speech_recognition/version.txt``. Version tags are then created using ``git config gpg.program gpg2 && git config user.signingkey DB45F6C431DE7C2DCD99FF7904882258A4063489 && git tag -s VERSION_GOES_HERE -m "Version VERSION_GOES_HERE"``.

Releases are done by running ``make-release.sh VERSION_GOES_HERE`` to build the Python source packages, sign them, and upload them to PyPI.

Testing
-------

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
----------------

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

Note on AI-generated contributions
-----------------------------------

Using AI as a learning aid or development tool is fine.
However, you are expected to understand and be able to explain any code you submit.
Submissions showing signs of unreviewed AI generation — such as unnecessary code, inconsistent style, or nonexistent API usage — will be rejected without further review.
