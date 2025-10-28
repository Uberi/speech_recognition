#!/usr/bin/env python3

import logging
import os
import stat

from setuptools import find_packages, setup
from setuptools.command.install import install

import speech_recognition

logger = logging.getLogger("SpeechRecognition.setup")

FILES_TO_MARK_EXECUTABLE = ["flac-linux-x86", "flac-linux-x86_64", "flac-mac", "flac-win32.exe"]


class InstallWithExtraSteps(install):
    def run(self):
        install.run(self)  # do the original install steps

        # mark the FLAC executables as executable by all users (this fixes occasional issues when file permissions get messed up)
        for output_path in self.get_outputs():
            if os.path.basename(output_path) in FILES_TO_MARK_EXECUTABLE:
                logger.info("setting executable permissions on %s", output_path)
                stat_info = os.stat(output_path)
                OWNER_CAN_READ_EXECUTE = stat.S_IRUSR | stat.S_IXUSR
                GROUP_CAN_READ_EXECUTE = stat.S_IRGRP | stat.S_IXGRP
                OTHERS_CAN_READ_EXECUTE = stat.S_IROTH | stat.S_IXOTH
                os.chmod(
                    output_path,
                    stat_info.st_mode
                    | OWNER_CAN_READ_EXECUTE
                    | GROUP_CAN_READ_EXECUTE
                    | OTHERS_CAN_READ_EXECUTE,
                )


setup(
    name="SpeechRecognition",
    version=speech_recognition.__version__,
    packages=find_packages(exclude=["tests.*", "test"]),
    include_package_data=True,
    cmdclass={"install": InstallWithExtraSteps},

    # PyPI metadata
    author=speech_recognition.__author__,
    author_email="azhang9@gmail.com",
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
