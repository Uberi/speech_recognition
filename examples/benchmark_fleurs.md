# Benchmark Parakeet-ja on Japanese FLEURS

This example compares NVIDIA's Parakeet-ja with DeNA's dialogue fine-tune using
`Recognizer.recognize_nemo` on CPU. It checks the clean FLEURS portion of [DeNA's
evaluation](https://engineering.dena.com/blog/2026/11/asr-finetuning-voice-dialogue/),
not the article's latency, noise, or other dataset benchmarks.

From the repository root, set up a Python 3.12 environment and install the
versions used for the macOS run:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[nemo]' 'nemo-toolkit[asr]==3.0.0' \
  torch==2.15.0 silero-vad==6.3 pyopenjtalk==0.4.1 jiwer==4.0.0

hf download google/fleurs data/ja_jp/test.tsv data/ja_jp/audio/test.tar.gz \
  --repo-type dataset --revision 70bb2e84b976b7e960aa89f1c648e09c59f894dd \
  --local-dir fleurs
hf download nvidia/parakeet-tdt_ctc-0.6b-ja parakeet-tdt_ctc-0.6b-ja.nemo \
  --revision 44edb27eea9317daf89333e75eb830db4b1cc298 --local-dir models
hf download dena-ai/parakeet-tdt_ctc-0.6b-ja-dialogue parakeet-tdt_ctc-0.6b-ja-dialogue.nemo \
  --revision 839ce2508439c6865394a18f0e0899eec925fe3d --local-dir models

python examples/benchmark_fleurs.py models/parakeet-tdt_ctc-0.6b-ja.nemo \
  fleurs/data/ja_jp/test.tsv fleurs/data/ja_jp/audio/test.tar.gz base.tsv --threads 3
python examples/benchmark_fleurs.py models/parakeet-tdt_ctc-0.6b-ja-dialogue.nemo \
  fleurs/data/ja_jp/test.tsv fleurs/data/ja_jp/audio/test.tar.gz dialogue.tsv --threads 3
```

Allow about 5.5 GB for model and audio downloads. The first reading conversion
also downloads the Open JTalk dictionary. Each run writes the exact clip IDs,
transcripts and katakana readings to its output TSV and prints the corpus-level
CER (total character edits divided by the total reference characters).

The [article and model card](https://huggingface.co/dena-ai/parakeet-tdt_ctc-0.6b-ja-dialogue)
specify 300 FLEURS utterances, Silero VAD, and katakana reading CER, but do not
identify the split, utterance list, VAD settings or reading normalizer.
This example samples 300 recordings from the public Japanese test split using
seed 0 by default. If the evaluation manifest becomes available, supply its
rows as the input TSV (FLEURS format, no header) and set `--count` to the
number of rows to use them all.

The example gates 1-second windows with Silero VAD 6.3's default settings. If
any window passes, it sends the full recording to `recognize_nemo` once;
otherwise it scores an empty transcript. It converts the FLEURS float WAV
to PCM16 for `AudioFile`. For reading CER it applies Unicode NFKC, removes
whitespace, punctuation and symbols, and uses Open JTalk to convert text to
katakana, then normalizes again. This is not an exact recreation of DeNA's
production VAD and text processing.
