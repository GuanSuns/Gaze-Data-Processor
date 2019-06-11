# data_visualizer.py
#
# Visualize the cleaned data (to verify the correctness)
# -----------------------
import os
import time
import shutil
import data_reader
# noinspection PyClassHasNoInit
import tarfile
import pygame


class DrawgcWrapper:
    def __init__(self):
        self.cursor = pygame.image.load('target.png')
        self.cursor_size = (self.cursor.get_width(), self.cursor.get_height())

    def draw_gc(self, screen, gaze_position):
        """ draw the gaze-contingent window on screen """
        region_top_left = (gaze_position[0] - self.cursor_size[0] // 2, gaze_position[1] - self.cursor_size[1] // 2)
        # Draws and shows the cursor content;
        screen.blit(self.cursor, region_top_left)


class DrawingStatus:
    def __init__(self):
        pass
    cur_frame_index = 0
    total_frame = 0
    target_fps = 60
    pause = False
    terminated = False
ds = DrawingStatus()


def preprocess_and_sanity_check(png_files, frameid_list):
    has_warning = False

    # remove unrelated files
    for fname in png_files:
        if not fname.endswith(".png"):
            print("Warning: %s is not a PNG file. Deleting it from the frames list" % fname)
            has_warning = True
            png_files.remove(fname)

    # check if each frame has its corresponding png file
    based_dir = png_files[0].split('/')[0]
    set_png_files = set(png_files)
    for frameid in frameid_list:
        png_fname = based_dir + '/' + frameid + '.png'
        if png_fname not in set_png_files:
            print("Warning: no corresponding png file for frame id %s." % frameid)
            has_warning = True

    if has_warning:
        print("There are warnings. Sleeping for 2 sec...")
        time.sleep(2)


def frameid_sort_key(frameid):
    return int(frameid.split('_')[2])


def check_gaze_range(pos_x, pos_y, w, h):
    """ Check if the gaze coordinate is within the screen """
    if pos_x < 0 or pos_x > w or pos_y < 0 or pos_y > h:
        return False
    return True


def event_handler_func():
    global ds

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                print("Fast-backward 5 seconds")
                ds.cur_frame_id -= 5 * ds.target_fps
            elif event.key == pygame.K_DOWN:
                print("Fast-forward 5 seconds")
                ds.cur_frame_id += 5 * ds.target_fps
            if event.key == pygame.K_LEFT:
                print("Moving to previous frame")
                ds.cur_frame_id -= 1
            elif event.key == pygame.K_RIGHT:
                print("Moving to next frame")
                ds.cur_frame_id += 1
            elif event.key == pygame.K_F3:
                p = float(raw_input("Seeking through the video. Enter a percentage in float: "))
                ds.cur_frame_id = int(p/100*ds.total_frame)
            elif event.key == pygame.K_SPACE:
                ds.pause = not ds.pause
            elif event.key == pygame.K_F9:
                ds.draw_many_gazes = not ds.draw_many_gazes
                print("draw all gazes belonging to a frame: %s" % ("ON" if ds.draw_many_gazes else "OFF"))
            elif event.key == pygame.K_F11:
                ds.target_fps -= 2
                print("Setting target FPS to %d" % ds.target_fps)
            elif event.key == pygame.K_F12:
                ds.target_fps += 2
                print("Setting target FPS to %d" % ds.target_fps)
            elif event.key == pygame.K_ESCAPE:
                ds.terminated = True
                print("\nStopping replay.")
    ds.cur_frame_id = max(0, min(ds.cur_frame_id, ds.total_frame))
    ds.target_fps = max(1, ds.target_fps)


def visualize_csv(tar_fname, csv_fname):
    # read from the csv file
    frameid2pos, _, frameid2duration, _, _, _, frameid_list = data_reader.read_gaze_data_csv_file(csv_fname)
    frameid_list = sorted(frameid_list, key=frameid_sort_key)

    # open the tar file
    tar = tarfile.open(tar_fname, 'r')
    png_files = tar.getnames()

    preprocess_and_sanity_check(png_files, frameid_list)

    print("\nYou can control the replay using keyboard. Try pressing space/up/down/left/right.")
    print("For all available keys, see event_handler_func() code.\n")
    temp_extract_dir = os.path.dirname(tar_fname) + "/gaze_data_tmp/"
    if not os.path.exists(temp_extract_dir):
        os.mkdir(temp_extract_dir)
    print("Uncompressing PNG tar file")
    tar.extractall(temp_extract_dir)
    # get the full path
    temp_extract_full_path_dir = temp_extract_dir + '/' + png_files[0].split('/')[0]
    print("Uncompressed PNG tar file into temporary directory: " + temp_extract_full_path_dir)

    # init pygame and other stuffs
    origin_w = 160
    x_scale = 2.0
    origin_h = 210
    y_scale = 2.0
    w, h = int(origin_w*x_scale), int(origin_h*y_scale)

    global ds
    ds.target_fps = 60
    ds.total_frame = len(png_files)
    ds.cur_frame_id = 0
    ds.terminated = False

    # init Drawgc Wrapper
    dw = DrawgcWrapper()

    # init pygame
    pygame.init()
    pygame.font.init()
    pygame_font = pygame.font.SysFont('Consolas', 28)
    pygame.display.set_mode((w, h), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.RLEACCEL, 32)
    screen = pygame.display.get_surface()

    while ds.cur_frame_id < ds.total_frame:
        event_handler_func()

        # Load PNG file and draw the frame and the gaze-contingent window
        frame_id = frameid_list[ds.cur_frame_id]
        png_fname = temp_extract_full_path_dir + '/' + frame_id + '.png'
        # check if the corresponding png file exists
        if not os.path.isfile(png_fname):
            screen.fill((0, 0, 0))
            text_surface_desc = pygame_font.render('Missing png file for frame id:', True, (255, 255, 255))
            screen.blit(text_surface_desc, (w // 10, 2 * h // 5))
            text_surface_frameid = pygame_font.render(frame_id, True, (255, 255, 255))
            screen.blit(text_surface_frameid, (w // 10, 3 * h // 5))
        else:
            s = pygame.image.load(png_fname)
            s = pygame.transform.scale(s, (w, h))
            screen.blit(s, (0, 0))

            # visualize the gaze
            gaze_list = frameid2pos[frame_id]
            if gaze_list is not None and len(gaze_list) > 0:
                for (posX, posY) in gaze_list:
                    if check_gaze_range(posX, posY, origin_w, origin_h):
                        dw.draw_gc(screen, (posX*x_scale, posY*y_scale))

        pygame.display.flip()

        if not ds.pause:
            ds.cur_frame_id = ds.cur_frame_id + 1
        if ds.terminated:
            break

        duration = frameid2duration[frame_id]
        if duration is not None:
            time.sleep(duration * 0.001)  # duration is in msec

    print("Replay ended.")

    # remove the temporary files
    print("Deleting PNG files in temporary directory.")
    shutil.rmtree(temp_extract_full_path_dir)


def do_testing_visualize_csv():
    testing_tar_fname = '/Users/lguan/Documents/Study/Research/UT Austin/Gaze-Dataset/data/raw-data/52_RZ_2394668_Aug-10-14-52-42.tar.bz2'
    testing_csv_fname = '/Users/lguan/Documents/Study/Research/UT Austin/Gaze-Dataset/data/csv/52_RZ_2394668_Aug-10-14-52-42.txt'
    visualize_csv(testing_tar_fname, testing_csv_fname)


if __name__ == '__main__':
    do_testing_visualize_csv()

