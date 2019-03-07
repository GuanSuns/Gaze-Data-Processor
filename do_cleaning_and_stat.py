# data_cleaning_and_stat.py
#
# Clean up dataset in the format of image, action, gaze, reward
# Each dataset of episode, total points
# CSV File Format: frameid,episode_id,score,duration,unclipped_reward,action,pos
# -----------------------
import data_cleaning
import data_stat


if __name__ == '__main__':
    data_cleaning.do_data_cleaning()
    data_stat.do_stat()
