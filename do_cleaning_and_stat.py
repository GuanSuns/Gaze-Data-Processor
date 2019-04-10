# data_cleaning_and_stat.py
#
# Clean up dataset in the format of image, action, gaze, reward
# Each dataset of episode, total points
# CSV File Format: frameid,episode_id,score,duration,unclipped_reward,action,pos
# -----------------------
import sys
import data_cleaning
import data_stat


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python data_cleaning_and_stat.py source_dir dest_dir [whether to include titles in txt file]')
        exit(1)

    source_dir = sys.argv[1]
    dest_dir = sys.argv[2]
    include_title = True
    if len(sys.argv) == 4:
        if sys.argv[3].lower() == 'true':
            include_title = True
        elif sys.argv[3].lower() == 'false':
            include_title = False
        else:
            print('For the third argument, please use True or False')
            exit(1)

    print('#'*20)
    data_cleaning.save_asc_files_in_dir_to_csv(source_dir, dest_dir, is_include_title=include_title)
    print('#' * 20)
    data_stat.do_per_trial_stat(dest_dir, dest_dir)
    print('#' * 20)
