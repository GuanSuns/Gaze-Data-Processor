# data_stat.py
#
# CSV File Format: frameid,episode_id,score,duration,unclipped_reward,action,pos
# -----------------------

import os
import re
import data_reader
import utils
import xlsxwriter


def do_per_game_stat(csv_dir, fname_regex='.*_.*_.*\.txt', is_ignore_null=False, func_fname_condition=None):
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
            # skip the file if it doesn't meet the file name condition
            if (func_fname_condition is not None) and (not func_fname_condition(fname)):
                continue

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
                    if current_episode is not None:
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


def do_per_trial_stat(csv_dir, saved_dir=None, fname_regex='.*_.*_.*\.txt', is_ignore_null=False, func_fname_condition=None):
    # stat data
    stat_dict = {}
    cnt_file = 0

    fname_format = re.compile(fname_regex)
    for fname in os.listdir(csv_dir):
        if fname_format.match(fname):
            # skip the file if it doesn't meet the file name condition
            if (func_fname_condition is not None) and (not func_fname_condition(fname)):
                continue

            trial_id = int(fname.split('_')[0])
            print('Processing trial ' + str(trial_id) + ' in csv file: ' + fname)
            cnt_file += 1

            # read data from the csv file
            fpath = os.path.join(csv_dir, fname)
            gaze_data = data_reader.read_gaze_data_csv_file(fpath)
            frameid2duration = gaze_data[2]
            frameid2unclipped_reward = gaze_data[3]
            frameid2episode = gaze_data[4]
            frameid2score = gaze_data[5]
            frameid_list = gaze_data[6]

            trial_lowest_score = float('inf')
            trial_highest_score = -float('inf')
            trial_lowest_cumulative_reward = float('inf')
            trial_highest_cumulative_reward = -float('inf')
            trial_stat_dict = {}

            episode_max_score = -float('inf')
            episode_max_cumulative_reward = -float('inf')
            episode_time = 0
            episode_cumulative_reward = 0
            episode_frame = 0
            current_episode = None

            cnt_frame = 0
            cnt_episode = 0
            game_play_time = 0

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
                    if episode_max_cumulative_reward != -float('inf'):
                        trial_lowest_cumulative_reward = min(trial_lowest_cumulative_reward, episode_max_cumulative_reward)
                    trial_highest_cumulative_reward = max(trial_highest_cumulative_reward, episode_max_cumulative_reward)
                    if episode_max_score != -float('inf'):
                        trial_lowest_score = min(trial_lowest_score, episode_max_score)
                    trial_highest_score = max(trial_highest_score, episode_max_score)
                    cnt_frame += episode_frame
                    if current_episode is not None:
                        cnt_episode += 1
                    game_play_time += episode_time

                    # reset the stat variables
                    episode_time = utils.set_value_by_int(0, duration)
                    episode_frame = 1
                    episode_max_score = utils.set_value_by_int(0, score)
                    episode_max_cumulative_reward = utils.set_value_by_int(0, unclipped_reward)
                    episode_cumulative_reward = unclipped_reward
                    current_episode = episode_id
                # if it's still in the same episode
                else:
                    episode_time = utils.increment_by_int(episode_time, duration)
                    episode_frame += 1
                    episode_cumulative_reward = utils.increment_by_int(episode_cumulative_reward, unclipped_reward)
                    episode_max_cumulative_reward = max(episode_max_cumulative_reward, episode_cumulative_reward)
                    episode_max_score = max(episode_max_score, utils.set_value_by_int(episode_max_score, score))

            # compute the stat data for the last episode
            game_play_time += episode_time
            cnt_frame += episode_frame
            cnt_episode += 1
            trial_lowest_cumulative_reward = min(trial_lowest_cumulative_reward, episode_max_cumulative_reward)
            trial_highest_cumulative_reward = max(trial_highest_cumulative_reward, episode_max_cumulative_reward)
            trial_lowest_score = min(trial_lowest_score, episode_max_score)
            trial_highest_score = max(trial_highest_score, episode_max_score)

            # display the result
            trial_stat_dict['highest_score'] = trial_highest_score
            trial_stat_dict['lowest_score'] = trial_lowest_score
            trial_stat_dict['highest_cumulative_score'] = trial_highest_cumulative_reward
            trial_stat_dict['lowest_cumulative_score'] = trial_lowest_cumulative_reward
            trial_stat_dict['total_episode'] = cnt_episode
            trial_stat_dict['total_frame'] = cnt_frame
            trial_stat_dict['total_game_play_time'] = game_play_time
            stat_dict[trial_id] = trial_stat_dict
            print('Statistics results from trial %d: ' % trial_id)
            print(trial_stat_dict)
            print(' ')

    print('\n----------------------------------')
    print('Done statistics from %d files.' % cnt_file)
    print('----------------------------------')

    # save the data to excel then return
    if saved_dir is not None:
        save_stat_data_to_excel(saved_dir, stat_dict)
    return stat_dict


def save_stat_data_to_excel(saved_dir, stat_dict):
    if not os.path.exists(saved_dir):
        os.makedirs(saved_dir)
    fname = 'stat_data.xlsx'
    fpath = os.path.join(saved_dir, fname)
    workbook = xlsxwriter.Workbook(fpath)
    worksheet = workbook.add_worksheet()

    row = 0
    col = 0
    for trial_id in stat_dict.keys():
        # write column names first
        if row == 0:
            worksheet.write(0, 0, 'trial_id')
            col += 1
            for col_name in stat_dict[trial_id].keys():
                worksheet.write(row, col, col_name)
                col += 1
        # write the data
        row += 1
        col = 0
        worksheet.write(row, col, trial_id)

        trial_stat = stat_dict[trial_id]
        for col_name, value in trial_stat.items():
            worksheet.write(row, col+1, value)
            col += 1
    # close the file and save the data
    workbook.close()


def fname_condition(fname):
    trial_id = int(fname.split('_')[0])
    return trial_id > 178


if __name__ == '__main__':
    data_dir = '/Users/lguan/Documents/Study/Research/Gaze-Dataset/data_processing/csv'
    do_per_trial_stat(csv_dir=data_dir, saved_dir=data_dir, func_fname_condition=fname_condition)



