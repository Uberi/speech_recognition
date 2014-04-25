import os
from setuptools import setup, find_packages

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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
