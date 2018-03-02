#!/usr/bin/env python3

import pygame


def lato(size, style=None):
    path = "../fonts/Lato/"
    if style == "black":
        return pygame.font.Font(path + "Lato-Black.ttf", int(size))
    elif style == "black_italic":
        return pygame.font.Font(path + "Lato-BlackItalic.ttf", int(size))
    elif style == "bold":
        return pygame.font.Font(path + "Lato-Bold.ttf", int(size))
    elif style == "bold_italic":
        return pygame.font.Font(path + "Lato-BoldItalic.ttf", int(size))
    elif style == "hairline":
        return pygame.font.Font(path + "Lato-Hairline.ttf", int(size))
    elif style == "hairline_italic":
        return pygame.font.Font(path + "Lato-HairlineItalic.ttf", int(size))
    elif style == "italic":
        return pygame.font.Font(path + "Lato-Italic.ttf", int(size))
    elif style == "light":
        return pygame.font.Font(path + "Lato-Light.ttf", int(size))
    elif style == "light_italic":
        return pygame.font.Font(path + "Lato-LightItalic.ttf", int(size))
    else:
        return pygame.font.Font(path + "Lato-Regular.ttf", int(size))


def lit_sans_medium(size, style=None):
    path = "../fonts/LitSans-Medium/"
    return pygame.font.Font(path + "LitSans-Medium.otf", int(size))
