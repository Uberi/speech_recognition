#!/usr/bin/env bash

python3 setup.py sdist

echo "if the following doesn't work, make sure you have your account set up properly with `python3 setup.py register`"
python3 setup.py sdist upload
