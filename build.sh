#!/usr/bin/env bash

echo "if the following doesn't work, make sure you have your account set up properly with `python3 setup.py register`"

# make sure we use GnuPG 2 rather than GnuPG 1
sudo ln "$(which gpg2)" dist/gpg
PATH=./dist:$PATH python3 setup.py sdist upload --sign
