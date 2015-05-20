python setup.py sdist
python setup.py bdist_wheel

echo "if the following doesn't work, make sure you have your account set up properly with `python setup.py register`"
python setup.py sdist bdist_wheel upload
