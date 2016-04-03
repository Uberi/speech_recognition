#!/usr/bin/env python3

import sys, os, stat

from setuptools import setup
from setuptools.command.install import install
from distutils import log

import speech_recognition

if sys.version_info < (2, 6):
    print("THIS MODULE REQUIRES PYTHON 2.6, 2.7, OR 3.3+. YOU ARE CURRENTLY USING PYTHON {0}".format(sys.version))
    sys.exit(1)

FILES_TO_MARK_EXECUTABLE = ["flac-linux-i386", "flac-mac", "flac-win32.exe"]
class InstallWithExtraSteps(install):
    def run(self):
        install.run(self) # do the original install steps

        # mark the FLAC executables as executable by all users (this fixes occasional issues when file permissions get messed up)
        for output_path in self.get_outputs():
            if os.path.basename(output_path) in FILES_TO_MARK_EXECUTABLE:
                log.info("setting executable permissions on {}".format(output_path))
                stat_info = os.stat(output_path)
                os.chmod(
                    output_path,
                    stat_info.st_mode |
                    stat.S_IRUSR | stat.S_IXUSR | # owner can read/execute
                    stat.S_IRGRP | stat.S_IXGRP | # group can read/execute
                    stat.S_IROTH | stat.S_IXOTH # everyone else can read/execute
                )

setup(
    name = "SpeechRecognition",
    version = speech_recognition.__version__,
    packages = ["speech_recognition"],
    include_package_data = True,
    cmdclass = {"install": InstallWithExtraSteps},

    # PyPI metadata
    author = speech_recognition.__author__,
    author_email = "azhang9@gmail.com",
    description = speech_recognition.__doc__,
    long_description = open("README.rst").read(),
    license = speech_recognition.__license__,
    keywords = "speech recognition voice google wit bing api ibm",
    url = "https://github.com/Uberi/speech_recognition#readme",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Other OS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
)
