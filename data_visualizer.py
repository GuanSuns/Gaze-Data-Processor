# data_visualizer.py
#
# Visualize the cleaned data (to verify the correctness)
# -----------------------
import os
import time
import data_reader

# noinspection PyClassHasNoInit
import tarfile
import pygame


class DrawingStatus:
    draw_many_gazes = True
    cur_frame_id = 1
    total_frame = None
    target_fps = 60
    pause = False
ds = DrawingStatus()


def preprocess_and_sanity_check(png_files, frameid_list):
    hasWarning = False

    for fname in png_files:
        if not fname.endswith(".png"):
            print ("Warning: %s is not a PNG file. Deleting it from the frames list" % fname)
            hasWarning = True
            png_files.remove(fname)

    for frameid in frameid_list:
        png_fname = frameid + '.png'
        if png_fname not in png_files:
            print ("Warning: no corresponding png file for frame id %d." % frameid)
            hasWarning = True

    if hasWarning:
        print "There are warnings. Sleeping for 2 sec..."
        time.sleep(2)


def frameid_sort_key(frameid):
    return int(frameid.split('_')[2])


def visualize_csv(tar_fname, csv_fname):
    # read from the csv file
    frameid2pos, _, frameid2duration, _, _, _, frameid_list = data_reader.read_gaze_data_csv_file(csv_fname)
    frameid_list = sorted(frameid_list, key=frameid_sort_key)

    # open the tar file
    tar = tarfile.open(tar_fname, 'r')
    png_files = set(tar.getnames())

    preprocess_and_sanity_check(png_files, frameid_list)

    print "\nYou can control the replay using keyboard. Try pressing space/up/down/left/right."
    print "For all available keys, see event_handler_func() code.\n"
    print "Uncompressing PNG tar file into memory (temp)..."
    temp_extract_dir = "/gaze_data_tmp/"
    if not os.path.exists(temp_extract_dir):
        os.mkdir(temp_extract_dir)
    tar.extractall(temp_extract_dir)

    # init pygame and other stuffs
    origin_w = 160
    x_scale = 2.0
    origin_h = 210
    y_scale = 2.0
    w, h = origin_w*x_scale, origin_h*y_scale
    pygame.init()
    pygame.display.set_mode((w, h), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.RLEACCEL, 32)
    






def do_testing_visualize_csv():
    testing_tar_fname = '/Users/lguan/Documents/Study/Research/UT Austin/Gaze-Dataset/data/raw-data/52_RZ_2394668_Aug-10-14-52-42.tar.bz2'
    testing_csv_fname = ''
    visualize_csv(testing_tar_fname, testing_csv_fname)


if __name__ == '__main__':
    do_testing_visualize_csv()

