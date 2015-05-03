__author__ = 'Trevor, Eric'


# if you want to change the database all you have to change is the images in the root folder and keep
# the same naming convention, no code needs to change

import cv2
import sys
import glob
import string
import numpy as np
from operator import itemgetter
import serial
import math

COM = "COM9"
BAUD = 115200

x_rot = None
y_rot = None

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


#Outputs the angle (degrees) and magnitude of the vector between the center of the frame
#and the location of of the target to the arduino via serial connection
def tracking(image, location, center, object_center, ser):
    # #calculate the difference of the target location and the center of the frame -Eric
    # x_rot = location[0] - center[0]
    # y_rot = location[1] - center[1]

    print "Location: ", location

    #Draw line from center to location -Eric
    cv2.line(image, center, object_center, 255, 4)

    # Determine the angle to turn in the y direction, mapping the position in the center of the object
    # to servo motion
    if (object_center[0] <= 80):
        y_rot = 100
    if ((object_center[0] > 80 ) & (object_center[0] <= 160)):
        y_rot = 90
    if ((object_center[0] > 160 ) & (object_center[0] <= 240)):
        y_rot = 80
    if ((object_center[0] > 240 ) & (object_center[0] <= 320)):
        y_rot = 70
    if ((object_center[0] > 320 ) & (object_center[0] <= 400)):
        y_rot = 60
    if (object_center[0] > 400 ):
        y_rot = 50

    # Determine the angle to turn in the y direction, mapping the position in the center of the object
    # to servo motion
    if (object_center[1] <= 80):
        x_rot = 143
    if ((object_center[1] > 80 ) & (object_center[1] <= 160)):
        x_rot = 125
    if ((object_center[1] > 160 ) & (object_center[1] <= 240)):
        x_rot = 108
    if ((object_center[1] > 240 ) & (object_center[1] <= 320)):
        x_rot = 90
    if ((object_center[1] > 320 ) & (object_center[1] <= 400)):
        x_rot = 73
    if ((object_center[1] > 400 ) & (object_center[1] <= 480)):
        x_rot = 55
    if ((object_center[1] > 480 ) & (object_center[1] <= 560)):
        x_rot = 38
    if (object_center[1] > 560 ):
        x_rot = 20

    #send the x
    ser.write(str(x_rot))
    print "x_rot: ", ser.readline()

    #send the y
    ser.write(str(y_rot))
    print "y_rot: ", ser.readline()

# sorts the detections by their maximum value returned from template matching
# highest value is at index 0
def decide(scores):
    scores.sort(key=itemgetter(0))
    scores.reverse()

    return scores[0]


def main():

    # Open serial connection to arduino at COM and BAUD rate -Eric
    ser = serial.Serial(COM, BAUD)
    # Check arduino status
    print "Arduino Status: ", ser.readline()


    # capture video feed and then get the dimensions
    cam = cv2.VideoCapture(0)
    retval, for_dims = cam.read()
    #calculate the width and height of the camera frame -Eric
    print "image dimensions: ", for_dims.shape
    width = for_dims.shape[1]
    height = for_dims.shape[0]

    #calculate the center of the frame -Eric
    center = width/2, height/2

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

        #Initialize object_loc so if it doesn't exist, camera won't move -Eric
        object_loc = None
        object_center = None

        # if the best result passes the threshold then the object was detected
        # so draw a bounding box around the object
        # IMPORTANT: object_loc will be the coordinates used for tracking
        if score >= threshold:
            print(score)

            cv2.rectangle(cam_frame, top_left, bottom_right, 255, 4)
            object_loc = coordinates
            object_center = (bottom_right[0] + top_left[0])/2, (bottom_right[1] + top_left[1])/2

            print "Center: ", center
            print "Object center: ", object_center

            #begin tracking -Eric
            tracking(cam_frame, object_loc, center, object_center, ser)
        
        #check to see if object_loc was initialized, otherwise use center -Eric
        if not object_loc:
            object_loc = center
        
        # display window with camera feed and bounding box
        cv2.imshow(win_name, cam_frame)

        
        # if ESCAPE key pressed, terminate execution
        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyWindow(win_name)
            break


if __name__ == "__main__":
    main()