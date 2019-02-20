# data_cleaning.py
#
# Clean up dataset in the format of image, action, gaze, reward
# Each dataset of episode, total points
# -----------------------

import os
import data_reader


def add_to_data_line(frameid, frameid2data, data_line='', separator=','):
    if frameid in frameid2data and frameid2data[frameid] is not None:
        data_line = data_line + str(frameid2data[frameid]) + separator
    else:
        data_line = data_line + 'null' + separator
    return data_line


def save_gaze_data_asc_file_to_csv(fname, saved_dir, is_include_title=False, saved_as_plain_txt=True):
    gaze_data = data_reader.read_gaze_data_asc_file(fname)
    frameid2pos = gaze_data[0]
    frameid2action = gaze_data[1]
    frameid2duration = gaze_data[2]
    frameid2unclipped_reward = gaze_data[3]
    frameid2episode = gaze_data[4]
    frameid2score = gaze_data[5]
    frameid_list = gaze_data[6]

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
    pos_separator = ' '

    # write the title information if is_include_title is set
    if is_include_title:
        titles = 'frameid,episode_id,score,duration,unclipped_reward,action,pos\n'
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
                    data_line = data_line + str(pos_list[i][0]) + pos_separator + str(pos_list[i][1])
                    if i < n_pos-1:
                        data_line += pos_separator
        else:
            data_line += 'null'
        # write the line to the csv file
        csv_file.write(data_line + '\n')
    # close the file
    csv_file.close()


def save_asc_file_in_dir_to_csv(dir, saved_dir, is_include_title=False, saved_as_plain_txt=True):
    for fname in os.listdir(dir):
        if fname.endswith(".asc"):
            fpath = os.path.join(dir, fname)
            print('Processing asc file: ' + fpath)
            save_gaze_data_asc_file_to_csv(fpath, saved_dir, is_include_title, saved_as_plain_txt)


if __name__ == '__main__':
    save_asc_file_in_dir_to_csv('/Users/lguan/Documents/Study/Research/Gaze-Dataset/data_dir', '/Users/lguan/Documents/Study/Research/Gaze-Dataset/data_processing/csv')

