#!/usr/bin/env python3

from setuptools import find_packages, setup

import speech_recognition

setup(
    name="SpeechRecognition",
    version=speech_recognition.__version__,
    packages=find_packages(exclude=["tests.*", "test", "speech_recognition.models"]),
    include_package_data=True,

    # PyPI metadata
    author=speech_recognition.__author__,
    author_email="azhang9@gmail.com",
    maintainer="nikkie",
    maintainer_email="takuyafjp+develop@gmail.com",
    description=speech_recognition.__doc__,
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    license=speech_recognition.__license__,
    keywords="speech recognition voice sphinx google wit bing api houndify ibm snowboy",
    url="https://github.com/Uberi/speech_recognition#readme",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Other OS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    python_requires=">=3.9",
    install_requires=[
        "typing-extensions",
        "standard-aifc; python_version>='3.13'",
        "audioop-lts; python_version>='3.13'",
    ],
    entry_points={
        "console_scripts": ["sprc=speech_recognition.cli:main"],
    },
)
