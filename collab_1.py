import pygame
from pygame.locals import *
import os
import sys
import random
import csv
import copy
import argparse
import itertools

import cv2 as cv
import numpy as np
import mediapipe as mp

from model import KeyPointClassifier


DEBUG = False


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


class Players:
    def __init__(self):
        self.cards = []
        self.points = 0
        self.amount_of_aces = 0
        self.add_points()

    def get_card(self, card):
        self.cards.append(card)
        self.add_points()

    def add_points(self):
        points = 0
        amount_of_aces = 0
        for card in self.cards:
            print(card)
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


# Initialize Pygame
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

        self.play_rect = self.play_button.get_rect()
        self.hit_rect = self.button_hit.get_rect()
        self.double_rect = self.button_double.get_rect()
        self.stand_rect = self.button_stand.get_rect()
        self.split_rect = self.split.get_rect()
        self.again_rect = self.button_again.get_rect()
        self.stop_rect = self.button_stop.get_rect()

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

    def get_num(self, event):
        if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]:

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

                    if key is not None:
                        player_amount = key

            self.display_player_number(player_amount)

    def render_hit(self, player_num):
        player = self.players[player_num]
        points = self.font.render(str(player.get_points()), True, self.white)
        points_rect = points.get_rect()
        points_rect.center = (
            (player_num + 1) * self.screen_width // (self.player_amount + 1), 650)

        self.screen.blit(self.card_images[player.get_card_by_index(-1)],
                         ((player_num + 1) * self.screen_width // (self.player_amount + 1) +
                          (player.get_card_amount() - 1) * 30 - 60, 500))

        pygame.draw.rect(
            self.screen, self.background, points_rect)
        self.screen.blit(points, points_rect)
        pygame.display.update()
        self.clock.tick(30)

    def init_players(self):
        Player1 = Players()
        Player2 = Players()
        Player3 = Players()
        Player4 = Players()
        Player5 = Players()
        Player6 = Players()
        Player7 = Players()
        max_players = [Player1, Player2, Player3,
                       Player4, Player5, Player6, Player7]
        self.players = []
        for i in range(0, self.player_amount):
            self.players.append(max_players[i])

        for number in range(self.player_amount):
            player = self.players[number]
            player.get_card(self.random_card_choice())
            player.get_card(self.random_card_choice())
            player = self.players[number]

    def random_card_choice(self):
        random_cards = random.choice(list(self.cards))
        self.cards.remove(random_cards)
        self.deleted_cards.append(random_cards)
        return random_cards

    def hit(self, player):
        player.get_card(self.random_card_choice())

    def double(self, player):
        player.get_card(self.random_card_choice())

    def display_game_over(self, text, number):
        text = self.font.render(text, True, self.white)
        text_rect = text.get_rect()
        text_rect.center = (
            (number + 1) * self.screen_width // (self.player_amount + 1), 680)
        self.screen.blit(text, text_rect)

    def run_game(self, running):
        while running:
            print("BUTTONS")
            self.init_buttons()
            print("IMAGES")
            self.init_cards()
            print("HOME")
            self.start_game()
            print("STARTING")
            self.init_players()
            self.screen.fill(self.background)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.update()
            self.clock.tick(30)

            dealer = Players()
            dealer.get_card(self.random_card_choice())
            self.screen.blit(
                self.card_images[dealer.status()[0][0]], (550, 30))
            points = self.font.render(
                str(dealer.status()[1]), True, self.white)
            points_rect = points.get_rect()
            points_rect.center = (600, 180)
            self.screen.blit(points, points_rect)
            pygame.display.update()
            self.clock.tick(30)
            for number in range(self.player_amount):
                player = self.players[number]
                points = self.font.render(
                    str(player.get_points()), True, self.white)
                points_rect = points.get_rect()
                points_rect.center = ((number + 1) * self.screen_width //
                                      (self.player_amount + 1), 650)
                self.screen.blit(self.card_images[player.get_card_by_index(0)], ((
                    number+1) * self.screen_width//(self.player_amount+1) - 60, 500))
                pygame.display.update()
                self.clock.tick(30)
                self.screen.blit(self.card_images[player.get_card_by_index(1)],
                                 ((number+1) * self.screen_width//(self.player_amount+1) +
                                  (player.get_card_amount()-1)*30 - 60, 500))

                pygame.draw.rect(self.screen, self.background, points_rect)
                self.screen.blit(points, points_rect)
                pygame.display.update()
                self.clock.tick(30)

            dealer.get_card(self.random_card_choice())
            self.screen.blit(
                self.card_images[(self.back, self.back)], (580, 30))
            pygame.display.update()
            self.clock.tick(30)

            # ask for the move
            busted_player = []

            for number in range(self.player_amount):
                turn = self.font.render("YOUR TURN", True, (50, 50, 50))
                turn_rect = turn.get_rect()
                turn_rect.center = ((number + 1) * self.screen_width //
                                    (self.player_amount + 1), 450)
                self.screen.blit(turn, turn_rect)
                pygame.display.update()
                self.clock.tick(30)
                move = None
                move = recognise_hand()
                pygame.time.delay(1000)
                player = self.players[number]
                if move == 'OK':
                    move = None
                    run_hit = True
                    while run_hit:
                        print("RUNNING HIT")
                        self.hit(player)
                        self.render_hit(number)
                        player_points = player.get_points()

                        if player_points > 21:
                            busted = self.font.render(
                                "BUSTED", True, (255, 50, 50))
                            busted_rect = busted.get_rect()
                            busted_rect.center = (
                                (number + 1) * self.screen_width // (self.player_amount + 1), 680)
                            self.screen.blit(busted, busted_rect)
                            pygame.display.update()
                            self.clock.tick(30)
                            busted_player.append(player)
                            run_hit = False
                        else:
                            move = recognise_hand()
                            pygame.time.delay(1000)
                            if move == 'OK':
                                run_hit = True
                            else:
                                run_hit = False
                elif move == 'Fakjoe':
                    self.double(player)
                    points = self.font.render(
                        str(player.get_points()), True, self.white)
                    points_rect = points.get_rect()
                    points_rect.center = (
                        (number + 1) * self.screen_width // (self.player_amount + 1), 650)
                    pygame.draw.rect(self.screen, self.background, points_rect)
                    self.screen.blit(points, points_rect)
                    pygame.display.update()
                    self.clock.tick(30)
                    player_status = player.status()
                    self.screen.blit(self.card_images[player.get_card_by_index(-1)], ((number + 1) * self.screen_width // (
                        self.player_amount + 1) + (player.get_card_amount() - 1) * 30 - 60, 500))

                    if player_status[1] > 21:
                        busted = self.font.render(
                            "BUSTED", True, (255, 50, 50))
                        busted_rect = busted.get_rect()
                        busted_rect.center = (
                            (number + 1) * self.screen_width // (self.player_amount + 1), 680)
                        self.screen.blit(busted, busted_rect)
                        busted_player.append(player)
                    else:
                        points = self.font.render(
                            str(player.status()[1]), True, self.white)
                        points_rect = points.get_rect()
                        points_rect.center = (
                            (number + 1) * self.screen_width // (self.player_amount + 1), 650)
                        pygame.draw.rect(
                            self.screen, self.background, points_rect)
                        self.screen.blit(points, points_rect)
                pygame.display.update()
                self.clock.tick(30)
                pygame.draw.rect(self.screen, self.background, turn_rect)

            # Dealer game
            dealer_takes_card = True
            dealer_busted = False
            self.screen.blit(
                self.card_images[dealer.status()[0][1]], (580, 30))
            points = self.font.render(
                str(dealer.status()[1]), True, self.white)
            points_rect = points.get_rect()
            points_rect.center = (600, 180)
            pygame.draw.rect(self.screen, self.background, points_rect)
            self.screen.blit(points, points_rect)
            pygame.display.update()
            self.clock.tick(30)

            while dealer_takes_card:
                dealer_score = dealer.status()[1]
                if dealer_score > 21:
                    busted = self.font.render("BUSTED", True, (255, 50, 50))
                    busted_rect = busted.get_rect()
                    busted_rect.center = (600, 210)
                    self.screen.blit(busted, busted_rect)
                    dealer_busted = True
                    dealer_takes_card = False
                elif dealer_score >= 17:
                    dealer_takes_card = False
                else:
                    dealer.get_card(self.random_card_choice())
                    self.screen.blit(self.card_images[dealer.status()[0][-1]],
                                     (550 + (len(dealer.status()[0]) - 1) * 30, 30))
                    points = self.font.render(
                        str(dealer.status()[1]), True, self.white)
                    points_rect = points.get_rect()
                    points_rect.center = (600, 180)
                    pygame.draw.rect(self.screen, self.background, points_rect)
                    self.screen.blit(points, points_rect)
                    dealer_score = dealer.status()[1]
                pygame.display.update()
                self.clock.tick(30)
            # Score players
            if dealer_busted is False:
                for number in range(self.player_amount):
                    player = self.players[number]
                    player_score = player.get_points()

                    print('score player en dealer')
                    print(player_score)
                    print(dealer_score)
                    if player in busted_player:
                        pass
                    elif player_score > dealer_score:
                        self.display_game_over("YOU WON", number)
                    elif player_score == dealer_score:
                        self.display_game_over("PUSH", number)
                    else:
                        self.display_game_over("YOU LOST", number)
                pygame.display.update()
                self.clock.tick(30)
            if dealer_busted is True:
                for number in range(self.player_amount):
                    player = self.players[number]
                    if player not in busted_player:
                        you_win = self.font.render("YOU WON", True, self.white)
                        you_win_rect = you_win.get_rect()
                        you_win_rect.center = (
                            (number + 1) * self.screen_width // (self.player_amount + 1), 680)
                        self.screen.blit(you_win, you_win_rect)

            play_again = True
            for card in self.deleted_cards:
                self.cards.append(card)

            self.screen.blit(self.button_again, self.again_rect)
            self.screen.blit(self.button_stop, self.stop_rect)
            pygame.display.update()
            self.clock.tick(30)
            while play_again:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN and play_again:
                        if self.again_rect.collidepoint(event.pos):
                            running = True
                        elif self.stop_rect.collidepoint(event.pos):
                            running = False
                            cap.release()
                            pygame.quit()
                            sys.exit()
                        pygame.draw.rect(
                            self.screen, self.background, self.again_rect)
                        pygame.draw.rect(
                            self.screen, self.background, self.stop_rect)
                        pygame.display.update()
                        self.clock.tick(30)
                        play_again = False

    def __init__(self):
        pygame.init()

        self.screen_width, self.screen_height = 1200, 800
        self.font = pygame.font.Font(None, 36)
        self.background = (1, 150, 32)

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        pygame.display.set_caption("Blackjack self.cards")

        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        self.faces = ["h", "d", "c", "s"]
        self.values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

        self.clock = pygame.time.Clock()
        running = True
        self.run_game(running)


GameState()
