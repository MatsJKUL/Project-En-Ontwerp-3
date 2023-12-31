import cv2
import os
import numpy as np
import time
import sys
import picamera2

CAMERA = 0
MIN_AREA = 50000
MAX_AREA = 3000000
SHOW_FRAME = 1
DEBUG_CARDS = 0

camera = picamera2.Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

time.sleep(0.1)
print("start")

class CardDetector():
    def __init__(self):
        self.image_folder = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "data")

        self.load_images()

    def load_images(self):
        self.face_images = {
            'd': cv2.imread(os.path.join(self.image_folder, 'diamond.jpg'), cv2.IMREAD_GRAYSCALE),
            'c': cv2.imread(os.path.join(self.image_folder, 'clubs.jpg'), cv2.IMREAD_GRAYSCALE),
            'h': cv2.imread(os.path.join(self.image_folder, 'hearts.jpg'), cv2.IMREAD_GRAYSCALE),
            's': cv2.imread(os.path.join(self.image_folder, 'spades.jpg'), cv2.IMREAD_GRAYSCALE),
        }

        self.value_images = {
            '2': cv2.imread(os.path.join(self.image_folder, '2.jpg'), cv2.IMREAD_GRAYSCALE),
            '3': cv2.imread(os.path.join(self.image_folder, '3.jpg'), cv2.IMREAD_GRAYSCALE),
            '4': cv2.imread(os.path.join(self.image_folder, '4.jpg'), cv2.IMREAD_GRAYSCALE),
            '5': cv2.imread(os.path.join(self.image_folder, '5.jpg'), cv2.IMREAD_GRAYSCALE),
            '6': cv2.imread(os.path.join(self.image_folder, '6.jpg'), cv2.IMREAD_GRAYSCALE),
            '7': cv2.imread(os.path.join(self.image_folder, '7.jpg'), cv2.IMREAD_GRAYSCALE),
            '8': cv2.imread(os.path.join(self.image_folder, '8.jpg'), cv2.IMREAD_GRAYSCALE),
            '9': cv2.imread(os.path.join(self.image_folder, '9.jpg'), cv2.IMREAD_GRAYSCALE),
            '10': cv2.imread(os.path.join(self.image_folder, '10.jpg'), cv2.IMREAD_GRAYSCALE),
            '11': cv2.imread(os.path.join(self.image_folder, 'jack.jpg'), cv2.IMREAD_GRAYSCALE),
            '12': cv2.imread(os.path.join(self.image_folder, 'queen.jpg'), cv2.IMREAD_GRAYSCALE),
            '13': cv2.imread(os.path.join(self.image_folder, 'king.jpg'), cv2.IMREAD_GRAYSCALE),
            '1': cv2.imread(os.path.join(self.image_folder, 'ace.jpg'), cv2.IMREAD_GRAYSCALE),
        }

    def rotate_frame(self, frame):
        imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)[..., 0]
        ret, thresh = cv2.threshold(
            imgray, 20, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        mask = 255 - thresh
        _, contours, _ = cv2.findContours(
            mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        maxArea = 0
        best = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > maxArea:
                maxArea = area
                best = contour

        rect = cv2.minAreaRect(best)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # crop image inside bounding box
        scale = 1  # cropping margin, 1 == no margin
        W = rect[1][0]
        H = rect[1][1]

        Xs = [i[0] for i in box]
        Ys = [i[1] for i in box]
        x1 = min(Xs)
        x2 = max(Xs)
        y1 = min(Ys)
        y2 = max(Ys)

        angle = rect[2]
        rotated = False
        if angle < -45:
            angle += 90
            rotated = True

        center = (int((x1+x2)/2), int((y1+y2)/2))
        size = (int(scale*(x2-x1)), int(scale*(y2-y1)))

        M = cv2.getRotationMatrix2D((size[0]/2, size[1]/2), angle, 1.0)

        cropped = cv2.getRectSubPix(frame, size, center)
        cropped = cv2.warpAffine(cropped, M, size)

        croppedW = W if not rotated else H
        croppedH = H if not rotated else W

        image = cv2.getRectSubPix(
            cropped, (int(croppedW*scale), int(croppedH*scale)), (size[0]/2, size[1]/2))
        return image

    def process_frame(self, frame, card_counter, show_frame=0):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        gray = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 9)
        """
        cnts = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        for c in cnts:
            cv2.drawContours(thresh, [c], -1, (255, 255, 255), -1)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        opening = cv2.morphologyEx(
            thresh, cv2.MORPH_OPEN, kernel, iterations=4)

        cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        """
        got_card = False
        card = frame
        cardit = frame
        #for c in cnts:
        #    print(c)
        #    if cv2.contourArea(c) > MIN_AREA and cv2.contourArea(c) < MAX_AREA:
        got_card = True
        #x, y, w, h = cv2.boundingRect(c)
       # cv2.rectangle(frame, (x, y), (x + w - 3, y + h - 2),
       #               (36, 255, 12), 3)

       # a = cv2.contourArea(c)
#                sh = 200000/a
#                sw = 150000/a
#                h = int(h/sh)
#                w = int(w/sw)
        #cardit = frame[y:y+h, x:x+w]

        s = 5
        down_width = 55*s
        down_height = 85*s
        down_points = (down_width, down_height)

        cardit = cv2.resize(
            cardit, down_points, interpolation=cv2.INTER_LINEAR)

        card = cardit[0:125, 0: 100]

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
        scaler = 1

        down_width = int(100*scaler)
        down_height = int(150*scaler)
        down_points = (down_width, down_height)

        face_frame = thresh_frame.copy()
        #face_frame = face_frame[70:120, 20:75]
        face_frame = thresh_frame[320:480, 30:150]
        resized_down = cv2.resize(
            face_frame, down_points, interpolation=cv2.INTER_LINEAR)

        best_max_loc = None
        template = None

        for face_name, face_image in self.face_images.items():
            face_match = cv2.matchTemplate(
                resized_down, face_image, cv2.TM_CCOEFF_NORMED)

            _, max_val_face, _, max_loc = cv2.minMaxLoc(face_match)

            if max_val_face > bmf_score:
                template = face_image
                best_max_loc = max_loc
                bmf_score = max_val_face
                bmf = face_name

        if DEBUG_CARDS:
           self.display_match(resized_down, template, best_max_loc, bmf)

        #bmf = self.post_process_face(bmf, color)

        return bmf

    def post_process_face(self, bmf, color):
        if bmf == 'diamonds' and color != 'red':
            bmf = 'spades'

        if color == 'red' and (bmf == 'spades' or bmf == 'clubs'):
            pass
            # print("Didn't find a good color")
        elif color == 'black' and (bmf == 'diamonds' or bmf == 'hearts'):
            pass
            # print("Found black but red face")

        return bmf

    def get_black(self, img_row):
        last_proper_index = 0
        white_pixel_count = 0
        for index, pixel in enumerate(img_row):
            if sum(pixel[0:3])/3 < 100 :
                white_pixel_count +=1
                if white_pixel_count >= 5:
                    return index
            else:
                white_pixel_count = 0
        return index

    def get_white(self, img_col):
        last_proper_index = 0
        white_pixel_count = 0
        print(img_col.shape)
        for index, pixel in enumerate(img_col):
            if sum(pixel[0:3])/3 > 100:
                white_pixel_count +=1
                if white_pixel_count >= 10:
                    return index
            else:
                white_pixel_count = 0
        return index



    def match_value(self, thresh_frame, dp_match=0):
    # thresh_frame is the original frame from the top left of the card
        # when dp_match is true we display the matches
        bmv = None
        bmv_score = float('-inf')

        scaler = 11/10

        down_width = int(100*scaler)
        down_height = int(150*scaler)
        down_points = (down_width, down_height)

        #thresh_frame = thresh_frame[10:80, 5: 75]
        thresh_frame = thresh_frame[140:340, 30:150]
        resized_down = cv2.resize(
            thresh_frame, down_points, interpolation=cv2.INTER_LINEAR)
        max_val = None
        template = None

        for value_name, value_image in self.value_images.items():
            value_match = cv2.matchTemplate(
                resized_down, value_image, cv2.TM_CCOEFF_NORMED)

            _, max_val_value, _, max_loc = cv2.minMaxLoc(value_match)

            # Can we remove this line

            if max_val_value > bmv_score:
                template = value_image
                bmv_score = max_val_value
                bmv = value_name
                max_val = max_loc

        if DEBUG_CARDS:
           self.display_match(resized_down, template, max_val, bmv)

        return bmv

    def display_match(self, frame, template, max_loc, name):
        w, h = template.shape[::-1]
        top_left = max_loc

        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(frame, top_left, bottom_right, 255, 2)
        print("SHOWING", name)
        if DEBUG_CARDS:
            cv2.imshow(name, frame)


    def get_match(self, frame):
        color = 'black'

        colorcode = self.check_color_present(frame)

        if (colorcode > 0.01):
            color = 'red'

        if (frame.shape[0]*frame.shape[1] < 5000):
            return

        #frame = cv2.bilateralFilter(frame, d=9, sigmaColor=75, sigmaSpace=75)

        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        # Apply adaptive thresholding to the grayscale frame
        thresh_frame = cv2.adaptiveThreshold(
            gray_frame, 200, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

        # Expand the black background to cover the whole top of the frame
        #frame[0:60, :] = (, 0.astype(object), 0.astype(object))

        best_match_face = self.match_face(thresh_frame, color, 1)
        best_match_value = self.match_value(thresh_frame, 1)
        # print(f"{best_match_face}, {best_match_value}")

        return best_match_face, best_match_value


card_class = CardDetector()
def capture_image():
    img_index = 0

    score_face_dict = {}
    score_value_dict = {}
    got_card = True

    for i in range(2):
        frame = camera.capture_array()
        
        x, y = 0,320
        if DEBUG_CARDS:
            cv2.imshow("frame", frame)

        card = frame[x:x + 480, 530-200:530]

        if DEBUG_CARDS:
            cv2.imshow("CARD", card)

        if got_card:
            # cv2.imwrite(f'./screens/kaart_{img_index}.jpg', card)
            face, value = card_class.get_match(card)
            print("F: ", face, "V: ", value)
            if face not in score_face_dict:
                score_face_dict[face] = 0

            if value not in score_value_dict:
                score_value_dict[value] = 0

            score_face_dict[face] += 1
            score_value_dict[value] += 1


        img_index += 1
    max_value = 0
    max_face = 0
    ff = 0
    fv = 0

    for key in score_face_dict:
        if not ff:
            max_face = key
            ff = 1
        if score_face_dict[key] > score_face_dict[max_face] and ff:
            max_face = key

    for key in score_value_dict:
        if not fv:
            max_value = key
            fv = 1

        if score_value_dict[key] > score_value_dict[max_value] and fv:
            max_value = key

    print("END RESULT", max_face, max_value)
    cv2.destroyAllWindows()
    return max_face, int(max_value)


def decode_img_file_name(n):
    face = ''
    for i, c in enumerate(n):
        if c == '_':
            value = n[i+1]
            break

        face += c

    return face.lower(), int(value)

