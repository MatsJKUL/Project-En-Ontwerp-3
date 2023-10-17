# Import the libraries to use
import cv2
import os
import time
import sys

CAMERA = 0
MIN_AREA = 4000
MAX_AREA = 300000


class CardDetector():
    def __init__(self):
        pass

    def load_images(self):
        self.face_images = {
            'diamond': cv2.imread(os.path.join(image_folder, 'diamond.jpg'), cv2.IMREAD_GRAYSCALE),
            'clubs': cv2.imread(os.path.join(image_folder, 'clubs.jpg'), cv2.IMREAD_GRAYSCALE),
            'hearts': cv2.imread(os.path.join(image_folder, 'hearts.jpg'), cv2.IMREAD_GRAYSCALE),
            'spades': cv2.imread(os.path.join(image_folder, 'spades.jpg'), cv2.IMREAD_GRAYSCALE),
        }

        self.value_images = {
            '2': cv2.imread(os.path.join(image_folder, '2.jpg'), cv2.IMREAD_GRAYSCALE),
            '3': cv2.imread(os.path.join(image_folder, '3.jpg'), cv2.IMREAD_GRAYSCALE),
            '4': cv2.imread(os.path.join(image_folder, '4.jpg'), cv2.IMREAD_GRAYSCALE),
            '5': cv2.imread(os.path.join(image_folder, '5.jpg'), cv2.IMREAD_GRAYSCALE),
            '6': cv2.imread(os.path.join(image_folder, '6.jpg'), cv2.IMREAD_GRAYSCALE),
            '7': cv2.imread(os.path.join(image_folder, '7.jpg'), cv2.IMREAD_GRAYSCALE),
            '8': cv2.imread(os.path.join(image_folder, '8.jpg'), cv2.IMREAD_GRAYSCALE),
            '9': cv2.imread(os.path.join(image_folder, '9.jpg'), cv2.IMREAD_GRAYSCALE),
            '10': cv2.imread(os.path.join(image_folder, '10.jpg'), cv2.IMREAD_GRAYSCALE),
            'jack': cv2.imread(os.path.join(image_folder, 'jack.jpg'), cv2.IMREAD_GRAYSCALE),
            'queen': cv2.imread(os.path.join(image_folder, 'queen.jpg'), cv2.IMREAD_GRAYSCALE),
            'king': cv2.imread(os.path.join(image_folder, 'king.jpg'), cv2.IMREAD_GRAYSCALE),
            'ace': cv2.imread(os.path.join(image_folder, 'ace.jpg'), cv2.IMREAD_GRAYSCALE),
        }

    def process_frame(self, frame):
        # print(f"Checking for area with: {MIN_AREA} < A < {MAX_AREA}")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # adaptive threshold
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 9)

        # Fill rectangular contours
#        cnts = cv2.findContours(
#            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
#        for c in cnts:
#            cv2.drawContours(thresh, [c], -1, (255, 255, 255), -1)

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
                card = card[0:125, 0: 100]

        cv2.imshow('CARD FRAME', frame)
        return got_card, card

    def check_color_present(self, frame):
        total_pixel = 0
        red_pixel = 0
        for row in frame:
            for pixel in row:
                if (pixel[2] > 200 and pixel[1] < 200 and pixel[0] < 200):
                    red_pixel += 1
                total_pixel += 1

        return red_pixel/total_pixel

    def get_match(self, frame):
        # Apply bilateral filtering to the frame
        if (frame.shape[0]*frame.shape[1] < 5000):
            return

        cv2.imshow('KAART', card)
        frame = cv2.bilateralFilter(frame, d=9, sigmaColor=75, sigmaSpace=75)

        color = 'black'

        colorcode = self.check_color_present(card)
        if (colorcode > 0.01):
            color = 'red'

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
        # Initialize to negative infinity
        best_match_face_score = float('-inf')
        # Initialize to negative infinity
        best_match_value_score = float('-inf')

        down_width = 170
        down_height = 170
        down_points = (down_width, down_height)
        face_frame = thresh_frame.copy()
        face_frame = face_frame[70:120, 20: 75]
        resized_down = cv2.resize(
            face_frame, down_points, interpolation=cv2.INTER_LINEAR)

        for face_name, face_image in self.face_images.items():
            # Try to match the face in the entire frame
            face_match = cv2.matchTemplate(
                resized_down, face_image, cv2.TM_CCOEFF_NORMED)

            template = cv2.imread(
                f'./data/{face_name}.jpg', cv2.IMREAD_GRAYSCALE)
            w, h = template.shape[::-1]
            # Find the maximum similarity score
            _, max_val_face, _, max_loc = cv2.minMaxLoc(face_match)
            top_left = max_loc

            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(resized_down, top_left, bottom_right, 255, 2)

            # Update the best match for faces if a better match is found
            if max_val_face > best_match_face_score:
                best_match_face_score = max_val_face
                best_match_face = face_name

        if best_match_face == 'diamonds' and color != 'red':
            print('CONVERTED')
            best_match_face = 'spades'

        down_width = 200
        down_height = 200
        down_points = (down_width, down_height)
        thresh_frame = thresh_frame[10:80, 5: 75]
        resized_down = cv2.resize(
            thresh_frame, down_points, interpolation=cv2.INTER_LINEAR)

        for value_name, value_image in self.value_images.items():
            # Try to match the value in the entire frame
            value_match = cv2.matchTemplate(
                resized_down, value_image, cv2.TM_CCOEFF_NORMED)

            # Find the maximum similarity score
            _, max_val_value, _, max_loc = cv2.minMaxLoc(value_match)

            template = cv2.imread(
                f'./data/{value_name}.jpg', cv2.IMREAD_GRAYSCALE)
            w, h = template.shape[::-1]
            # Find the maximum similarity score
            _, max_val_face, _, max_loc = cv2.minMaxLoc(value_match)
            top_left = max_loc

            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(resized_down, top_left, bottom_right, 255, 2)

            cv2.imshow('DOWN FRAME', resized_down)
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

    for i, arg in enumerate(sys.argv):
        if i == 1:
            print("GETCAM")
            CAMERA = arg

    cap = cv2.VideoCapture(2)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    img_index = 0
    while True:
        ret, frame = cap.read()
        # frame = cv2.imread('./data/diamonds5.jpg')
        if not ret:
            break

        got_card, card = process_frame(frame)

        if got_card:
            # cv2.imwrite(f'./screens/kaart_{img_index}.jpg', card)
            cv2.imshow("LOL", card)
            get_match(card)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        img_index += 1

    cap.release()
    cv2.destroyAllWindows()
