# data_reader.py
#
# Read gaze dataset from asc file or csv file
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
    file_meta_data = {'avg_error': None, 'max_error': None, 'low_sample_rate': None, 'total_frame': None}
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
    # regex for meta data (validation)
    validation_msg = re.compile(r"MSG\s+(\d+)\s+!CAL\sVALIDATION.+ERROR\s+(%s)\s+avg\.\s+(%s)\s+max\s+OFFSET.+" % (freg, freg))

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

        match_validation = validation_msg.match(line)
        if match_validation:
            avg_error, max_error = match_validation.group(2), match_validation.group(3)
            # replace the old value since we will only use the validation data after the last frame
            file_meta_data['avg_error'] = float(avg_error)
            file_meta_data['max_error'] = float(max_error)
            continue

    # throw out gazes after the last frame, because the game has ended but eye tracker keeps recording
    frameid2pos[frameid] = []

    if len(frameid2pos) < 1000:     # simple sanity check
        print ("Warning: did you provide the correct ASC file? Because the data for only %d frames is detected" % (len(frameid2pos)))
        raw_input("Press any key to continue")

    few_cnt = 0
    n_frame = len(frameid_list)
    for v in frameid2pos.values():
        if len(v) < 10:
            few_cnt += 1
    print ("Warning:  %d frames have less than 10 gaze samples. (%.1f%%, total frame: %d)" %
           (few_cnt, 100.0*few_cnt/n_frame, n_frame))
    # save the values to meta data
    file_meta_data['low_sample_rate'] = "{:.1f}".format(100.0*float(few_cnt)/float(n_frame)) + "%"
    file_meta_data['total_frame'] = n_frame

    return frameid2pos, frameid2action, frameid2duration, frameid2unclipped_reward, frameid2episode, frameid2score, frameid_list, file_meta_data


def make_unique_frame_id(UTID, frameid):
    # noinspection PyRedundantParentheses
    return (UTID, int(frameid))


def read_gaze_data_csv_file(fname, separator=',', pos_separator=' '):
    """ This function reads a csv file and returns
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

    for (i, line) in enumerate(lines):
        # for the first line, check if titles (column names) are included
        if i == 0 and 'frameid' in line:
            continue

        # parse each section: frameid,episode_id,score,duration,unclipped_reward,action,pos
        data_line = line.split(separator)
        # frame id
        frameid = data_line[0]
        frameid_list.append(frameid)
        # episode id
        episode_id = data_line[1]
        if episode_id == 'null':
            episode_id = None
        else:
            episode_id = int(episode_id)
        frameid2episode[frameid] = episode_id
        # score
        score = data_line[2]
        if score == 'null':
            score = None
        else:
            score = int(score)
        frameid2score[frameid] = score
        # duration
        duration = data_line[3]
        if duration == 'null':
            duration = None
        else:
            duration = int(duration)
        frameid2duration[frameid] = duration
        # unclipped_reward
        unclipped_reward = data_line[4]
        if unclipped_reward == 'null':
            unclipped_reward = None
        else:
            unclipped_reward = int(unclipped_reward)
        frameid2unclipped_reward[frameid] = unclipped_reward
        # action
        action = data_line[5]
        if action == 'null':
            action = None
        else:
            action = int(action)
        frameid2action[frameid] = action
        # pos
        pos_data = data_line[6]
        if pos_data == 'null':
            frameid2pos[frameid] = None
        else:
            pos_data_list = pos_data.split(pos_separator)
            pos_list = []
            n_pos = len(pos_data_list) / 2
            for j in range(0, n_pos):
                posX = float(pos_data_list[2*j])
                posY = float(pos_data_list[2*j+1])
                pos_list.append((posX, posY))
            frameid2pos[frameid] = pos_list
    return frameid2pos, frameid2action, frameid2duration, frameid2unclipped_reward, frameid2episode, frameid2score, frameid_list


if __name__ == '__main__':
    read_gaze_data_csv_file('/Users/lguan/Documents/Study/Research/Gaze-Dataset/data_cleaning/csv/191_JAW_9955253_Jun-25-14-35-04.txt')
