# data_cleaning.py
#
# Clean up dataset in the format of image, action, gaze, reward
# Each dataset of episode, total points
# CSV File Format: frameid,episode_id,score,duration,unclipped_reward,action,pos
# -----------------------

import os
import re
import sys
import time
import data_reader
import utils


def add_to_data_line(frameid, frameid2data, data_line='', separator=','):
    if frameid in frameid2data and frameid2data[frameid] is not None:
        data_line = data_line + str(frameid2data[frameid]) + separator
    else:
        data_line = data_line + 'null' + separator
    return data_line


def save_gaze_data_asc_file_to_csv(fname, saved_dir, is_include_title=True, saved_as_plain_txt=True):
    gaze_data = data_reader.read_gaze_data_asc_file(fname)
    frameid2pos = gaze_data[0]
    frameid2action = gaze_data[1]
    frameid2duration = gaze_data[2]
    frameid2unclipped_reward = gaze_data[3]
    frameid2episode = gaze_data[4]
    frameid2score = gaze_data[5]
    frameid_list = gaze_data[6]
    file_meta_data = gaze_data[7]

    # create the saved_dir if not exists
    if not os.path.exists(saved_dir):
        os.makedirs(saved_dir)

    # create the csv file (saved as txt file)
    csv_fname = os.path.basename(fname).split('.')[0]
    if saved_as_plain_txt:
        csv_fname += '.txt'
    else:
        csv_fname += '.csv'
    csv_fpath = os.path.join(saved_dir, csv_fname)
    csv_file = open(csv_fpath, 'w')

    # define the separator in csv file
    separator = ','
    pos_separator = ','

    # write the title information if is_include_title is set
    if is_include_title:
        titles = 'frame_id,episode_id,score,duration(ms),unclipped_reward,action,gaze_positions\n'
        csv_file.write(titles)

    # save the data to the file
    for frameid in frameid_list:
        # write the frameid
        data_line = str(frameid[0]) + '_' + str(frameid[1]) + separator
        # write the episode id
        data_line = add_to_data_line(frameid, frameid2episode, data_line, separator)
        # write the score
        data_line = add_to_data_line(frameid, frameid2score, data_line, separator)
        # write the duration
        data_line = add_to_data_line(frameid, frameid2duration, data_line, separator)
        # write the unclipped_reward
        data_line = add_to_data_line(frameid, frameid2unclipped_reward, data_line, separator)
        # write the action
        data_line = add_to_data_line(frameid, frameid2action, data_line, separator)
        # write the pos (use space as separator)
        if frameid in frameid2pos:
            pos_list = frameid2pos[frameid]
            n_pos = len(pos_list)
            if n_pos == 0:
                data_line += 'null'
            else:
                for i in range(0, n_pos):
                    data_line = data_line + format(pos_list[i][0]/8.0, '.2f') + pos_separator + format(pos_list[i][1]/4.0, '.2f')
                    if i < n_pos-1:
                        data_line += pos_separator
        else:
            data_line += 'null'
        # write the line to the csv file
        csv_file.write(data_line + '\n')
    # close the file
    csv_file.close()

    # return the meta data
    return file_meta_data


def save_asc_files_in_dir_to_csv(asc_dir, saved_dir, fname_regex='.', is_include_title=True, saved_as_plain_txt=True, saved_to_excel=True):
    # create the saved_dir if not exists (to store meta data)
    if not os.path.exists(saved_dir):
        os.makedirs(saved_dir)

    str_timestamp = str(int(time.time() * 1000))
    fname_meta_data = str_timestamp + '_meta.txt'
    meta_fpath = os.path.join(saved_dir, fname_meta_data)
    meta_file = open(meta_fpath, 'w')

    meta_data_dict = {}
    fname_meta_excel = str_timestamp + '_meta.xlsx'

    fname_format = re.compile(fname_regex)
    for fname in os.listdir(asc_dir):
        if fname.endswith(".asc") and fname_format.match(fname):
            fpath = os.path.join(asc_dir, fname)
            print('Processing asc file: ' + fpath)
            file_meta_data = save_gaze_data_asc_file_to_csv(fpath, saved_dir, is_include_title, saved_as_plain_txt)
            # write the meta data
            trial_id = int(fname.split('_')[0])
            meta_file.write('\'' + str(trial_id) + '\'' + ':' + str(file_meta_data) + '\n')
            meta_data_dict[trial_id] = file_meta_data
    # close the meta data file
    meta_file.close()
    # save the mata data to excel file
    if saved_to_excel:
        utils.save_trials_data_to_excel(saved_dir, fname_meta_excel, meta_data_dict)
    return meta_data_dict


def do_data_cleaning():
    data_dir = '/Users/lguan/Documents/Study/Research/Gaze-Dataset/data'
    csv_dir = '/Users/lguan/Documents/Study/Research/Gaze-Dataset/data_processing/csv'
    save_asc_files_in_dir_to_csv(data_dir, csv_dir)


def do_testing():
    testing_csv_dir = '/Users/lguan/Documents/Study/Research/Gaze-Dataset/testing_csv_dir'
    testing_data_dir = '/Users/lguan/Documents/Study/Research/Gaze-Dataset/testing_data_dir'
    save_asc_files_in_dir_to_csv(testing_data_dir, testing_csv_dir)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python data_cleaning.py source_dir dest_dir [whether to include titles in txt file]')
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

    save_asc_files_in_dir_to_csv(source_dir, dest_dir, is_include_title=include_title)


