# data_cleaning.py
#
# Clean up dataset in the format of image, action, gaze, reward
# Each dataset of episode, total points
# -----------------------

import os, re, threading, time
import numpy as np
from IPython import embed
from scipy import misc


def read_gaze_data_asc_file(fname):
    """ This function reads a ASC file and returns
        a dictionary mapping frame ID to a list of gaze positions,
        a dictionary mapping frame ID to action """

    with open(fname, 'r') as f:
        lines = f.readlines()
    frameid, xpos, ypos = 'BEFORE-FIRST-FRAME', None, None
    frameid2pos = {frameid: []}
    frameid2action = {frameid: None}
    frameid2duration = {frameid: None}
    frameid2unclipped_reward = {frameid: None}
    frameid2episode = {frameid: None}
    frameid2score = {frameid: None}
    # frame id list (exclude the 'BEFORE-FIRST-FRAME')
    frameid_list = []
    start_timestamp = 0
    # regex for starting message
    scr_msg = re.compile(r"MSG\s+(\d+)\s+SCR_RECORDER FRAMEID (\d+) UTID (\w+)")
    # regex for floating point numbers
    freg = r"[-+]?[0-9]*\.?[0-9]+"
    # regex for gaze message
    gaze_msg = re.compile(r"(\d+)\s+(%s)\s+(%s)" % (freg, freg))
    # regex for action message
    act_msg = re.compile(r"MSG\s+(\d+)\s+key_pressed atari_action (\d+)")
    # regex for reward message
    reward_msg = re.compile(r"MSG\s+(\d+)\s+reward (\d+)")
    # regex for episode message
    episode_msg = re.compile(r"MSG\s+(\d+)\s+episode (\d+)")
    # regex for score message
    score_msg = re.compile(r"MSG\s+(\d+)\s+score (\d+)")

    for (i, line) in enumerate(lines):
        match_sample = gaze_msg.match(line)
        if match_sample:
            timestamp, xpos, ypos = match_sample.group(1), match_sample.group(2), match_sample.group(3)
            xpos, ypos = float(xpos), float(ypos)
            frameid2pos[frameid].append((xpos, ypos))
            continue

        match_scr_msg = scr_msg.match(line)
        # when a new id is encountered
        if match_scr_msg:
            old_frameid = frameid
            timestamp, frameid, UTID = match_scr_msg.group(1), match_scr_msg.group(2), match_scr_msg.group(3)
            frameid2duration[old_frameid] = int(timestamp) - start_timestamp
            start_timestamp = int(timestamp)
            frameid = make_unique_frame_id(UTID, frameid)
            frameid_list.append(frameid)
            frameid2pos[frameid] = []
            frameid2action[frameid] = None
            continue

        match_action = act_msg.match(line)
        if match_action:
            timestamp, action_label = match_action.group(1), match_action.group(2)
            if frameid2action[frameid] is None:
                frameid2action[frameid] = int(action_label)
            else:
                print ("Warning: there is more than 1 action for frame id %s. Not supposed to happen." % str(frameid))
            continue

        match_reward = reward_msg.match(line)
        if match_reward:
            timestamp, reward = match_reward.group(1), match_reward.group(2)
            if frameid not in frameid2unclipped_reward:
                frameid2unclipped_reward[frameid] = int(reward)
            else:
                print ("Warning: there is more than 1 reward for frame id %s. Not supposed to happen." % str(frameid))
            continue

        match_episode = episode_msg.match(line)
        if match_episode:
            timestamp, episode = match_episode.group(1), match_episode.group(2)
            assert frameid not in frameid2episode, "ERROR: there is more than 1 episode for frame id %s. Not supposed to happen." % str(frameid)
            frameid2episode[frameid] = int(episode)
            continue

        match_score = score_msg.match(line)
        if match_score:
            timestamp, score = match_score.group(1), match_score.group(2)
            assert frameid not in frameid2score, "ERROR: there is more than 1 score for frame id %s. Not supposed to happen." % str(
                frameid)
            frameid2score[frameid] = int(score)
            continue

    frameid2pos[frameid] = []   # throw out gazes after the last frame, because the game has ended but eye tracker keeps recording

    if len(frameid2pos) < 1000:     # simple sanity check
        print ("Warning: did you provide the correct ASC file? Because the data for only %d frames is detected" % (len(frameid2pos)))
        raw_input("Press any key to continue")

    few_cnt = 0
    for v in frameid2pos.values():
        if len(v) < 10:
            few_cnt += 1
    print ("Warning:  %d frames have less than 10 gaze samples. (%.1f%%, total frame: %d)" %
           (few_cnt, 100.0*few_cnt/len(frameid2pos), len(frameid2pos)))

    return frameid2pos, frameid2action, frameid2duration, frameid2unclipped_reward, frameid2episode, frameid2score, frameid_list


def make_unique_frame_id(UTID, frameid):
    # noinspection PyRedundantParentheses
    return (UTID, int(frameid))


def add_to_data_line(frameid, frameid2data, data_line='', separator=','):
    if frameid in frameid2data:
        data_line = data_line + str(frameid2data[frameid]) + separator
    else:
        data_line = data_line + 'null' + separator
    return data_line


def save_gaze_data_asc_file_to_csv(fname, saved_dir, is_include_title=False, saved_as_plain_txt=True):
    gaze_data = read_gaze_data_asc_file(fname)
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
    csv_fpath = saved_dir + '/' + csv_fname
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


if __name__ == '__main__':
    save_gaze_data_asc_file_to_csv('/Users/lguan/Documents/Study/Research/Gaze-Dataset/data/191_JAW_9955253_Jun-25-14-35-04.asc', '/Users/lguan/Documents/Study/Research/Gaze-Dataset/data_cleaning/csv', True)

