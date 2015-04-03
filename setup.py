#!/usr/bin/env python3

from setuptools import setup, find_packages

import sys
if sys.version_info < (2, 6):
    print("THIS MODULE REQUIRES PYTHON 2.6 OR LATER. YOU ARE CURRENTLY USING PYTHON " + sys.version)
    sys.exit(1)

import speech_recognition

setup(
    name="SpeechRecognition",
    version=speech_recognition.__version__,
    packages=["speech_recognition"],
    include_package_data=True,

    # PyPI metadata
    author=speech_recognition.__author__,
    author_email="azhang9@gmail.com",
    description=speech_recognition.__doc__,
    long_description=open("README.rst").read(),
    license=speech_recognition.__license__,
    keywords="speech recognition google",
    url="https://github.com/Uberi/speech_recognition#readme",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Other OS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
