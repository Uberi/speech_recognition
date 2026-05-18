from __future__ import annotations

import aifc
import audioop
import io
import os
import platform
import stat
import subprocess
import sys
import wave


class AudioData(object):
    """
    Creates a new ``AudioData`` instance, which represents mono audio data.

    The raw audio data is specified by ``frame_data``, which is a sequence of bytes representing audio samples. This is the frame data structure used by the PCM WAV format.

    The width of each sample, in bytes, is specified by ``sample_width``. Each group of ``sample_width`` bytes represents a single audio sample.

    The audio data is assumed to have a sample rate of ``sample_rate`` samples per second (Hertz).

    Usually, instances of this class are obtained from ``recognizer_instance.record`` or ``recognizer_instance.listen``, or in the callback for ``recognizer_instance.listen_in_background``, rather than instantiating them directly.
    """

    _WAV_HEADER_OVERHEAD = 44

    def __init__(self, frame_data, sample_rate, sample_width):
        assert sample_rate > 0, "Sample rate must be a positive integer"
        assert (
            sample_width % 1 == 0 and 1 <= sample_width <= 4
        ), "Sample width must be between 1 and 4 inclusive"
        self.frame_data = frame_data
        self.sample_rate = sample_rate
        self.sample_width = int(sample_width)

    @classmethod
    def from_file(cls, file_path: str) -> AudioData:
        """Creates a new ``AudioData`` instance from an audio file."""
        import speech_recognition as sr

        r = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            return r.record(source)

    def get_segment(self, start_ms=None, end_ms=None):
        """
        Returns a new ``AudioData`` instance, trimmed to a given time interval. In other words, an ``AudioData`` instance with the same audio data except starting at ``start_ms`` milliseconds in and ending ``end_ms`` milliseconds in.

        If not specified, ``start_ms`` defaults to the beginning of the audio, and ``end_ms`` defaults to the end.
        """
        assert (
            start_ms is None or start_ms >= 0
        ), "``start_ms`` must be a non-negative number"
        assert end_ms is None or end_ms >= (
            0 if start_ms is None else start_ms
        ), "``end_ms`` must be a non-negative number greater or equal to ``start_ms``"
        if start_ms is None:
            start_byte = 0
        else:
            start_byte = int(
                (start_ms * self.sample_rate * self.sample_width) // 1000
            )
        if end_ms is None:
            end_byte = len(self.frame_data)
        else:
            end_byte = int(
                (end_ms * self.sample_rate * self.sample_width) // 1000
            )
        return AudioData(
            self.frame_data[start_byte:end_byte],
            self.sample_rate,
            self.sample_width,
        )

    def split(
        self, max_bytes: int, *, silence_aware: bool = False
    ) -> list[AudioData]:
        """
        Splits this audio into a list of ``AudioData`` chunks targeting ``max_bytes`` per chunk when serialized as WAV (via ``get_wav_data()``).

        When ``silence_aware=False`` (the default), splits the audio mechanically on sample boundaries; each returned chunk's WAV-serialized size is guaranteed to be at most ``max_bytes``. No optional dependency is required.

        When ``silence_aware=True``, chooses chunk boundaries near silences via ``librosa.effects.split`` while keeping every chunk within ``max_bytes`` (the boundary search looks only before the target, never past it). When no suitable silence boundary is found in the look-back window, the chunk is cut at the size-derived target the same way as the fixed-time mode. Requires ``librosa`` and ``numpy``; raises ``SetupError`` if they are not installed or fail to initialize at runtime.

        Raises ``ValueError`` if ``len(frame_data)`` is not a multiple of ``sample_width`` (which ``AudioData`` would otherwise accept), since enforcing the ``max_bytes`` cap requires sample-aligned input.

        Returns ``[self]`` unchanged when the audio already fits within ``max_bytes`` (even when ``silence_aware=True``, in which case the librosa import is skipped).

        Example::

            chunks = audio.split(max_bytes=24 * 1024 * 1024)
            texts = [r.recognize_openai(c) for c in chunks]
        """
        min_required = self._WAV_HEADER_OVERHEAD + self.sample_width
        if max_bytes < min_required:
            raise ValueError(
                "``max_bytes`` must be at least "
                f"{min_required} bytes (WAV header + one sample) for "
                f"sample_width={self.sample_width}; got {max_bytes}"
            )
        if len(self.frame_data) % self.sample_width != 0:
            raise ValueError(
                "``split`` requires ``frame_data`` length to be a multiple "
                f"of sample_width ({self.sample_width}); got "
                f"{len(self.frame_data)} bytes. Trim the audio to a sample "
                "boundary before calling ``split``."
            )

        if (
            len(self.frame_data) + self._WAV_HEADER_OVERHEAD
            <= max_bytes
        ):
            return [self]

        if silence_aware:
            return self._split_silence_aware(max_bytes)
        return self._split_fixed(max_bytes)

    def _split_fixed(self, max_bytes: int) -> list[AudioData]:
        max_payload = max_bytes - self._WAV_HEADER_OVERHEAD
        chunk_size = (max_payload // self.sample_width) * self.sample_width

        chunks: list[AudioData] = []
        for start in range(0, len(self.frame_data), chunk_size):
            chunks.append(
                AudioData(
                    self.frame_data[start:start + chunk_size],
                    self.sample_rate,
                    self.sample_width,
                )
            )
        return chunks

    def _split_silence_aware(self, max_bytes: int) -> list[AudioData]:
        # Force-load the exact dependencies we use so that lazy import or
        # numba-style runtime errors from librosa surface here as a single
        # ``SetupError`` rather than escaping later mid-loop.
        try:
            import numpy as np
            from librosa.effects import split as librosa_split
        except Exception as exc:
            from speech_recognition.exceptions import SetupError

            if isinstance(exc, ImportError):
                hint = (
                    "install them with `pip install "
                    "SpeechRecognition[audio-split]`"
                )
            else:
                hint = (
                    "the package(s) appear installed but failed to "
                    "initialize; check environment-specific issues such "
                    "as a non-writable numba cache directory"
                )
            raise SetupError(
                "silence-aware splitting could not initialize librosa/numpy: "
                f"{type(exc).__name__}: {exc}. {hint}."
            ) from exc

        target_payload = max_bytes - self._WAV_HEADER_OVERHEAD
        chunk_samples = target_payload // self.sample_width

        sw = self.sample_width
        total_samples = len(self.frame_data) // sw
        silence_top_db = 40.0
        min_progress_samples = self.sample_rate // 2
        # Search window stays entirely before ``target`` so ``max_bytes`` is
        # a hard ceiling on chunk size. Quality is recovered by snapping to
        # silence within the look-back window instead of overshooting.
        search_before = min(chunk_samples // 2, 10 * self.sample_rate)

        boundaries = [0]
        start = 0
        while start < total_samples:
            target = min(start + chunk_samples, total_samples)
            if target >= total_samples:
                boundaries.append(total_samples)
                break

            search_start = max(start, target - search_before)
            search_end = target

            proposed_end = target
            if search_end > search_start:
                # Materialize only the search window as float to keep peak
                # memory bounded by the window size (≈ seconds of audio),
                # not the entire recording (potentially hours).
                segment = self._to_float_ndarray(
                    np,
                    raw=self.frame_data[
                        search_start * sw:search_end * sw
                    ],
                )
                # Call-time numba JIT/cache failures inside librosa can
                # raise long after our import probe; translate them into
                # the same SetupError surface.
                try:
                    nonsilent_ranges = librosa_split(
                        segment,
                        top_db=silence_top_db,
                        frame_length=2048,
                        hop_length=512,
                    )
                except Exception as exc:
                    from speech_recognition.exceptions import SetupError

                    raise SetupError(
                        "librosa.effects.split failed during invocation: "
                        f"{type(exc).__name__}: {exc}. The package is "
                        "installed but its runtime backend (numba/llvmlite) "
                        "could not initialize in this environment."
                    ) from exc
                segment_len = len(segment)
                candidates = []
                for nonsilent_range in nonsilent_ranges:
                    start_idx = int(nonsilent_range[0])
                    end_idx = int(nonsilent_range[1])
                    if start_idx > 0:
                        candidates.append(search_start + start_idx)
                    if end_idx < segment_len:
                        candidates.append(search_start + end_idx)

                min_allowed = start + min_progress_samples
                valid = [
                    c for c in candidates if min_allowed < c <= search_end
                ]
                if valid:
                    proposed_end = min(valid, key=lambda c: abs(c - target))

            if proposed_end <= start:
                proposed_end = min(start + chunk_samples, total_samples)
                if proposed_end <= start:
                    break

            boundaries.append(proposed_end)
            start = proposed_end

        chunks: list[AudioData] = []
        for i in range(len(boundaries) - 1):
            sample_start = boundaries[i]
            sample_end = boundaries[i + 1]
            byte_start = sample_start * self.sample_width
            byte_end = sample_end * self.sample_width
            chunks.append(
                AudioData(
                    self.frame_data[byte_start:byte_end],
                    self.sample_rate,
                    self.sample_width,
                )
            )
        return chunks

    def _to_float_ndarray(self, np, raw=None):
        # WAV PCM frame data is little-endian; use explicit byte-order
        # dtypes so the conversion is correct on big-endian hosts.
        if raw is None:
            raw = self.frame_data
        sw = self.sample_width
        if sw == 1:
            raw = audioop.bias(raw, 1, -128)
            return np.frombuffer(raw, dtype=np.int8).astype(np.float32) / 128.0
        if sw == 2:
            return (
                np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
            )
        if sw == 3:
            packed = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
            pad = np.where(packed[:, 2:3] & 0x80, 0xFF, 0x00).astype(np.uint8)
            # ``packed`` is already in little-endian byte order (low byte
            # first); append the sign-extension byte at the high end so
            # the resulting 4-byte rows are little-endian int32.
            extended = np.concatenate([packed, pad], axis=1)
            return (
                extended.view(dtype="<i4").flatten().astype(np.float32)
                / float(1 << 23)
            )
        if sw == 4:
            return (
                np.frombuffer(raw, dtype="<i4").astype(np.float32)
                / float(1 << 31)
            )
        raise ValueError(f"Unsupported sample_width: {sw}")

    def get_raw_data(self, convert_rate=None, convert_width=None):
        """
        Returns a byte string representing the raw frame data for the audio represented by the ``AudioData`` instance.

        If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

        If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

        Writing these bytes directly to a file results in a valid `RAW/PCM audio file <https://en.wikipedia.org/wiki/Raw_audio_format>`__.
        """
        assert (
            convert_rate is None or convert_rate > 0
        ), "Sample rate to convert to must be a positive integer"
        assert convert_width is None or (
            convert_width % 1 == 0 and 1 <= convert_width <= 4
        ), "Sample width to convert to must be between 1 and 4 inclusive"

        raw_data = self.frame_data

        # make sure unsigned 8-bit audio (which uses unsigned samples) is handled like higher sample width audio (which uses signed samples)
        if self.sample_width == 1:
            raw_data = audioop.bias(
                raw_data, 1, -128
            )  # subtract 128 from every sample to make them act like signed samples

        # resample audio at the desired rate if specified
        if convert_rate is not None and self.sample_rate != convert_rate:
            raw_data, _ = audioop.ratecv(
                raw_data,
                self.sample_width,
                1,
                self.sample_rate,
                convert_rate,
                None,
            )

        # convert samples to desired sample width if specified
        if convert_width is not None and self.sample_width != convert_width:
            if (
                convert_width == 3
            ):  # we're converting the audio into 24-bit (workaround for https://bugs.python.org/issue12866)
                raw_data = audioop.lin2lin(
                    raw_data, self.sample_width, 4
                )  # convert audio into 32-bit first, which is always supported
                try:
                    audioop.bias(
                        b"", 3, 0
                    )  # test whether 24-bit audio is supported (for example, ``audioop`` in Python 3.3 and below don't support sample width 3, while Python 3.4+ do)
                except (
                    audioop.error
                ):  # this version of audioop doesn't support 24-bit audio (probably Python 3.3 or less)
                    raw_data = b"".join(
                        raw_data[i + 1: i + 4]
                        for i in range(0, len(raw_data), 4)
                    )  # since we're in little endian, we discard the first byte from each 32-bit sample to get a 24-bit sample
                else:  # 24-bit audio fully supported, we don't need to shim anything
                    raw_data = audioop.lin2lin(
                        raw_data, self.sample_width, convert_width
                    )
            else:
                raw_data = audioop.lin2lin(
                    raw_data, self.sample_width, convert_width
                )

        # if the output is 8-bit audio with unsigned samples, convert the samples we've been treating as signed to unsigned again
        if convert_width == 1:
            raw_data = audioop.bias(
                raw_data, 1, 128
            )  # add 128 to every sample to make them act like unsigned samples again

        return raw_data

    def get_wav_data(self, convert_rate=None, convert_width=None):
        """
        Returns a byte string representing the contents of a WAV file containing the audio represented by the ``AudioData`` instance.

        If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

        If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

        Writing these bytes directly to a file results in a valid `WAV file <https://en.wikipedia.org/wiki/WAV>`__.
        """
        raw_data = self.get_raw_data(convert_rate, convert_width)
        sample_rate = (
            self.sample_rate if convert_rate is None else convert_rate
        )
        sample_width = (
            self.sample_width if convert_width is None else convert_width
        )

        # generate the WAV file contents
        with io.BytesIO() as wav_file:
            wav_writer = wave.open(wav_file, "wb")
            try:  # note that we can't use context manager, since that was only added in Python 3.4
                wav_writer.setframerate(sample_rate)
                wav_writer.setsampwidth(sample_width)
                wav_writer.setnchannels(1)
                wav_writer.writeframes(raw_data)
                wav_data = wav_file.getvalue()
            finally:  # make sure resources are cleaned up
                wav_writer.close()
        return wav_data

    def get_aiff_data(self, convert_rate=None, convert_width=None):
        """
        Returns a byte string representing the contents of an AIFF-C file containing the audio represented by the ``AudioData`` instance.

        If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

        If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

        Writing these bytes directly to a file results in a valid `AIFF-C file <https://en.wikipedia.org/wiki/Audio_Interchange_File_Format>`__.
        """
        raw_data = self.get_raw_data(convert_rate, convert_width)
        sample_rate = (
            self.sample_rate if convert_rate is None else convert_rate
        )
        sample_width = (
            self.sample_width if convert_width is None else convert_width
        )

        # the AIFF format is big-endian, so we need to convert the little-endian raw data to big-endian
        if hasattr(
            audioop, "byteswap"
        ):  # ``audioop.byteswap`` was only added in Python 3.4
            raw_data = audioop.byteswap(raw_data, sample_width)
        else:  # manually reverse the bytes of each sample, which is slower but works well enough as a fallback
            raw_data = raw_data[sample_width - 1:: -1] + b"".join(
                raw_data[i + sample_width: i: -1]
                for i in range(sample_width - 1, len(raw_data), sample_width)
            )

        # generate the AIFF-C file contents
        with io.BytesIO() as aiff_file:
            aiff_writer = aifc.open(aiff_file, "wb")
            try:  # note that we can't use context manager, since that was only added in Python 3.4
                aiff_writer.setframerate(sample_rate)
                aiff_writer.setsampwidth(sample_width)
                aiff_writer.setnchannels(1)
                aiff_writer.writeframes(raw_data)
                aiff_data = aiff_file.getvalue()
            finally:  # make sure resources are cleaned up
                aiff_writer.close()
        return aiff_data

    def get_flac_data(self, convert_rate=None, convert_width=None):
        """
        Returns a byte string representing the contents of a FLAC file containing the audio represented by the ``AudioData`` instance.

        Note that 32-bit FLAC is not supported. If the audio data is 32-bit and ``convert_width`` is not specified, then the resulting FLAC will be a 24-bit FLAC.

        If ``convert_rate`` is specified and the audio sample rate is not ``convert_rate`` Hz, the resulting audio is resampled to match.

        If ``convert_width`` is specified and the audio samples are not ``convert_width`` bytes each, the resulting audio is converted to match.

        Writing these bytes directly to a file results in a valid `FLAC file <https://en.wikipedia.org/wiki/FLAC>`__.
        """
        assert convert_width is None or (
            convert_width % 1 == 0 and 1 <= convert_width <= 3
        ), "Sample width to convert to must be between 1 and 3 inclusive"

        if (
            self.sample_width > 3 and convert_width is None
        ):  # resulting WAV data would be 32-bit, which is not convertable to FLAC using our encoder
            convert_width = 3  # the largest supported sample width is 24-bit, so we'll limit the sample width to that

        # run the FLAC converter with the WAV data to get the FLAC data
        wav_data = self.get_wav_data(convert_rate, convert_width)
        flac_converter = get_flac_converter()
        if (
            os.name == "nt"
        ):  # on Windows, specify that the process is to be started without showing a console window
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= (
                subprocess.STARTF_USESHOWWINDOW
            )  # specify that the wShowWindow field of `startup_info` contains a value
            startup_info.wShowWindow = (
                subprocess.SW_HIDE
            )  # specify that the console window should be hidden
        else:
            startup_info = None  # default startupinfo
        process = subprocess.Popen(
            [
                flac_converter,
                "--stdout",
                "--totally-silent",  # put the resulting FLAC file in stdout, and make sure it's not mixed with any program output
                "--best",  # highest level of compression available
                "-",  # the input FLAC file contents will be given in stdin
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            startupinfo=startup_info,
        )
        flac_data, stderr = process.communicate(wav_data)
        return flac_data


def get_flac_converter():
    """Returns the absolute path of a FLAC converter executable, or raises an OSError if none can be found."""
    flac_converter = shutil_which("flac")  # check for installed version first
    if flac_converter is None:  # flac utility is not installed
        base_path = os.path.dirname(
            os.path.abspath(__file__)
        )  # directory of the current module file, where all the FLAC bundled binaries are stored
        system, machine = platform.system(), platform.machine()
        if system == "Windows" and machine in {
            "i686",
            "i786",
            "x86",
            "x86_64",
            "AMD64",
        }:
            flac_converter = os.path.join(base_path, "flac-win32.exe")
        elif system == "Darwin" and machine in {
            "i686",
            "i786",
            "x86",
            "x86_64",
            "AMD64",
            "arm64",
        }:
            flac_converter = os.path.join(base_path, "flac-mac")
        elif system == "Linux" and machine in {"i686", "i786", "x86"}:
            flac_converter = os.path.join(base_path, "flac-linux-x86")
        elif system == "Linux" and machine in {"x86_64", "AMD64"}:
            flac_converter = os.path.join(base_path, "flac-linux-x86_64")
        else:  # no FLAC converter available
            raise OSError(
                "FLAC conversion utility not available - consider installing the FLAC command line application by running `apt-get install flac` or your operating system's equivalent"
            )

    # mark FLAC converter as executable if possible
    try:
        # handle known issue when running on docker:
        # run executable right after chmod() may result in OSError "Text file busy"
        # fix: flush FS with sync
        if not os.access(flac_converter, os.X_OK):
            stat_info = os.stat(flac_converter)
            os.chmod(flac_converter, stat_info.st_mode | stat.S_IEXEC)
            if "Linux" in platform.system():
                os.sync() if sys.version_info >= (3, 3) else os.system("sync")

    except OSError:
        pass

    return flac_converter


def shutil_which(pgm):
    """Python 2 compatibility: backport of ``shutil.which()`` from Python 3"""
    path = os.getenv("PATH")
    for p in path.split(os.path.pathsep):
        p = os.path.join(p, pgm)
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
