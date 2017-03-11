#!/usr/bin/env bash

# set up bash to handle errors more aggressively - a "strict mode" of sorts
set -e # give an error if any command finishes with a non-zero exit code
set -u # give an error if we reference unset variables
set -o pipefail # for a pipeline, if any of the commands fail with a non-zero exit code, fail the entire pipeline with that exit code

echo "if the following doesn't work, make sure you have your account set up properly with 'python3 setup.py register'"

# make sure we use GnuPG 2 rather than GnuPG 1
sudo ln --force "$(which gpg2)" dist/gpg
PATH=./dist:$PATH python3 setup.py bdist_wheel upload --sign
