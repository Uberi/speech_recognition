import argparse
import csv
import io
import random
import statistics
import tarfile
import time
import unicodedata

import speech_recognition as sr


def select_clips(reference_tsv, count, seed):
    with open(reference_tsv, encoding="utf-8", newline="") as source:
        rows = csv.reader(source, delimiter="\t", quoting=csv.QUOTE_NONE)
        references = {filename: reference for _, filename, reference, *_ in rows}
    if not 1 <= count <= len(references):
        raise ValueError(f"Expected --count between 1 and {len(references)}, got {count}")
    if count == len(references):
        return references
    return dict(random.Random(seed).sample(list(references.items()), count))


def normalize(text):
    text = unicodedata.normalize("NFKC", text)
    return "".join(
        char for char in text
        if not char.isspace() and unicodedata.category(char)[0] not in "PS"
    )


def reading(text):
    from pyopenjtalk import g2p

    text = normalize(text)
    return normalize(g2p(text, kana=True)) if text else ""


def read_recordings(archive, selected, vad_model):
    import soundfile
    import torch
    from silero_vad import get_speech_timestamps

    recordings = {}
    with tarfile.open(archive, mode="r|gz") as tar:
        for member in tar:
            filename = member.name.removeprefix("test/")
            if not member.isfile() or filename not in selected:
                continue
            with tar.extractfile(member) as audio_file:
                waveform, rate = soundfile.read(io.BytesIO(audio_file.read()), dtype="float32")
            if rate != 16000 or waveform.ndim != 1:
                raise ValueError(f"Expected 16 kHz mono audio: {member.name}")
            speech_detected = any(
                get_speech_timestamps(window, vad_model, sampling_rate=rate)
                for window in torch.from_numpy(waveform).split(rate)
            )
            with io.BytesIO() as wav:
                soundfile.write(wav, waveform, rate, format="WAV", subtype="PCM_16")
                wav.seek(0)
                with sr.AudioFile(wav) as source:
                    audio = sr.Recognizer().record(source)
            recordings[filename] = audio, speech_detected
    missing = selected.keys() - recordings.keys()
    if missing:
        raise ValueError(f"Audio archive is missing {len(missing)} selected recordings, e.g. {min(missing)}")
    return recordings


def recognize_clip(recognizer, audio, speech_detected, model):
    if not speech_detected:
        return ""
    return recognizer.recognize_nemo(audio, model=model)


def main():
    parser = argparse.ArgumentParser(description="Benchmark a NeMo checkpoint on Japanese FLEURS.")
    parser.add_argument("model", help="Local .nemo checkpoint")
    parser.add_argument("reference_tsv", help="Japanese FLEURS test.tsv")
    parser.add_argument("audio_archive", help="Japanese FLEURS audio/test.tar.gz")
    parser.add_argument("output", help="Path for the per-utterance TSV")
    parser.add_argument("--count", type=int, default=300, help="Number of utterances")
    parser.add_argument("--seed", type=int, default=0, help="FLEURS sampling seed")
    parser.add_argument("--threads", type=int, default=6, help="PyTorch CPU threads")
    args = parser.parse_args()

    from jiwer import process_characters
    import torch
    from nemo.collections.asr.models import ASRModel
    from silero_vad import load_silero_vad

    torch.set_num_threads(args.threads)
    selected = select_clips(args.reference_tsv, args.count, args.seed)
    recordings = read_recordings(args.audio_archive, selected, load_silero_vad())
    start = time.perf_counter()
    model = ASRModel.restore_from(args.model, map_location="cpu")
    print(f"model={args.model} device={model.device} load_seconds={time.perf_counter() - start:.3f}")

    recognizer = sr.Recognizer()
    references, hypotheses, latencies = [], [], []
    audio_seconds = 0.0
    gated = 0
    with open(args.output, "w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t")
        writer.writerow([
            "clip", "reference", "hypothesis", "reference_reading", "hypothesis_reading",
            "speech_detected", "audio_seconds", "inference_seconds",
        ])
        for index, (filename, reference) in enumerate(selected.items(), 1):
            audio, speech_detected = recordings[filename]
            duration = len(audio.frame_data) / audio.sample_width / audio.sample_rate
            start = time.perf_counter()
            hypothesis = recognize_clip(recognizer, audio, speech_detected, model)
            elapsed = time.perf_counter() - start
            ref_reading, hyp_reading = reading(reference), reading(hypothesis)
            references.append(ref_reading)
            hypotheses.append(hyp_reading)
            latencies.append(elapsed)
            audio_seconds += duration
            gated += not speech_detected
            writer.writerow([
                filename, reference, hypothesis, ref_reading, hyp_reading,
                speech_detected, duration, elapsed,
            ])
            if index == 1 or index % 25 == 0:
                print(f"{index}/{len(selected)} clip={filename} inference_seconds={elapsed:.3f}", flush=True)

    scores = process_characters(references, hypotheses)
    errors = scores.substitutions + scores.deletions + scores.insertions
    reference_chars = scores.hits + scores.substitutions + scores.deletions
    print(
        f"count={len(latencies)} gated={gated} reading_CER={scores.cer:.4%} "
        f"errors={errors} reference_chars={reference_chars}"
    )
    print(
        f"audio_seconds={audio_seconds:.3f} inference_seconds={sum(latencies):.3f} "
        f"median_clip_seconds={statistics.median(latencies):.3f} "
        f"realtime_factor={sum(latencies) / audio_seconds:.4f}"
    )


if __name__ == "__main__":
    main()
