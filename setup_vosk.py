# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests",
#     "tqdm",
# ]
# ///
import os
import shutil
import tempfile
import zipfile

import requests
from tqdm import tqdm


def setup_vosk_model(model_url: str, model_dir: str) -> None:
    model_filename = os.path.basename(model_url)
    model_name = os.path.splitext(model_filename)[0]

    print(f"Downloading model {model_filename} ...")
    response = requests.get(model_url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))

    with tempfile.TemporaryDirectory() as temp_dir:
        download_path = os.path.join(temp_dir, model_filename)
        with open(download_path, "wb") as f:
            with tqdm(total=total_size, unit="B", unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
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


if __name__ == "__main__":
    model_url = (
        "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    )
    setup_vosk_model(model_url, "model")
