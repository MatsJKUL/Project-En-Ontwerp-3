import pygame
import time
from pygame.locals import *
import os
import random
import csv
import copy
import argparse
import itertools
from tts import tts

import cv2 as cv
import numpy as np
import mediapipe as mp

from model import KeyPointClassifier

import RPi.GPIO as GPIO
import time

DEBUG = False

GPIO.setmode(GPIO.BCM) #setup motors
servo1_pin = 14
servo2_pin = 16
dc1_pin = 17
dc2_pin = 18
GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)
GPIO.setup(dc1_pin, GPIO.OUT)
GPIO.setup(dc2_pin, GPIO.OUT)
pwm1 = GPIO.PWM(servo1_pin, 50)
pwm1.start(0)
pwm2 = GPIO.PWM(servo2_pin, 50)
pwm2.start(0)

def turn_servo1(angle):
    duty_cycle = 2.5 + 10 * angle / 270  # Map the angle to the duty cycle
    pwm1.ChangeDutyCycle(duty_cycle)
    time.sleep(1)

def turn_servo2(angle):
    duty_cycle = 2.5 + 10 * angle / 270  # Map the angle to the duty cycle
    pwm2.ChangeDutyCycle(duty_cycle)
    time.sleep(1)
def turn_dc1():
    GPIO.output(dc1_pin, GPIO.HIGH)

def stop_dc1():
    GPIO.output(dc1_pin, GPIO.LOW)

def turn_dc2():
    GPIO.output(dc2_pin, GPIO.HIGH)

def stop_dc2():
    GPIO.output(dc2_pin, GPIO.LOW)
def servo_stop():
    pwm1.stop()  # Stop the PWM signal
    pwm2.stop()  # Stop the PWM signal
    GPIO.cleanup()  # Clean up the GPIO configuration

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

# Read labels ###########################################################
with open('model/keypoint_classifier/keypoint_classifier_label.csv',
          encoding='utf-8-sig') as f:
    keypoint_classifier_labels = csv.reader(f)
    keypoint_classifier_labels = [
        row[0] for row in keypoint_classifier_labels
    ]


def recognise_hand():
    icount = 0
    while True:
        if DEBUG:
            print("RESET")
        hand_sign_id = None
        for i in range(5):
            cap.grab()
        ret, image = cap.read()
        if not ret:
            continue

        icount += 1
        if DEBUG:
            print("COUNT", icount)
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
                elif hand_sign_id == 5:
                    return 'Fakjoe'
                if hand_sign_id == 1:
                    return 'closed'

    cap.release()


def select_mode(key, mode):
    number = -1
    if 48 <= key <= 57:  # 0 ~ 9
        number = key - 48
    if key == 110:  # n
        mode = 0
    if key == 107:  # k
        mode = 1
    if key == 104:  # h
        mode = 2
    return number, mode


def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)

    return [x, y, x + w, y + h]


def calc_landmark_list(image, landmarks):
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


def pre_process_point_history(image, point_history):
    image_width, image_height = image.shape[1], image.shape[0]

    temp_point_history = copy.deepcopy(point_history)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, point in enumerate(temp_point_history):
        if index == 0:
            base_x, base_y = point[0], point[1]

        temp_point_history[index][0] = (temp_point_history[index][0] -
                                        base_x) / image_width
        temp_point_history[index][1] = (temp_point_history[index][1] -
                                        base_y) / image_height

    # Convert to a one-dimensional list
    temp_point_history = list(
        itertools.chain.from_iterable(temp_point_history))

    return temp_point_history


def logging_csv(number, mode, landmark_list, point_history_list):
    if mode == 0:
        pass
    if mode == 1 and (0 <= number <= 9):
        csv_path = 'model/keypoint_classifier/keypoint.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    if mode == 2 and (0 <= number <= 9):
        csv_path = 'model/point_history_classifier/point_history.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *point_history_list])
    return


def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        # Outer rectangle
        cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]),
                     (0, 0, 0), 1)

    return image


def draw_info_text(image, brect, handedness, hand_sign_text,
                   finger_gesture_text):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22),
                 (0, 0, 0), -1)

    info_text = handedness.classification[0].label[0:]
    if hand_sign_text != "":
        info_text = info_text + ':' + hand_sign_text
    cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)

    if finger_gesture_text != "":
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv.LINE_AA)
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2,
                   cv.LINE_AA)

    return (image, hand_sign_text)


def draw_point_history(image, point_history):
    for index, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:
            cv.circle(image, (point[0], point[1]), 1 + int(index / 2),
                      (152, 251, 152), 2)

    return image


def draw_info(image, fps, mode, number):
    cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               1.0, (0, 0, 0), 4, cv.LINE_AA)
    cv.putText(image, "FPS:" + str(fps), (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               1.0, (255, 255, 255), 2, cv.LINE_AA)

    mode_string = ['Logging Key Point', 'Logging Point History']
    if 1 <= mode <= 2:
        cv.putText(image, "MODE:" + mode_string[mode - 1], (10, 90),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                   cv.LINE_AA)
        if 0 <= number <= 9:
            cv.putText(image, "NUM:" + str(number), (10, 110),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                       cv.LINE_AA)
    return image


class Player:
    def __init__(self, num, bet, name):
        self.cards = []
        self.bet = bet
        self.points = 0
        self.amount_of_aces = 0
        self.number = num
        self.name = name
        self.add_points()
        self.hand_amount = 1

    def get_inzet(self):
        return self.bet

    def get_card(self, card):
        self.cards.append(card)
        self.add_points()

    def add_points(self):
        points = 0
        amount_of_aces = 0
        for card in self.cards:
            if card[1] < 11 and 1 < card[1]:
                points += card[1]

            elif card[1] == 1:
                amount_of_aces += 1
                points += 11
            else:
                points += 10
        self.points = points
        self.amount_of_aces = amount_of_aces
        self.total_points()

    def total_points(self):
        if self.points > 21:
            if self.amount_of_aces > 0:
                self.points -= 10
                self.amount_of_aces -= 1
                self.total_points()

    def status(self):
        return self.cards, self.points

    def get_cards(self):
        return self.cards

    def get_card_by_index(self, i):
        try:
            card = self.cards[i]
        except:
            print("NOT A VALID CARD INDEX, returning first card")
            card = self.cards[0]

        return card

    def get_points(self):
        return self.points

    def get_card_amount(self):
        return len(self.cards)

    def get_winst(self):
        if self.state == 'BUSTED':
            return -self.bet
        elif self.state == 'PUSH':
            return 0
        elif self.state == 'WIN':
            return 2*self.bet

    def display_player_cards(self, game, pos):
        self.add_points()
        pts = self.get_points()
        points = game.font.render(
            str(pts), True, game.white)
        points_rect = points.get_rect()
        points_rect.center = ((pos + 1) * game.screen_width //
                              (game.max_cards_on_screen + 1), 685)

        if (pts > 21):
            game.render_bust(pos)

        pygame.draw.rect(game.screen, game.background, points_rect)
        game.screen.blit(points, points_rect)

        name = game.font.render(
            str(f"{self.name}"), True, game.white)

        name_rect = name.get_rect()
        name_rect.center = ((pos + 1) * game.screen_width //
                            (game.max_cards_on_screen + 1), 650)

        pygame.draw.rect(game.screen, game.background, name_rect)
        game.screen.blit(name, name_rect)

        for i in range(self.get_card_amount()):
            game.screen.blit(game.card_images[self.get_card_by_index(i)], ((
                pos+1) * game.screen_width//(game.max_cards_on_screen+1) +
                (i) * 30 - 60, 500))

        pygame.display.update()
        game.clock.tick(30)


class GameState:
    def init_cards(self):
        self.card_images = {}
        self.cards = []
        self.deleted_cards = []

        card_path = 'cards/'
        for face in ['h', 'd', 'c', 's']:
            for value in range(1, 14):
                card_name = f'{face}{value}'
                self.cards.append((face, value))

                card_image_name = card_name + '.png'
                self.card_images[(face, value)] = pygame.image.load(
                    os.path.join(card_path, card_image_name))
        self.back = 'back'
        self.card_images[(self.back, self.back)] = pygame.image.load(
            os.path.join(card_path, f'{self.back}.png'))

    def init_buttons(self):
        self.play_button = self.font.render("Play", True, self.white)
        self.button_hit = self.font.render("Hit", True, self.white)
        self.button_double = self.font.render("Double", True, self.white)
        self.button_stand = self.font.render("Stand", True, self.white)
        self.split = self.font.render("Split", True, self.white)
        self.button_again = self.font.render("Play again", True, self.white)
        self.button_stop = self.font.render("Stop", True, self.white)
        self.min_bet_txt = self.font.render(
            f"MINIMUM Bet: ${self.min_bet}", True, self.white)

        self.play_rect = self.play_button.get_rect()
        self.hit_rect = self.button_hit.get_rect()
        self.double_rect = self.button_double.get_rect()
        self.stand_rect = self.button_stand.get_rect()
        self.split_rect = self.split.get_rect()
        self.again_rect = self.button_again.get_rect()
        self.stop_rect = self.button_stop.get_rect()
        self.min_bet_rect = self.min_bet_txt.get_rect()

        self.play_rect.center = (
            self.screen_width // 2, self.screen_height // 2)
        self.hit_rect.center = (50, 30)
        self.double_rect.center = (210, 30)
        self.stand_rect.center = (115, 30)
        self.split_rect.center = (260, 30)
        self.again_rect.center = (self.screen_width // 2 -
                                  100, self.screen_height // 2)
        self.stop_rect.center = (self.screen_width // 2 +
                                 100, self.screen_height // 2)

        self.min_bet_rect.center = (125, 40)

    def get_num(self, event):
        if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7] and event.unicode.isdigit():

            return int(event.unicode)

    def display_player_number(self, player_amount):
        text = self.font.render("How many players: " +
                                str(player_amount), True, self.white)
        text_rect = text.get_rect()
        text_rect.center = (self.screen_width // 2,
                            self.screen_height // 2 + 50)
        self.screen.blit(text, text_rect)
        pygame.display.update()

    def start_game(self):
        player_amount = 1

        self.max_cards_on_screen = 3

        while True:
            self.screen.fill(self.black)
            self.screen.blit(self.play_button, self.play_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_rect.collidepoint(event.pos):
                        pygame.display.flip()
                        self.player_amount = player_amount
                        return

                elif event.type == pygame.KEYDOWN and event.key == K_RETURN:
                    pygame.display.flip()
                    self.player_amount = player_amount
                    return

                elif event.type == pygame.KEYDOWN:
                    key = self.get_num(event)

                    if key is not None and type(key) == int:
                        player_amount = key

            self.display_player_number(player_amount)

    def calc_next_card_pos(self, player, player_num):
        return (player_num + 1) * self.screen_width // (self.max_cards_on_screen + 1) + (player.get_card_amount() - 1) * 30 - 60

    def render_hit(self, player, pos):
        points = self.font.render(str(player.get_points()), True, self.white)
        points_rect = points.get_rect()
        points_rect.center = (
            (pos+1)*self.screen_width//(self.max_cards_on_screen + 1), 685)

        card_image = self.card_images[player.get_card_by_index(-1)]
        image_point = (self.calc_next_card_pos(player, pos), 500)
        self.screen.blit(card_image, image_point)

        pygame.draw.rect(
            self.screen, self.background, points_rect)
        self.screen.blit(points, points_rect)

        self.render_move("HIT")

        pygame.display.update()
        self.clock.tick(30)
    def render_double(self,player, pos):
        points = self.font.render(str(player.get_points()), True, self.white)
        points_rect = points.get_rect()
        points_rect.center = (
            (pos + 1) * self.screen_width // (self.max_cards_on_screen + 1), 685)

        card_image = self.card_images[player.get_card_by_index(-1)]
        image_point = (self.calc_next_card_pos(player, pos), 500)
        self.screen.blit(card_image, image_point)

        pygame.draw.rect(
            self.screen, self.background, points_rect)
        self.screen.blit(points, points_rect)

        self.render_move("DOUBLE")

        pygame.display.update()
        self.clock.tick(30)
    def render_move(self, txt):
        pygame.mixer.music.stop()
        f = pygame.font.Font(None, 50)
        hit_popup = f.render(txt, True, (255, 0, 0))
        hit_popup_rect = hit_popup.get_rect()
        hit_popup_rect.center = (
            int(self.screen_width/2), int(self.screen_height/2))

        pygame.draw.rect(
            self.screen, self.background, hit_popup_rect)
        self.screen.blit(hit_popup, hit_popup_rect)

        pygame.display.update()
        self.clock.tick(30)

        pygame.mixer.Sound.play(self.sounds[txt.upper()])

    def init_players(self):
        self.player_nums = {}
        self.players = []
        for i in range(0, self.player_amount):
            bet = self.min_bet
            self.player_nums[i+1] = Player(i+1, bet, f"Player {i+1}")
            self.players.append(self.player_nums[i+1])
        angle = 270 / (self.player_amount + 1)
        for number in range(self.player_amount):
            player = self.players[number]
            turn_dc2()
            time.sleep(1)
            stop_dc2()
            player.get_card(self.random_card_choice())
            turn_servo1(angle)
        turn_servo1(-self.player_amount*angle)
        for number in range(self.player_amount):
            player = self.players[number]
            turn_dc2()
            time.sleep(1)
            stop_dc2()
            player.get_card(self.random_card_choice())
            player = self.players[number]
            if number >= 0 and number < 2:
                player.display_player_cards(self, number + 1)

    def random_card_choice(self):
        random_cards = random.choice(list(self.cards))
        self.cards.remove(random_cards)
        self.deleted_cards.append(random_cards)
        return random_cards

    def hit(self, player):
        turn_dc2()
        time.sleep(1)
        stop_dc2()
        player.get_card(self.random_card_choice())

    def double(self, player):
        turn_dc2()
        time.sleep(1)
        stop_dc2()
        player.get_card(self.random_card_choice())

    def display_game_over(self, text, number, color=(255, 255, 255)):
        player = self.players[number]
        name = self.font.render(
            str(f"{player.name}"), True, self.white)
        name_rect = name.get_rect()
        name_rect.center = ((number + 1) * self.screen_width //
                            (self.player_amount + 1), 650)

        pygame.draw.rect(self.screen, self.background, name_rect)
        self.screen.blit(name, name_rect)

        text = self.font.render(text, True, color)
        text_rect = text.get_rect()
        text_rect.center = (
            (number + 1) * self.screen_width // (self.player_amount + 1), 680)
        self.screen.blit(text, text_rect)

        points = self.font.render(
            "PUNTEN" + str(player.get_points()), True, self.white)
        points_rect = points.get_rect()
        points_rect.center = (
            (number + 1) * self.screen_width // (self.player_amount + 1), 600)
        self.screen.blit(points, points_rect)

        inzet = self.font.render("INZET: " + str(
            player.get_inzet()), True, self.white)
        inzet_rect = inzet.get_rect()
        inzet_rect.center = (
            (number + 1) * self.screen_width // (self.player_amount + 1) - 30, 500)
        self.screen.blit(inzet, inzet_rect)

        winst = self.font.render("WINST: " + str(
            player.get_winst()), True, self.white)
        winst_rect = winst.get_rect()
        winst_rect.center = (
            (number + 1) * self.screen_width // (self.player_amount + 1) + 30, 550)
        self.screen.blit(winst, winst_rect)

    def init_dealer(self):
        self.dealer = Player('d', 0, 'dealer')
        turn_dc2()
        time.sleep(1)
        stop_dc2()
        self.dealer.get_card(self.random_card_choice())
        turn_dc2()
        time.sleep(1)
        stop_dc2()
        self.dealer.get_card(self.random_card_choice())
        self.screen.blit(
            self.card_images[self.dealer.get_card_by_index(0)], (550, 30))
        self.screen.blit(
            self.card_images[(self.back, self.back)], (580, 30))

        pygame.display.update()
        self.clock.tick(30)

    def init_game(self):
        print("BUTTONS")
        self.init_buttons()
        print("IMAGES")
        self.init_cards()
        print("HOME")
        self.start_game()
        self.screen.fill(self.background)
        print("STARTING")
        self.init_players()
        print("DEALER")
        self.init_dealer()

        self.screen.blit(self.min_bet_txt, self.min_bet_rect)
        pygame.display.update()
        self.clock.tick(30)

    def render_bust(self, pos):
        busted = self.font.render(
            "BUSTED", True, (255, 50, 50))
        busted_rect = busted.get_rect()
        busted_rect.center = (
            (pos + 1) * self.screen_width // (self.max_cards_on_screen + 1), 720)
        self.screen.blit(busted, busted_rect)
        pygame.display.update()
        self.clock.tick(30)

    def clear_move(self):
        print("CLEAR")
        f = pygame.font.Font(None, 50)
        clear = f.render("AAAAAAAAAAAAAAAAAAAAAAAAAAA",
                         True, self.background)
        clear_rect = clear.get_rect()
        clear_rect.center = (
            int(self.screen_width/2), int(self.screen_height/2))

        pygame.draw.rect(
            self.screen, self.background, clear_rect)
        self.screen.blit(clear, clear_rect)
        pygame.display.update()

    def handle_move(self, move, player, pos):
        if move == 'OK':
            print("RUNNING HIT")
            self.hit(player)
            self.render_hit(player, pos)
            player_points = player.get_points()

            if player_points > 21:
                self.render_bust(pos)
                time.sleep(.5)
                pygame.mixer.Sound.play(self.sounds["BUST"])
                pygame.mixer.Sound.play(self.sounds["CRASH"])
                self.busted_players.append(player)
                return "STOP"
            else:
                return "CONTINUE"
        elif move == "Fakjoe":
            if player.cards[0][1] != player.cards[1][1] and len(player.cards) == 2:
                move = recognise_hand()
                return self.handle_move(move, player, pos)
            else:
                new_player = Player(player.number, self.min_bet,
                                    player.name + "-" + str(player.hand_amount))
                player.hand_amount += 1
                new_player.cards = [player.cards[1]]
                turn_dc2()
                time.sleep(1)
                stop_dc2()
                new_player.get_card(self.random_card_choice())
                player.cards = [player.cards[0]]
                turn_dc2()
                time.sleep(1)
                stop_dc2()
                player.get_card(self.random_card_choice())
                # Will this insert work?
                self.players.insert(
                    player.number + player.hand_amount - 2, new_player)
                print(self.players)
                # check good render
                self.player_amount += 1
                self.render_cards_on_screen(player.number - 1)

        elif move == 'closed':
            print('double')
            self.double(player)
            self.render_double(player, pos)
            player_points = player.get_points()

            if player_points > 21:
                self.render_bust(pos)
                time.sleep(.5)
                pygame.mixer.Sound.play(self.sounds["BUST"])
                pygame.mixer.Sound.play(self.sounds["CRASH"])
                self.busted_players.append(player)
            return "STOP"

        elif move.upper() == 'PEACE':
            self.render_move("STAND")
            return 'STOP'

    def clear_cards(self):
        rect = pygame.Rect((150, 400), (self.screen_width - 300, 350))
        pygame.draw.rect(self.screen, self.background, rect)
        pygame.display.update()

    def display_count(self, txt):
        f = pygame.font.Font(None, 80)

        count = f.render(txt, True, self.white)
        count_rect = count.get_rect()
        count_rect.center = (self.screen_width - 200, 150)
        pygame.mixer.Sound.play(self.sounds[txt])

        pygame.draw.rect(
            self.screen, (255, 0, 0), count_rect)
        self.screen.blit(count, count_rect)
        pygame.display.update()
        time.sleep(1)
        pygame.mixer.music.stop()

    def render_cards_on_screen(self, number):
        self.clear_cards()
        for i in range(-1, 2):
            if number + i <= self.player_amount - 1 and number + i >= 0:
                player = self.players[number + i]
                player.display_player_cards(self, i + 1)

    def again_screen(self):
        self.screen.blit(self.button_again, self.again_rect)
        self.screen.blit(self.button_stop, self.stop_rect)
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.again_rect.collidepoint(event.pos):
                        return True
                    elif self.stop_rect.collidepoint(event.pos):
                        return False

    def display_count_down(self, number):
        player = self.players[number]
        f = pygame.font.Font(None, 50)
        count = f.render(f"Get ready {player.name}!", True, self.white)
        count_rect = count.get_rect()
        count_rect.center = (self.screen_width - 200, 80)

        rect = pygame.Rect((self.screen_width - 350, 115), (300, 70))
        pygame.draw.rect(self.screen, (255, 0, 0), rect)
        pygame.display.update()

        pygame.draw.rect(
            self.screen, self.background, count_rect)
        self.screen.blit(count, count_rect)
        pygame.display.update()

        for i in range(3, -1, -1):
            self.display_count(str(i))
        self.display_count("DETECT")

    def display_score(self):
        self.clear_cards()
        dealer_score = self.dealer.get_points()
        for number in range(self.player_amount):
            print(f"number {number}")
            player = self.players[number]
            player_score = player.get_points()

            if player in self.busted_players:
                player.state = 'BUSTED'
                self.display_game_over("BUSTED", number, (255, 0, 0))
                continue
            elif dealer_score > 21:
                player.state = 'WIN'
                self.display_game_over("YOU WON", number)
            elif player_score > dealer_score:
                player.state = 'WIN'
                self.display_game_over("YOU WON", number)

            elif player_score == dealer_score:
                player.state = 'PUSH'
                self.display_game_over("PUSH", number)
            else:
                player.state = 'BUSTED'
                self.display_game_over("YOU LOST", number)
        pygame.display.update()
        self.clock.tick(30)

    def run_game(self):
        self.init_game()
        turn_dc1()
        self.busted_players = []
        number = 0
        angle = 270/self.player_amount
        while True:
            if number < self.player_amount:
                player = self.players[number]
                print(f"NEXT PLAYER {player.number+1}")
                self.render_cards_on_screen(number)
                turn = self.font.render(
                    f"YOUR TURN {player.name}", True, (50, 50, 50))
                turn_rect = turn.get_rect()
                turn_rect.center = (2 * self.screen_width //
                                    (self.max_cards_on_screen + 1), 450)
                self.screen.blit(turn, turn_rect)
                pygame.display.update()
                self.clock.tick(30)
                play = "CONTINUE"
                while play != "STOP":
                    print("fuclk")
                    self.display_count_down(number)
                    move = recognise_hand()
                    play = self.handle_move(move, player, 1)
                    time.sleep(1)
                    self.clear_move()

                pygame.display.update()
                self.clock.tick(30)
                pygame.draw.rect(self.screen, self.background, turn_rect)
                turn_servo1(angle)
                number += 1
            else:
                break
        # self.dealer game
        dealer_takes_card = True
        self.screen.blit(
            self.card_images[self.dealer.get_card_by_index(1)], (580, 30))
        points = self.font.render(
            str(self.dealer.get_points()), True, self.white)
        points_rect = points.get_rect()
        points_rect.center = (600, 180)
        pygame.draw.rect(self.screen, self.background, points_rect)
        self.screen.blit(points, points_rect)
        pygame.display.update()
        self.clock.tick(30)

        while dealer_takes_card:
            dealer_score = self.dealer.status()[1]
            if dealer_score > 21:
                busted = self.font.render("BUSTED", True, (255, 50, 50))
                busted_rect = busted.get_rect()
                busted_rect.center = (600, 210)
                self.screen.blit(busted, busted_rect)
                dealer_takes_card = False
            elif dealer_score >= 17:
                dealer_takes_card = False
            else:
                turn_dc2()
                time.sleep(1)
                stop_dc2()
                self.dealer.get_card(self.random_card_choice())
                self.screen.blit(self.card_images[self.dealer.get_card_by_index(-1)],
                                 (550 + (self.dealer.get_card_amount() - 1) * 30, 30))
                points = self.font.render(
                    str(self.dealer.get_points()), True, self.white)
                points_rect = points.get_rect()
                points_rect.center = (600, 180)
                pygame.draw.rect(self.screen, self.background, points_rect)
                self.screen.blit(points, points_rect)
                dealer_score = self.dealer.get_points()

            pygame.display.update()
            self.clock.tick(30)

        self.display_score()

    def __init__(self):
        pygame.init()

        self.screen_width, self.screen_height = 1200, 800
        self.font = pygame.font.Font(None, 36)
        self.background = (1, 150, 32)

        self.min_bet = 1
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        pygame.display.set_caption("Blackjack self.cards")

        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        self.faces = ["h", "d", "c", "s"]
        self.values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.sounds = {}

        self.sounds['0'] = pygame.mixer.Sound("sounds/0.mp3")
        self.sounds['1'] = pygame.mixer.Sound("sounds/1.mp3")
        self.sounds['2'] = pygame.mixer.Sound("sounds/2.mp3")
        self.sounds['3'] = pygame.mixer.Sound("sounds/3.mp3")

        self.sounds['DETECT'] = pygame.mixer.Sound("sounds/DETECT.mp3")
        self.sounds['FAKJOE'] = pygame.mixer.Sound("sounds/FAKJOE.mp3")
        self.sounds['HIT'] = pygame.mixer.Sound("sounds/HIT.mp3")
        self.sounds['DOUBLE'] = pygame.mixer.Sound("sounds/DOUBLE.mp3")
        self.sounds['STAND'] = pygame.mixer.Sound("sounds/PEACE.mp3")
        self.sounds['BUST'] = pygame.mixer.Sound("sounds/BUST.mp3")
        self.sounds['CRASH'] = pygame.mixer.Sound("sounds/CRASH.mp3")

        self.clock = pygame.time.Clock()
        a = True
        while a:
            self.run_game()
            a = self.again_screen()
        stop_dc1()
        cap.release()
        pygame.quit()
        servo_stop()
        quit()


GameState()
