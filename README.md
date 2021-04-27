# PA193_Security_Certificate_Parser

![Python version](https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9-blue)
![Build](https://img.shields.io/github/checks-status/BorysekOndrej/PA193_Security_Certificate_Parser/main)

Repository for a school project from PA193.

[Link](https://is.muni.cz/auth/el/fi/jaro2021/PA193/um/project/pa193_project_overview_2021.pdf) to the semestral  project assignment. 

The submodule `dataset` contains content of zip folder dataset as available from [IS](https://is.muni.cz/auth/el/fi/jaro2021/PA193/um/project/pa193_dataset.zip).


#### Quickstart

```sh
git clone https://github.com/BorysekOndrej/PA193_Security_Certificate_Parser.git
cd PA193_Security_Certificate_Parser

git submodule init
git submodule update

python3 -m pip install -r requirements.txt

# Print usage help
python3 cli.py -h

# For a single file:
python3 cli.py -i "dataset/dataset/NSCIB-CC-0095534-STLite.txt" -o "results/jsons/NSCIB-CC-0095534-STLite.json" --correct_file "dataset/dataset/NSCIB-CC-0095534-STLite.json"

# For a whole folder:
python3 cli.py -I "dataset/dataset/" -O "results/jsons/" --correct_folder "dataset/dataset/"

```

Command to update the submodules (currently just the dataset) link to HEAD of remote.
If you want to also push this update to server, don't forget commit and push.

```sh
git submodule update --recursive --remote
```
