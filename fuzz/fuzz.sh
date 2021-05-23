#!/bin/sh

# you need to install afl and python-afl (pip3 install python-afl)
py-afl-fuzz -m 400 -i initial-inputs-ascii/ -o fuzzing-results/ -- python ../fuzz-wrapper-ascii.py
