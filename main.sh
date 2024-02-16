#!/bin/bash

export PYTHONPATH=/home/michal/python-libs

env > main.trc

python3 main.py >> main.trc 2>&1

