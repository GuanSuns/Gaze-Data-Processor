# data_stat.py
#
# CSV File Format: frameid,episode_id,score,duration,unclipped_reward,action,pos
# -----------------------

import os
import re
import data_reader
import utils


def do_per_game_stat(csv_dir, fname_regex='.', is_ignore_null=False):
    # stat data
    cnt_file = 0
    cnt_frame = 0
    cnt_episode = 0
    game_play_time = 0
    lowest_score = float('inf')
    highest_score = -float('inf')
    lowest_cumulative_reward = float('inf')
    highest_cumulative_reward = -float('inf')

    fname_format = re.compile(fname_regex)
    for fname in os.listdir(csv_dir):
        if fname_format.match(fname):
            print('Processing csv file: ' + fname)
            cnt_file += 1

            # read data from the csv file
            fpath = os.path.join(csv_dir, fname)
            gaze_data = data_reader.read_gaze_data_csv_file(fpath)
            frameid2duration = gaze_data[2]
            frameid2unclipped_reward = gaze_data[3]
            frameid2episode = gaze_data[4]
            frameid2score = gaze_data[5]
            frameid_list = gaze_data[6]

            episode_score = 0
            episode_time = 0
            episode_cumulative_reward = 0
            episode_frame = 0
            current_episode = None

            for frameid in frameid_list:
                duration = frameid2duration[frameid]
                unclipped_reward = frameid2unclipped_reward[frameid]
                episode_id = frameid2episode[frameid]
                score = frameid2score[frameid]

                if is_ignore_null:
                    if duration is None or unclipped_reward is None or episode_id is None or score is None:
                        break

                # if it's a new episode
                if episode_id is not None and episode_id != current_episode:
                    # compute the stat data for previous episode
                    game_play_time += episode_time
                    lowest_cumulative_reward = min(lowest_cumulative_reward, episode_cumulative_reward)
                    highest_cumulative_reward = max(highest_cumulative_reward, episode_cumulative_reward)
                    cnt_frame += episode_frame
                    cnt_episode += 1
                    lowest_score = min(lowest_score, episode_score)
                    highest_score = max(highest_score, episode_score)

                    # reset the stat variables
                    episode_time = utils.set_value_by_int(0, duration)
                    episode_frame = 1
                    episode_score = utils.set_value_by_int(0, score)
                    episode_cumulative_reward = utils.set_value_by_int(0, unclipped_reward)
                    current_episode = episode_id
                # if it's still in the same episode
                else:
                    episode_time = utils.increment_by_int(episode_time, duration)
                    episode_frame += 1
                    episode_cumulative_reward = utils.increment_by_int(episode_cumulative_reward, unclipped_reward)
                    episode_score = utils.set_value_by_int(episode_score, score)

            # compute the stat data for the last episode
            game_play_time += episode_time
            lowest_cumulative_reward = min(lowest_cumulative_reward, episode_cumulative_reward)
            highest_cumulative_reward = max(highest_cumulative_reward, episode_cumulative_reward)
            cnt_frame += episode_frame
            cnt_episode += 1
            lowest_score = min(lowest_score, episode_score)
            highest_score = max(highest_score, episode_score)

    # display the result
    print('\n-------------------------------------')
    print('-------------------------------------')
    print('Statistics results from %d files' % cnt_file)
    print('Episodes: %d' % cnt_episode)
    print('Frames: %d' % cnt_frame)
    print('Game play time: %d' % game_play_time)
    print('Lowest cumulative reward: %d' % lowest_cumulative_reward)
    print('Highest cumulative reward: %d' % highest_cumulative_reward)
    print('Lowest score: %d' % lowest_score)
    print('Highest score: %d' % highest_score)
    print('-------------------------------------')
    print('-------------------------------------')


def display_time_score(csv_dir, fname_regex='.'):
    time_score_pair_list = []
    fname_format = re.compile(fname_regex)
    for fname in os.listdir(csv_dir):
        if fname_format.match(fname):
            print('Processing csv file: ' + fname)

            # read data from the csv file
            fpath = os.path.join(csv_dir, fname)
            gaze_data = data_reader.read_gaze_data_csv_file(fpath)
            frameid2duration = gaze_data[2]
            frameid2episode = gaze_data[4]
            frameid2score = gaze_data[5]
            frameid_list = gaze_data[6]

            episode_score = 0
            current_episode = None
            total_time = 0


if __name__ == '__main__':
    do_per_game_stat('/Users/lguan/Documents/Study/Research/Gaze-Dataset/testing_csv_dir')

