# Gaze-Data-Processor

## Description
The python program to clean and process the gaze data

## Transform asc files to txt (or csv) files
- **Usage**: python data_cleaning.py  source_dir  dest_dir  \[whether to include titles in txt file\]
    - It will transform all the asc files under the source dir to txt (or csv) files, and save the generated files to the dest_dir
    - An Excel file that contains the meta data of each trial will also be generated under the dest_dir
- **Source Code**: data_cleaning.py

## Statistics (Use the generated txt/csv files)
- **Usage**: python data_stat.py source_dir saved_dir
    - It will do statistics analysis for each trial (csv/txt files under source_dir) and save the result in an Excel file under the saved_dir
- **Source Code**: data_stat.py
    - Function do\_per\_game\_stat is not used currently, which aims to do stat for each game (one game includes many trials)


## Replay
- **Usage**: python data\_visualizer.py tar\_fname csv\_fname
	- tar\_fname: the path to the tar file including the png files of each frame
	- csv\_fname: the path to the txt (csv) file containing the data of each trial.
- **Control**: 
    - You can control the replay using keyboard. Try pressing esc/space/up/down/left/right.
    - Use esc to safely terminate the program.
- **Source Code**: data\_visualizer.py


## All in one command
- **Usage**: python do\_cleaning\_and\_stat.py source_dir  dest_dir  \[whether to include titles in txt file\]
    - It will do both data cleaning (processing) and statistics analysis
    - source_dir: the directory saving the asc files
    - dest_dir: the directory saving the csv/txt and results (Excel) files.
- **Source Code**: do\_cleaning\_and\_stat.py
  