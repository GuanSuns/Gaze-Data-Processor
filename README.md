# Gaze-Data-Processor

## Description
The python program to clean and process the gaze data

## Transform asc files to txt (or csv) files
- **Usage**: python data_cleaning.py  source_dir  dest_dir  \[whether to include titles in txt file\]
    - It will transform all the asc files under the source dir to txt (or csv) files, and save the generated files to the dest_dir
    - An Excel file that contains the meta data of each trial will also be generated under the dest_dir
- **Source**: data_cleaning.py

## Statistics

- **Source**: data_stat.py
    - Function do\_per\_game\_stat is not used currently, which aims to do stat for each game (one game includes many trials)
     