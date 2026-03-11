import argparse
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen

from tqdm import tqdm


def download_vosk_model(url: str, model_dir: str) -> None:
    model_filename = os.path.basename(url)
    model_name = os.path.splitext(model_filename)[0]

    print(f"Downloading model {model_filename} ...")
    with urlopen(url) as response:
        total_size = int(response.headers.get("Content-Length", 0))
        with tempfile.TemporaryDirectory() as temp_dir:
            download_path = os.path.join(temp_dir, model_filename)
            with open(download_path, "wb") as f, tqdm(
                total=total_size, unit="B", unit_scale=True
            ) as pbar:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    pbar.update(len(chunk))

            print("Unzip model...")
            with zipfile.ZipFile(download_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            extracted_dir = os.path.join(temp_dir, model_name)
            if os.path.exists(model_dir):
                shutil.rmtree(model_dir)
            shutil.copytree(extracted_dir, model_dir)

    print(f"Setup complete! Model is placed in the directory: {model_dir}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="sprc")
    subparsers = parser.add_subparsers(dest="command")

    download_parser = subparsers.add_parser("download")
    download_subparsers = download_parser.add_subparsers(dest="target")

    vosk_parser = download_subparsers.add_parser("vosk")
    vosk_parser.add_argument(
        "--url",
        default="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
    )

    def _download_vosk(args):
        download_vosk_model(
            args.url, str(Path(__file__).parent / "models" / "vosk")
        )

    vosk_parser.set_defaults(func=_download_vosk)

    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
