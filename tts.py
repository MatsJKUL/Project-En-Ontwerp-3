import csv
import copy
import argparse
import itertools
from collections import Counter
from collections import deque
DEBUG = False
import cv2 as cv
import numpy as np
import mediapipe as mp

from model import KeyPointClassifier
from model import PointHistoryClassifier
def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence",
                        help='min_detection_confidence',
                        type=float,
                        default=0.7)
    parser.add_argument("--min_tracking_confidence",
                        help='min_tracking_confidence',
                        type=int,
                        default=0.5)

    args = parser.parse_args()

    return args


args = get_args()

cap_device = args.device
cap_width = args.width
cap_height = args.height

use_static_image_mode = args.use_static_image_mode
min_detection_confidence = args.min_detection_confidence
min_tracking_confidence = args.min_tracking_confidence

use_brect = True


cap = cv.VideoCapture(cap_device)
cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=use_static_image_mode,
    max_num_hands=1,
    min_detection_confidence=min_detection_confidence,
    min_tracking_confidence=min_tracking_confidence,
)

keypoint_classifier = KeyPointClassifier()

with open('model/keypoint_classifier/keypoint_classifier_label.csv',
          encoding='utf-8-sig') as f:
    keypoint_classifier_labels = csv.reader(f)
    keypoint_classifier_labels = [
        row[0] for row in keypoint_classifier_labels
    ]


def recognise_hand():
    icount = 0
    while True:
        hand_sign_id = None
        for i in range(5):
            cap.grab()
        ret, image = cap.read()
        if not ret:
            continue

        icount += 1
        image = cv.flip(image, 1)  # Mirror display

        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        #  ####################################################################
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                landmark_list = calc_landmark_list(image, hand_landmarks)

                pre_processed_landmark_list = pre_process_landmark(
                    landmark_list)

                hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                confidence = handedness.classification[0].score

                if DEBUG:
                    print(f"Sign id: {hand_sign_id}")
                    print(f"Confidence: {confidence}")

                if confidence < 0.80:
                    print("Confidence not high enough => Trying again")
                    continue

                if hand_sign_id == 3:
                    return 'OK'
                elif hand_sign_id == 4:
                    return 'Peace'
                elif hand_sign_id == 0:
                    return 'Open'
                if hand_sign_id == 1:
                    return 'closed'

    cap.release()




def calc_landmark_list(image, landmarks):
    print(calc_landmark_list)
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point


def pre_process_landmark(landmark_list):
    print(pre_process_landmark)
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list












####################    HAND RECOGNISION   ##########################
move = None
while move is not 'OK':
    move = recognise_hand()