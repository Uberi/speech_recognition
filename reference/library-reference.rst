Speech Recognition Library Reference
====================================

``Microphone(device_index = None, sample_rate = 16000, chunk_size = 1024)``
---------------------------------------------------------------------------

Creates a new ``Microphone`` instance, which represents a physical microphone on the computer. Subclass of ``AudioSource``.

This will throw an ``AttributeError`` if you don't have PyAudio 0.2.9 or later installed.

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
--------------------------------------

Returns a list of the names of all available microphones. For microphones where the name can't be retrieved, the list entry contains ``None`` instead.

The index of each microphone's name is the same as its device index when creating a ``Microphone`` instance - indices in this list can be used as values of ``device_index``.

To create a ``Microphone`` instance by name:

.. code:: python

    m = None
    for microphone_name in Microphone.list_microphone_names():
        if microphone_name == "HDA Intel HDMI: 0 (hw:0,3)":
            m = Microphone(i)

``AudioFile(filename_or_fileobject)``
-------------------------------------

Creates a new ``AudioFile`` instance given a WAV/AIFF/FLAC audio file `filename_or_fileobject`. Subclass of ``AudioSource``.

If ``filename_or_fileobject`` is a string, then it is interpreted as a path to an audio file on the filesystem. Otherwise, ``filename_or_fileobject`` should be a file-like object such as ``io.BytesIO`` or similar.

Note that functions that read from the audio (such as ``recognizer_instance.record`` or ``recognizer_instance.listen``) will move ahead in the stream. For example, if you execute ``recognizer_instance.record(audiofile_instance, duration=10)`` twice, the first time it will return the first 10 seconds of audio, and the second time it will return the 10 seconds of audio right after that. This is always reset when entering the context with a context manager.

WAV files must be in PCM/LPCM format; WAVE_FORMAT_EXTENSIBLE and compressed WAV are not supported and may result in undefined behaviour.

Both AIFF and AIFF-C (compressed AIFF) formats are supported.

FLAC files must be in native FLAC format; OGG-FLAC is not supported and may result in undefined behaviour.

Instances of this class are context managers, and are designed to be used with ``with`` statements:

.. code:: python

    import speech_recognition as sr
    with sr.AudioFile("SOME_AUDIO_FILE") as source:    # open the audio file for reading
        pass                                           # do things here - ``source`` is the AudioFile instance created above

``audiofile_instance.DURATION``
-------------------------------

Represents the length of the audio stored in the audio file in seconds. This property is only available when inside a context - essentially, that means it should only be accessed inside the body of a ``with audiofile_instance ...`` statement. Outside of contexts, this property is ``None``.

This is useful when combined with the ``offset`` parameter of ``recognizer_instance.record``, since when together it is possible to perform speech recognition in chunks.

However, note that recognizing speech in multiple chunks is not the same as recognizing the whole thing at once. If spoken words appear on the boundaries that we split the audio into chunks on, each chunk only gets part of the word, which may result in inaccurate results.

``Recognizer()``
----------------

Creates a new ``Recognizer`` instance, which represents a collection of speech recognition settings and functionality.

``recognizer_instance.energy_threshold = 300``
----------------------------------------------

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
-------------------------------------------------------

Represents whether the energy level threshold (see ``recognizer_instance.energy_threshold``) for sounds should be automatically adjusted based on the currently ambient noise level while listening. Can be changed.

Recommended for situations where the ambient noise level is unpredictable, which seems to be the majority of use cases. If the ambient noise level is strictly controlled, better results might be achieved by setting this to ``False`` to turn it off.

``recognizer_instance.dynamic_energy_adjustment_damping = 0.15``
----------------------------------------------------------------

If the dynamic energy threshold setting is enabled (see ``recognizer_instance.dynamic_energy_threshold``), represents approximately the fraction of the current energy threshold that is retained after one second of dynamic threshold adjustment. Can be changed (not recommended).

Lower values allow for faster adjustment, but also make it more likely to miss certain phrases (especially those with slowly changing volume). This value should be between 0 and 1. As this value approaches 1, dynamic adjustment has less of an effect over time. When this value is 1, dynamic adjustment has no effect.

``recognizer_instance.dynamic_energy_adjustment_ratio = 1.5``
-------------------------------------------------------------

If the dynamic energy threshold setting is enabled (see ``recognizer_instance.dynamic_energy_threshold``), represents the minimum factor by which speech is louder than ambient noise. Can be changed (not recommended).

For example, the default value of 1.5 means that speech is at least 1.5 times louder than ambient noise. Smaller values result in more false positives (but fewer false negatives) when ambient noise is loud compared to speech.

``recognizer_instance.pause_threshold = 0.8``
---------------------------------------------

Represents the minimum length of silence (in seconds) that will register as the end of a phrase. Can be changed.

Smaller values result in the recognition completing more quickly, but might result in slower speakers being cut off.

``recognizer_instance.record(source, duration = None, offset = None)``
----------------------------------------------------------------------

Records up to ``duration`` seconds of audio from ``source`` (an ``AudioSource`` instance) starting at ``offset`` (or at the beginning if not specified) into an ``AudioData`` instance, which it returns.

If ``duration`` is not specified, then it will record until there is no more audio input.

``recognizer_instance.adjust_for_ambient_noise(source, duration = 1)``
----------------------------------------------------------------------

Adjusts the energy threshold dynamically using audio from ``source`` (an ``AudioSource`` instance) to account for ambient noise.

Intended to calibrate the energy threshold with the ambient energy level. Should be used on periods of audio without speech - will stop early if any speech is detected.

The ``duration`` parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning. This value should be at least 0.5 in order to get a representative sample of the ambient noise.

``recognizer_instance.listen(source, timeout = None)``
------------------------------------------------------

Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.

This is done by waiting until the audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking), and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of non-speaking or there is no more audio input. The ending silence is not included.

The ``timeout`` parameter is the maximum number of seconds that it will wait for a phrase to start before giving up and throwing an ``speech_recognition.WaitTimeoutError`` exception. If ``timeout`` is ``None``, it will wait indefinitely.

``recognizer_instance.listen_in_background(source, callback)``
--------------------------------------------------------------

Spawns a thread to repeatedly record phrases from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance and call ``callback`` with that ``AudioData`` instance as soon as each phrase are detected.

Returns a function object that, when called, requests that the background listener thread stop, and waits until it does before returning. The background thread is a daemon and will not stop the program from exiting if there are no other non-daemon threads.

Phrase recognition uses the exact same mechanism as ``recognizer_instance.listen(source)``.

The ``callback`` parameter is a function that should accept two parameters - the ``recognizer_instance``, and an ``AudioData`` instance representing the captured audio. Note that ``callback`` function will be called from a non-main thread.

``recognizer_instance.recognize_sphinx(audio_data, language = "en-US", show_all = False)``
------------------------------------------------------------------------------------------

Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using CMU Sphinx.

The recognition language is determined by ``language``, an IETF language tag like ``"en-US"`` or ``"en-GB"``, defaulting to US English. Out of the box, only ``en-US`` is supported. See `Notes on using `PocketSphinx <https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst>`__ for information about installing other languages. This document is also included under ``reference/pocketsphinx.rst``.

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the Sphinx ``pocketsphinx.pocketsphinx.Hypothesis`` object generated by Sphinx.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if there are any issues with the Sphinx installation.

``recognizer_instance.recognize_google(audio_data, key = None, language = "en-US", show_all = False)``
------------------------------------------------------------------------------------------------------

Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Google Speech Recognition API.

The Google Speech Recognition API key is specified by ``key``. If not specified, it uses a generic key that works out of the box. This should generally be used for personal or testing purposes only, as it **may be revoked by Google at any time**.

To obtain your own API key, simply follow the steps on the `API Keys <http://www.chromium.org/developers/how-tos/api-keys>`__ page at the Chromium Developers site. In the Google Developers Console, Google Speech Recognition is listed as "Speech API". Note that **the API quota for your own keys is 50 requests per day**, and there is currently no way to raise this limit.

The recognition language is determined by ``language``, an IETF language tag like ``"en-US"`` or ``"en-GB"``, defaulting to US English. A list of supported language codes can be found `here <http://stackoverflow.com/questions/14257598/what-are-language-codes-for-voice-recognition-languages-in-chromes-implementati>`__. Basically, language codes can be just the language (``en``), or a language with a dialect (``en-US``).

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the raw API response as a JSON dictionary.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.

``recognizer_instance.recognize_wit(audio_data, key, show_all = False)``
------------------------------------------------------------------------

Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Wit.ai API.

The Wit.ai API key is specified by ``key``. Unfortunately, these are not available without `signing up for an account <https://wit.ai/>`__ and creating an app. You will need to add at least one intent to the app before you can see the API key, though the actual intent settings don't matter.

To get the API key for a Wit.ai app, go to the app's overview page, go to the section titled "Make an API request", and look for something along the lines of ``Authorization: Bearer XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX``; ``XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`` is the API key. Wit.ai API keys are 32-character uppercase alphanumeric strings.

The recognition language is configured in the Wit.ai app settings.

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <https://wit.ai/docs/http/20141022#get-intent-via-text-link>`__ as a JSON dictionary.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.

``recognizer_instance.recognize_bing(audio_data, key, language = "en-US", show_all = False)``
---------------------------------------------------------------------------------------------

Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Microsoft Bing Voice Recognition API.

The Microsoft Bing Voice Recognition API key is specified by ``key``. Unfortunately, these are not available without `signing up for an account <https://www.microsoft.com/cognitive-services/en-us/speech-api>`__ with Microsoft Cognitive Services.

To get the API key, go to the `Microsoft Cognitive Services subscriptions overview <https://www.microsoft.com/cognitive-services/en-us/subscriptions>`__, go to the entry titled "Speech", and look for the key under the "Keys" column. Microsoft Bing Voice Recognition API keys are 32-character lowercase hexadecimal strings.

The recognition language is determined by ``language``, an RFC5646 language tag like ``"en-US"`` (US English) or ``"fr-FR"`` (International French), defaulting to US English. A list of supported language values can be found in the `API documentation <https://www.microsoft.com/cognitive-services/en-us/speech-api/documentation/api-reference-rest/BingVoiceRecognition#user-content-4-supported-locales>`__.

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <https://www.microsoft.com/cognitive-services/en-us/speech-api/documentation/api-reference-rest/BingVoiceRecognition#user-content-3-voice-recognition-responses>`__ as a JSON dictionary.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.

``recognizer_instance.recognize_api(audio_data, client_access_token, language = "en", session_id = None, show_all = False)``
----------------------------------------------------------------------------------------------------------------------------

Perform speech recognition on ``audio_data`` (an ``AudioData`` instance), using the api.ai Speech to Text API.

The api.ai API client access token is specified by ``client_access_token``. Unfortunately, this is not available without `signing up for an account <https://console.api.ai/api-client/#/signup>`__ and creating an api.ai agent. To get the API client access token, go to the agent settings, go to the section titled "API keys", and look for "Client access token". API client access tokens are 32-character lowercase hexadecimal strings.

Although the recognition language is specified when creating the api.ai agent in the web console, it must also be provided in the ``language`` parameter as an RFC5646 language tag like ``"en"`` (US English) or ``"fr"`` (International French), defaulting to US English. A list of supported language values can be found in the `API documentation <https://api.ai/docs/reference/#languages>`__.

The ``session_id`` is an optional string of up to 36 characters used to identify the client making the requests; api.ai can make use of previous requests that used the same session ID to give more accurate results for future requests. If ``None``, sessions are not used; every query is interpreted as if it is the first one.

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <https://api.ai/docs/reference/#a-namepost-multipost-query-multipart>`__ as a JSON dictionary.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.

``recognizer_instance.recognize_ibm(audio_data, username, password, language = "en-US", show_all = False)``
-----------------------------------------------------------------------------------------------------------

Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the IBM Speech to Text API.

The IBM Speech to Text username and password are specified by ``username`` and ``password``, respectively. Unfortunately, these are not available without `signing up for an account <https://console.ng.bluemix.net/registration/>`__. Once logged into the Bluemix console, follow the instructions for `creating an IBM Watson service instance <http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/doc/getting_started/gs-credentials.shtml>`__, where the Watson service is "Speech To Text". IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX, while passwords are mixed-case alphanumeric strings.

The recognition language is determined by ``language``, an IETF language tag with a dialect like ``"en-US"`` or ``"es-ES"``, defaulting to US English. The supported languages are listed under the ``model`` parameter of the `audio recognition API documentation <http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/speech-to-text/api/v1/#recognize_audio_sessionless12>`__.

Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the `raw API response <http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/speech-to-text/api/v1/#recognize_audio_sessionless12>`__ as a JSON dictionary.

Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.

``AudioSource``
---------------

Base class representing audio sources. Do not instantiate.

Instances of subclasses of this class, such as ``Microphone`` and ``AudioFile``, can be passed to things like ``recognizer_instance.record`` and ``recognizer_instance.listen``. Those instances act like context managers, and are designed to be used with ``with`` statements.

For more information, see the documentation for the individual subclasses.

``AudioData``
-------------

Storage class for audio data. Do not instantiate.

Instances of this class are returned from ``recognizer_instance.record`` and ``recognizer_instance.listen``, and are passed to callbacks of ``recognizer_instance.listen_in_background``.

``audiodata_instance.get_raw_data(convert_rate = None, convert_width = None)``
------------------------------------------------------------------------------

Returns a byte string representing the raw frame data for the audio represented by the ``AudioData`` instance.

If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

Writing these bytes directly to a file results in a valid `RAW/PCM audio file <https://en.wikipedia.org/wiki/Raw_audio_format>`__.

``audiodata_instance.get_wav_data(convert_rate = None, convert_width = None)``
------------------------------------------------------------------------------

Returns a byte string representing the contents of a WAV file containing the audio represented by the ``AudioData`` instance.

If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

Writing these bytes directly to a file results in a valid `WAV file <https://en.wikipedia.org/wiki/WAV>`__.

``audiodata_instance.get_aiff_data(convert_rate = None, convert_width = None)``
-------------------------------------------------------------------------------

Returns a byte string representing the contents of an AIFF-C file containing the audio represented by the ``AudioData`` instance.

If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

Writing these bytes directly to a file results in a valid `AIFF-C file <https://en.wikipedia.org/wiki/Audio_Interchange_File_Format>`__.

``audiodata_instance.get_flac_data(convert_rate = None, convert_width = None)``
-------------------------------------------------------------------------------

Returns a byte string representing the contents of a FLAC file containing the audio represented by the ``AudioData`` instance.

Note that 32-bit FLAC is not supported. If the audio data is 32-bit and ``convert_width`` is not specified, then the resulting FLAC will be a 24-bit FLAC.

If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

Writing these bytes directly to a file results in a valid `FLAC file <https://en.wikipedia.org/wiki/FLAC>`__.
