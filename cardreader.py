# Import the libraries to use
import cv2
import os
import time
import sys

CAMERA = 0
MIN_AREA = 200
MAX_AREA = 999900000


def process_frame(frame):
    # print(f"Checking for area with: {MIN_AREA} < A < {MAX_AREA}")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # adaptive threshold
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 9)

    # Fill rectangular contours
    cnts = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(thresh, [c], -1, (255, 255, 255), -1)

    # Morph open
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    opening = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, kernel, iterations=4)

    # Draw rectangles, the 'area_treshold' value was determined empirically
    cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)

    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    got_card = False
    card = frame
    for c in cnts:
        if cv2.contourArea(c) > MIN_AREA and cv2.contourArea(c) < MAX_AREA:

            got_card = True
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w - 3, y + h - 2),
                          (36, 255, 12), 3)

            card = frame[y:y+h, x:x+w]
            card = card[0:80, 0:120]

    cv2.imshow('Card Detection', frame)
    return got_card, card


def get_match(frame):
    # Apply bilateral filtering to the frame
    cv2.imshow('CARD FRAME', card)
    frame = cv2.bilateralFilter(frame, d=9, sigmaColor=75, sigmaSpace=75)

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    # Apply adaptive thresholding to the grayscale frame
    thresh_frame = cv2.adaptiveThreshold(
        gray_frame, 200, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    # Expand the black background to cover the whole top of the frame
    frame[0:60, :] = (0, 0, 0)

    # Loop through the face and value images to find matches
    best_match_face = None
    best_match_value = None
    best_match_face_score = float('-inf')  # Initialize to negative infinity
    best_match_value_score = float('-inf')  # Initialize to negative infinity

    down_width = 70
    down_height = 120
    down_points = (down_width, down_height)
    resized_down = cv2.resize(
        thresh_frame, down_points, interpolation=cv2.INTER_LINEAR)

    cv2.imshow('DOWN FRAME', resized_down)
    for face_name, face_image in face_images.items():
        # Try to match the face in the entire frame
        face_match = cv2.matchTemplate(
            resized_down, face_image, cv2.TM_CCOEFF_NORMED)

        # Find the maximum similarity score
        _, max_val_face, _, _ = cv2.minMaxLoc(face_match)

        # Update the best match for faces if a better match is found
        if max_val_face > best_match_face_score:
            best_match_face_score = max_val_face
            best_match_face = face_name

    for value_name, value_image in value_images.items():
        # Try to match the value in the entire frame
        value_match = cv2.matchTemplate(
            resized_down, value_image, cv2.TM_CCOEFF_NORMED)

        # Find the maximum similarity score
        _, max_val_value, _, _ = cv2.minMaxLoc(value_match)

        # Update the best match for values if a better match is found
        if max_val_value > best_match_value_score:
            best_match_value_score = max_val_value
            best_match_value = value_name

    # Display the result with improved readability
#    cv2.putText(frame, f"Face: {best_match_face}, Value: {best_match_value}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
#                (0, 255, 0), 2)
    print(f"Face: {best_match_face}, Value: {best_match_value}")
    time.sleep(.05)


# Release the webcam and close all windows
if __name__ == "__main__":
    image_folder = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "data")

    # Create a separate window for the thresholded image
    # Load the binarized card images for faces and values
    face_images = {
        'diamond': cv2.imread(os.path.join(image_folder, 'Diamonds.jpg'), 0),
        'clubs': cv2.imread(os.path.join(image_folder, 'Clubs.jpg'), 0),
        'hearts': cv2.imread(os.path.join(image_folder, 'Hearts.jpg'), 0),
        'spades': cv2.imread(os.path.join(image_folder, 'Spades.jpg'), 0),
    }

    value_images = {
        '2': cv2.imread(os.path.join(image_folder, '2.jpg'), 0),
        '3': cv2.imread(os.path.join(image_folder, '3.jpg'), 0),
        '4': cv2.imread(os.path.join(image_folder, '4.jpg'), 0),
        '5': cv2.imread(os.path.join(image_folder, '5.jpg'), 0),
        '6': cv2.imread(os.path.join(image_folder, '6.jpg'), 0),
        '7': cv2.imread(os.path.join(image_folder, '7.jpg'), 0),
        '8': cv2.imread(os.path.join(image_folder, '8.jpg'), 0),
        '9': cv2.imread(os.path.join(image_folder, '9.jpg'), 0),
        '10': cv2.imread(os.path.join(image_folder, '10.jpg'), 0),
        'jack': cv2.imread(os.path.join(image_folder, 'jack.jpg'), 0),
        'queen': cv2.imread(os.path.join(image_folder, 'queen.jpg'), 0),
        'king': cv2.imread(os.path.join(image_folder, 'king.jpg'), 0),
        'ace': cv2.imread(os.path.join(image_folder, 'ace.jpg'), 0),
    }

    for i, arg in enumerate(sys.argv):
        if i == 1:
            print("GETCAM")
            CAMERA = arg

    cap = cv2.VideoCapture(2)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    i = 0
    while True:
        ret, frame = cap.read()
        # frame = cv2.imread('./data/diamonds5.jpg')
        if not ret:
            break

        got_card, card = process_frame(frame)

        if got_card:
            print("GOT A CARD")
            get_match(card)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
