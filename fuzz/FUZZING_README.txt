You need to install AFL fuzzer and the python-afl pip package.
To fuzz single-core just run ./fuzz.sh
To fuzz on multiple cores you need to run multiple py-afl-fuzz instances.

Run the first (master) instance using:
py-afl-fuzz -m 400 -M fuzzer01 -i initial-inputs-ascii/ -o fuzzing-results/ -- python ../fuzz-wrapper-ascii.py

Then run arbitrary number of slave nodes using:
py-afl-fuzz -m 400 -S fuzzer02 -i initial-inputs-ascii/ -o fuzzing-results/ -- python ../fuzz-wrapper-ascii.py

Dont forget to assign unique names for each slave (here "fuzzer02").
