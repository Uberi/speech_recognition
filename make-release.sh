#!/usr/bin/env bash

# set up bash to handle errors more aggressively - a "strict mode" of sorts
set -e # give an error if any command finishes with a non-zero exit code
set -u # give an error if we reference unset variables
set -o pipefail # for a pipeline, if any of the commands fail with a non-zero exit code, fail the entire pipeline with that exit code

echo "Making release for SpeechRecognition-$1"

python setup.py bdist_wheel
gpg --detach-sign -a dist/SpeechRecognition-$1-*.whl
twine upload dist/SpeechRecognition-$1-*.whl dist/SpeechRecognition-$1-*.whl.asc
