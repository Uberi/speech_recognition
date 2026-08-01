from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pyaudio


class PyAudioWrapper:
    @staticmethod
    def get_pyaudio() -> pyaudio.PyAudio:
        """Returns pyaudio.PyAudio instance.

        Checks pyaudio's installation, throws exceptions if pyaudio can't be found
        """
        try:
            import pyaudio
        except ImportError:
            raise AttributeError(
                "Could not find PyAudio; Run `pip install SpeechRecognition[audio]`"
            )
        return pyaudio.PyAudio()

    @staticmethod
    def list_microphone_names():
        """
        Returns a list of the names of all available microphones. For microphones where the name can't be retrieved, the list entry contains ``None`` instead.

        The index of each microphone's name in the returned list is the same as its device index when creating a ``Microphone`` instance - if you want to use the microphone at index 3 in the returned list, use ``Microphone(device_index=3)``.
        """
        audio = PyAudioWrapper.get_pyaudio()
        try:
            result = []
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                result.append(device_info.get("name"))
        finally:
            audio.terminate()
        return result
