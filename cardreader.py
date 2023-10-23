# Import the libraries to use
import cv2
import os
import time
import sys

CAMERA = 0
MIN_AREA = 4000
MAX_AREA = 3000000
SHOW_FRAME = 1


class CardDetector():
    def __init__(self):
        self.load_images()

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

    def process_frame(self, frame, show_frame=0):
        #    # print(f"Checking for area with: {MIN_AREA} < A < {MAX_AREA}")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # adaptive threshold
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 9)

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
                print("GOT CARD")
                x, y, w, h = cv2.boundingRect(c)
#                cv2.rectangle(frame, (x, y), (x + w - 3, y + h - 2),
# (36, 255, 12), 3)

                cv2.drawContours(frame, [c], -1, (36, 255, 12), 4)

                a = cv2.contourArea(c)
                sh = 150000/a
                sw = 100000/a
                h = int(h/sh)
                w = int(w/sw)
                card = frame[y:y+h, x:x+w]
                card = card[0:125, 0: 100]

                down_width = 75
                down_height = 125
                down_points = (down_width, down_height)

                card = cv2.resize(
                    card, down_points, interpolation=cv2.INTER_CUBIC)

        if show_frame:
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

    def match_face(self, thresh_frame, color, dp_match=0):
        bmf = None
        bmf_score = float('-inf')

        down_width = 170
        down_height = 170
        down_points = (down_width, down_height)

        face_frame = thresh_frame.copy()
        face_frame = face_frame[70:120, 20:75]
        resized_down = cv2.resize(
            face_frame, down_points, interpolation=cv2.INTER_LINEAR)

        for face_name, face_image in self.face_images.items():
            face_match = cv2.matchTemplate(
                resized_down, face_image, cv2.TM_CCOEFF_NORMED)

            _, max_val_face, _, max_loc = cv2.minMaxLoc(face_match)

            template = cv2.imread(
                f'./data/{face_name}.jpg', cv2.IMREAD_GRAYSCALE)

            if dp_match:
                self.display_match(resized_down, template, max_loc)

            if max_val_face > bmf_score:
                bmf_score = max_val_face
                bmf = face_name

        bmf = self.post_process_face(bmf, color)

        return bmf

    def post_process_face(self, bmf, color):
        if bmf == 'diamonds' and color != 'red':
            bmf = 'spades'

        if color == 'red' and (bmf == 'spades' or bmf == 'clubs'):
            print("Didn't find a good color")
        elif color == 'black' and (bmf == 'diamonds' or bmf == 'hearts'):
            print("Found black but red face")

        return bmf

    def match_value(self, thresh_frame, dp_match=0):
        # thresh_frame is the original frame from the top left of the card
        # when dp_match is true we display the matches
        bmv = None
        bmv_score = float('-inf')

        down_width = 200
        down_height = 200
        down_points = (down_width, down_height)
        thresh_frame = thresh_frame[10:80, 5: 75]
        resized_down = cv2.resize(
            thresh_frame, down_points, interpolation=cv2.INTER_LINEAR)

        for value_name, value_image in self.value_images.items():
            value_match = cv2.matchTemplate(
                resized_down, value_image, cv2.TM_CCOEFF_NORMED)

            _, max_val_value, _, max_loc = cv2.minMaxLoc(value_match)

            # Can we remove this line
            template = cv2.imread(
                f'./data/{value_name}.jpg', cv2.IMREAD_GRAYSCALE)

            if dp_match:
                self.display_match(resized_down, template, max_loc)

            if max_val_value > bmv_score:
                bmv_score = max_val_value
                bmv = value_name

        return bmv

    def display_match(self, frame, template, max_loc):
        w, h = template.shape[::-1]
        top_left = max_loc

        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(frame, top_left, bottom_right, 255, 2)

        cv2.imshow('Matched Value Frame', frame)

    def get_match(self, frame):
        color = 'black'

        colorcode = self.check_color_present(frame)

        if (colorcode > 0.01):
            print("RED")
            color = 'red'

        if (frame.shape[0]*frame.shape[1] < 5000):
            return

        frame = cv2.bilateralFilter(frame, d=9, sigmaColor=75, sigmaSpace=75)

        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        # Apply adaptive thresholding to the grayscale frame
        thresh_frame = cv2.adaptiveThreshold(
            gray_frame, 200, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

        # Expand the black background to cover the whole top of the frame
        frame[0:60, :] = (0, 0, 0)

        best_match_face = self.match_face(thresh_frame, color, 1)
        best_match_value = self.match_value(thresh_frame, 1)

        # Display the result with improved readability
        # cv2.putText(frame, f"Face: {best_match_face}, Value: {best_match_value}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
        # (0, 255, 0), 2)
        print(f"Face: {best_match_face}, Value: {best_match_value}")
        time.sleep(.05)


if __name__ == "__main__":
    image_folder = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "data")

    for i, arg in enumerate(sys.argv):
        if i == 1:
            print("GETCAM")
            CAMERA = arg

    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    img_index = 0
    card_class = CardDetector()
    while True:

        ret, frame = cap.read()
        # frame = cv2.imread('./data/diamonds5.jpg')
        if not ret:
            break

        got_card, card = card_class.process_frame(frame, SHOW_FRAME)

        if got_card:
            # cv2.imwrite(f'./screens/kaart_{img_index}.jpg', card)
            card_class.get_match(card)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        img_index += 1

    cap.release()
    cv2.destroyAllWindows()
