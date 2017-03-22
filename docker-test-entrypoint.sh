#!/bin/bash -e

# Start Gunicorn processes
echo Starting tests
pip install -r requirements-test.txt
flake8
./runtests.sh
mkdir reports -p
cp htmlcov/ reports -R
cp .coverage reports/
