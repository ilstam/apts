#!/usr/bin/env bash
# run tests and display coverage report

cd ..
coverage run --source='apts' --omit=apts/__init__.py,apts/config.py -m unittest
coverage report
