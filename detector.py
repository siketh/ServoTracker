__author__ = 'Trevor'

# if you want to change the database all you have to change is the images in the root folder and keep
# the same naming convention, no code needs to change

import cv2
import sys
import glob
import string
import numpy as np
from operator import itemgetter

import cv2


# copy database images, will grab all images starting with "test_" and append to database list
def init_db():
    db = []

    for image_file in glob.glob('test_*'):
        db_in = cv2.imread(image_file, 1).copy()
        db.append(db_in)

    return db


# template matching detection: returns the max, the top left and bottom right of the bounding box
# for the object, and the coordinates of the maximum value
def detect(image, scene):
    method = eval('cv2.TM_CCOEFF')
    height, width = image.shape[:2]
    result = cv2.matchTemplate(scene, image, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    top_left = max_loc
    bottom_right = (top_left[0] + width, top_left[1] + height)
    return max_val, top_left, bottom_right, max_loc


# sorts the detections by their maximum value returned from template matching
# highest value is at index 0
def decide(scores):
    scores.sort(key=itemgetter(0))
    scores.reverse()

    return scores[0]


def main():
    # capture video feed
    cam = cv2.VideoCapture(0)

    # initialize window with camera feed
    win_name = "QR Detector"
    cv2.namedWindow(win_name, cv2.CV_WINDOW_AUTOSIZE)

    # initialize template database and detection threshold
    database = init_db()
    threshold = 200000000.0

    # run continuously until the ESCAPE key is pressed
    while True:
        # reset scores list to empty and grab a frame from the video feed
        scores = []
        object_loc = [-1, -1]
        cam_frame = cam.read()[1]

        # perform template matching on this frame using each of the templates
        # add consecutive results to the scores list
        for template in database:
            scores.append(detect(template, cam_frame))

        # determine the best overall template matching result
        score, top_left, bottom_right, coordinates = decide(scores)

        # if the best result passes the threshold then the object was detected
        # so draw a bounding box around the object
        # IMPORTANT: object_loc will be the coordinates used for tracking
        if score >= threshold:
            print(score)
            cv2.rectangle(cam_frame, top_left, bottom_right, 255, 4)
            object_loc = coordinates

        # display window with camera feed and bounding box
        cv2.imshow(win_name, cam_frame)

        # if ESCAPE key pressed, terminate execution
        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyWindow(win_name)
            break

if __name__ == "__main__":
    main()