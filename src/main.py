#!/usr/bin/env python3

import os
import csv
import cv2
import sys
import time
import yaml
import pygame
import numpy as np

# Custom libraries
from src.keyboard import keyboard
from fonts import lato
import colors

with open("config.yaml") as file:
    dictionary = yaml.load(file)
usr = dictionary["usr"]
app = dictionary["app"]


def get_file_paths(directory):
    """
    :param directory: directory to collect file names from (string)
    :return: file paths (list)
    """
    file_names = []
    path = directory
    if os.path.isdir(directory):
        for item in os.listdir(directory):
            item = "/".join([path, item])
            if os.path.isdir(item):
                file_names += get_file_paths(item)
            elif os.path.isfile(item):
                file_names.append(item)
    else:
        print("Warning: " + directory + " not found.")
    return file_names


class ImageLabel(object):

    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(app["size"])                  # Initialise window & set size
        pygame.display.set_caption(app["title"])                            # Caption window
        self.clock = pygame.time.Clock()                                    # Initialise clock
        self.mouse_pos = (0, 0)                                             # Initialise tuple for mouse pos
        self.mouse_click = (0, 0, 0)                                        # Initialise tuple for mouse click
        self.key_status = {}                                                # Initialise key status dict
        [self.key_status.update({key: False}) for key in keyboard]          # Populate key status dict
        self.pages = {"label": LabelPage(self.window),
                      "view": ViewPage(self.window)}                        # Initialise pages
        self.current_page = "label"                                         # Set the current page

    def main(self):
        while True:
            self.current_page = self.pages[self.current_page].run()


class Page(object):

    def __init__(self):
        self.mouse_pos = (0, 0)                                         # Initialise tuple for mouse pos
        self.mouse_click = (0, 0, 0)                                    # Initialise tuple for mouse click
        self.key_status = {}                                            # Initialise key status dict
        [self.key_status.update({key: False}) for key in keyboard]      # Populate key status dict
        self.clock = pygame.time.Clock()                                # Initialise clock

    def event_handler(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_click = pygame.mouse.get_pressed()
        for event in pygame.event.get():                                # Get all pygame events
            if event.type == pygame.QUIT:                               # If an event is of type quit
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:                          # If key event is key down
                for key, value in keyboard.items():
                    if event.key == value:
                        self.key_status[key] = True                     # Update key_status dictionary
                        break
            elif event.type == pygame.KEYUP:                            # If key event is key up
                for key, value in keyboard.items():
                    if event.key == value:
                        self.key_status[key] = False                    # Update key_status dictionary
                        break

    @staticmethod
    def text(display, message, col, pos, font):
        text_surf = font.render(message, True, col)
        text_rect = text_surf.get_rect()
        text_rect.center = (pos[0], pos[1])
        display.blit(text_surf, text_rect)


class LabelPage(Page):

    def __init__(self, window):
        Page.__init__(self)
        self.window = window
        self.current_cat = 0
        self.current_rect = [0, 0, 0, 0]
        self.was_pressed = [0, 0, 0]
        self.rects = []
        self.cats = []
        self.image = None
        self.next_page = None
        self.p0 = None
        self.t0 = time.time()
        self.image_paths = []
        self.get_image_paths()

    def run(self):
        self.next_page = None
        self.load_image(usr["current_image"], 2)
        while True:
            self.window.fill(colors.WHITE)
            self.show_image()
            self.event_handler()
            self.handle_keys(0.3)
            if self.next_page is not None:
                return self.next_page
            self.handle_mouse()
            self.draw_rects()
            self.current_image_text((self.image.shape[0] + 100, 100))
            self.category_menu((self.image.shape[0] + 100, 200))
            pygame.display.update()
            self.clock.tick(app["fps"])

    def handle_mouse(self):
        # If mouse is clicked once, change was_pressed and record mouse pos
        shape = self.image.shape
        if self.mouse_click[0] == 1 and self.was_pressed[0] == 0:
            self.was_pressed[0] = 1
            self.p0 = self.mouse_pos
            self.p0 = (min(self.p0[0], shape[0]), min(self.p0[1], shape[1]))

        # If mouse is being pressed, draw rect
        elif self.mouse_click[0] == 1:
            self.current_rect = (max(self.p0[0], 0),
                                 max(self.p0[1], 0),
                                 min(self.mouse_pos[0] - self.p0[0], shape[0] - self.p0[0]),
                                 min(self.mouse_pos[1] - self.p0[1], shape[1] - self.p0[1]))
            pygame.draw.rect(self.window, usr["cat_cols"][self.current_cat], self.current_rect, 1)

        # If mouse is released once, store rect, category and change was_pressed
        elif self.mouse_click[0] == 0 and self.was_pressed[0] == 1:
            self.was_pressed[0] = 0
            self.rects.append(self.current_rect)
            self.cats.append(self.current_cat)

    def handle_keys(self, delay=0.0):
        # Time since a key was last used
        dt = time.time() - self.t0

        # Key presses for changing category
        for i in range(len(usr["cat_names"])):
            if self.key_status["k_" + str(i)] is True:
                self.current_cat = i

        # Delete if backspace is pressed
        if self.key_status["k_backspace"] is True and dt > delay:
            self.t0 = time.time()
            self.rects = self.rects[:-1]
            self.cats = self.cats[:-1]

        # Skip image (don't save)
        if self.key_status["k_space"] is True and dt > delay:
            self.t0 = time.time()
            self.next_image()

        # Done - Save and next image
        if self.key_status["k_return"] is True and dt > delay:
            self.t0 = time.time()
            self.save_labels()
            self.next_image()
            self.update_config()

        # Change page if kp enter is pressed
        if self.key_status["k_kp_enter"] is True:
            self.next_page = "view"

    def draw_rects(self):
        for cat, rect in zip(self.cats, self.rects):
            pygame.draw.rect(self.window, usr["cat_cols"][cat], rect, 1)

    def current_image_text(self, pos):
        self.text(self.window,
                  "Image",
                  colors.BLACK,
                  pos,
                  lato(30))
        self.text(self.window,
                  usr["current_image"].split("/")[-1],
                  colors.BLACK,
                  (pos[0], pos[1] + 35),
                  lato(20))

    def save_labels(self):
        # Check directory exists (create it if necessary)
        path = ""
        for folder in usr["out_file"].split("/")[:-1]:
            path += folder + "/"
            if not os.path.isdir(path):
                os.mkdir(path)

        # Organise line to write to file
        line = []
        for cat, rect in zip(self.cats, self.rects):
            box = self.rect2box(rect)
            box = list(map(lambda x: int(x / usr["scale"]), box))
            label = [[cat], box]
            label = [item for sublist in label for item in sublist]
            line.append(label)
        line = [item for sublist in line for item in sublist]

        # Write line to file
        with open(usr["out_file"], "a") as f:
            f.write(usr["current_image"]
                    + ","
                    + ",".join(list(map(str, line)))
                    + "\n")

    def category_menu(self, pos):
        self.text(self.window,
                  "Categores",
                  colors.BLACK,
                  pos,
                  lato(30))
        for i, (name, col) in enumerate(zip(usr["cat_names"], usr["cat_cols"])):
            self.text(self.window,
                      str(i) + " - " + name,
                      col,
                      (pos[0], (i + 1) * 25 + pos[1] + 10),
                      lato(20))
        pygame.draw.rect(self.window,
                         usr["cat_cols"][self.current_cat],
                         (pos[0] - 70, (self.current_cat + 1) * 25 + pos[1] - 3, 140, 25),
                         2)

    def next_image(self):
        self.rects = []
        self.cats = []
        index = self.image_paths.index(usr["current_image"])
        usr["current_image"] = self.image_paths[index + 1]
        self.load_image(usr["current_image"], 2)

    def get_image_paths(self):
        image_paths = get_file_paths(usr["image_dir"])                 # Get image file paths
        image_paths = self.filter_frames(image_paths, usr["frames"])   # Remove filter out some frames
        self.image_paths = sorted(image_paths, key=str.lower)          # Sort file paths
        if usr["current_image"] not in self.image_paths:
            print(usr["current_image"] + " not found.")
            print("Starting at " + self.image_paths[0] + ".")
            usr["current_image"] = self.image_paths[0]

    def load_image(self, file_path, scale=1):
        image = cv2.imread(file_path)
        b, g, r = cv2.split(image)
        image = cv2.merge([r, g, b])
        image = np.fliplr(image)
        image = np.rot90(image)
        self.image = cv2.resize(image, (0, 0), fx=scale, fy=scale)

    def show_image(self):
        surf = pygame.surfarray.make_surface(self.image)
        self.window.blit(surf, (0, 0))

    @staticmethod
    def update_config():
        # Update config file
        with open("config.yaml", "w") as f:
            yaml.dump({"usr": usr, "app": app}, f)

    @staticmethod
    def rect2box(rect):
        box = [rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]]
        box = [min(box[0], box[2]),
               min(box[1], box[3]),
               max(box[0], box[2]),
               max(box[1], box[3])]
        return box

    @staticmethod
    def filter_frames(file_paths, frames):
        return [path for path in file_paths if
                int(path.split("/")[-1].split(".")[0].split("_")[-1]) in frames]


class ViewPage(Page):

    def __init__(self, window):
        Page.__init__(self)
        self.window = window
        self.rects = []
        self.cats = []
        self.n = 0
        self.t0 = time.time()
        self.image = None
        self.image_paths = []
        self.next_page = None
        self.get_image_paths()

    def run(self):
        self.next_page = None
        self.get_image_paths()
        self.load_image(self.image_paths[self.n])
        while True:
            self.window.fill(colors.WHITE)
            self.show_image()
            self.event_handler()
            self.handle_keys(0.3)
            if self.next_page is not None:
                return self.next_page
            self.draw_rects()
            self.current_image_text((self.image.shape[0] + 100, 100))
            self.category_menu((self.image.shape[0] + 100, 200))
            pygame.display.update()
            self.clock.tick(app["fps"])

    def handle_keys(self, delay=0.0):
        # Time since a key was last used
        dt = time.time() - self.t0

        # Next image
        if self.key_status["k_space"] is True and dt > delay:
            self.t0 = time.time()
            self.n += 1
            if self.n > len(self.image_paths) - 1:
                self.n = 0
            self.load_image(self.image_paths[self.n])

        # Previous image
        if self.key_status["k_backspace"] is True and dt > delay:
            self.t0 = time.time()
            self.n -= 1
            if self.n < 0:
                self.n = len(self.image_paths) - 1
            self.load_image(self.image_paths[self.n])

        # Change page if kp enter is pressed
        if self.key_status["k_kp_enter"] is True:
            self.next_page = "label"

    def draw_rects(self):
        for cat, rect in zip(self.cats[self.n], self.rects[self.n]):
            pygame.draw.rect(self.window, usr["cat_cols"][cat], rect, 1)

    def category_menu(self, pos):
        self.text(self.window,
                  "Categores",
                  colors.BLACK,
                  pos,
                  lato(30))
        for i, (name, col) in enumerate(zip(usr["cat_names"], usr["cat_cols"])):
            self.text(self.window,
                      str(i) + " - " + name,
                      col,
                      (pos[0], (i + 1) * 25 + pos[1] + 10),
                      lato(20))

    def current_image_text(self, pos):
        self.text(self.window,
                  "Image",
                  colors.BLACK,
                  pos,
                  lato(30))
        self.text(self.window,
                  self.image_paths[self.n].split("/")[-1],
                  colors.BLACK,
                  (pos[0], pos[1] + 35),
                  lato(20))

    def get_image_paths(self):
        self.cats = []
        self.rects = []
        self.image_paths = []
        with open(usr["out_file"], "r") as f:
            csv_file = csv.reader(f, delimiter=",", quotechar="|")
            for row in csv_file:
                row = list(filter(None, row))
                self.image_paths.append(row[0])
                cats = []
                rects = []
                row = row[1:]
                for obj in range(int(len(row) / 5)):
                    item = row[obj * 5: (obj+1) * 5]
                    rects.append(self.box2rect(list(map(int, item[1:5]))))
                    cats.append(int(item[0]))
                self.cats.append(cats)
                self.rects.append(rects)

    def load_image(self, file_path, scale=1):
        image = cv2.imread(file_path)
        b, g, r = cv2.split(image)
        image = cv2.merge([r, g, b])
        image = np.fliplr(image)
        image = np.rot90(image)
        self.image = cv2.resize(image, (0, 0), fx=scale, fy=scale)

    def show_image(self):
        surf = pygame.surfarray.make_surface(self.image)
        self.window.blit(surf, (0, 0))

    @staticmethod
    def box2rect(box):
        rect = [min(box[0], box[2]),
                min(box[1], box[3]),
                abs(box[0] - box[2]),
                abs(box[1] - box[3])]
        return rect


if __name__ == "__main__":
    image_label = ImageLabel()
    image_label.main()
