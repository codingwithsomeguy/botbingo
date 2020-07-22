"""simple image bingo card generator in python, originally for bots"""

import io
import math
import random

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont


CARD_SIZE = (720, 720)
NUDGE = 8
MODE = "RGBA"
IMAGE_FORMAT = "PNG"

PALETTE = ["#597498", "#b8c6d8", "#8499b6", "#37547d", "#1d3a62"]
LINE_COLOR = PALETTE[4]
BG_COLOR = PALETTE[1]
FG_COLOR = LINE_COLOR
LOGO_COLOR = PALETTE[3]

# move this to an init
FONT_FILE = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
FONT_SIZE = 20
FONT = PIL.ImageFont.truetype(FONT_FILE, size=FONT_SIZE)
SMALL_FONT_SIZE = math.floor(FONT_SIZE * 0.8)
SMALL_FONT = PIL.ImageFont.truetype(FONT_FILE, size=SMALL_FONT_SIZE)
LOGO_FILE = "logo.png"
DESIRED_LOGO_WIDTH = 40


def get_box_size(image_size, number_of_cells):
    """get the box size of each cell on the board"""
    box_width = math.ceil(image_size[0] / number_of_cells)
    box_height = math.ceil(image_size[1] / number_of_cells)

    return box_width, box_height


def draw_grid(draw):
    """draw the grid lines"""
    image_size = draw.im.size

    box_width, box_height = get_box_size(image_size, 5)

    draw.rectangle(
        ((0, 0), (image_size[0] - 1, image_size[1] - 1)),
        outline="blue",
        width=1,
    )
    for col in range(1, 5):
        xline = col * box_width
        draw.line(
            ((xline, 0), (xline, image_size[1])), width=5, fill=LINE_COLOR
        )

        yline = col * box_height
        draw.line(
            ((0, yline), (image_size[0], yline)), width=5, fill=LINE_COLOR
        )


def get_center_box(boxes_per_side):
    """simple center box selector"""
    return math.floor(boxes_per_side / 2)


def get_left_top(draw, image_size, boxes_per_side, location, word):
    """overly simple text layout top left pixel selector"""
    # draw is needed for font metrics, but could use a private draw

    chosen_font = FONT
    box_size = get_box_size(image_size, boxes_per_side)
    # not using text_height due to descenders between fonts
    #  causing issues
    text_width, _ = draw.textsize(word, font=FONT)
    if text_width > (box_size[0] - NUDGE):
        text_width, _ = draw.textsize(word, font=SMALL_FONT)
        chosen_font = SMALL_FONT

    left_side = math.floor(
        location[1] * box_size[0] + (box_size[0] / 2) - (text_width / 2)
    )

    top_side = math.floor(
        location[0] * box_size[1] + (box_size[1] / 2) - (chosen_font.size / 2)
    )

    return (left_side, top_side), chosen_font


def draw_labels(draw, center_label, labels, boxes_per_side):
    """draw the labels on the grid"""
    image_size = draw.im.size
    center_box_side = get_center_box(boxes_per_side)

    for which_word in range(boxes_per_side ** 2):
        loc = (
            math.floor(which_word / boxes_per_side),
            which_word % boxes_per_side,
        )
        chosen_word = labels[which_word]
        if loc[0] == center_box_side and loc[1] == center_box_side:
            chosen_word = center_label

        left_top, chosen_font = get_left_top(
            draw, image_size, boxes_per_side, loc, chosen_word
        )
        draw.text(left_top, chosen_word, font=chosen_font, fill=FG_COLOR)


def draw_logo(img, draw):
    """draws the logo and branding"""
    font = PIL.ImageFont.truetype(FONT_FILE, size=FONT_SIZE)

    rawlogo = PIL.Image.open(LOGO_FILE)

    aspect = rawlogo.size[0] / rawlogo.size[1]
    logo = rawlogo.resize(
        (DESIRED_LOGO_WIDTH, math.floor(DESIRED_LOGO_WIDTH / aspect))
    )

    img.paste(
        logo,
        (img.size[0] - logo.size[0] - 1, img.size[1] - logo.size[1] - 1,),
    )

    logo_text = "@SomeCodingGuy"
    text_width, text_height = draw.textsize(logo_text, font=font)
    top_left = (
        img.size[0] - text_width - logo.size[0] - 10,
        img.size[1] - text_height - 3,
    )
    draw.text(top_left, logo_text, font=font, fill=LOGO_COLOR)


def load_word_set(filename):
    """loads the words used as bingo labels, first line is the center"""
    lines = open(filename).readlines()
    if len(lines) < 25:
        raise Exception("Not enough labels in %s" % filename)

    total_word_list = [x.strip() for x in lines]
    center_word = total_word_list[0]
    words = random.sample(total_word_list[1:], 25)

    return center_word, words


def generate_card(word_set_filename):
    """generate_card generates a bingo card"""
    center_word, words = load_word_set(word_set_filename)

    card_image = PIL.Image.new(MODE, CARD_SIZE, BG_COLOR)
    draw = PIL.ImageDraw.Draw(card_image)

    draw_grid(draw)
    draw_labels(draw, center_word, words, 5)
    draw_logo(card_image, draw)

    # save the image to a binary buffer and rewind it
    result_image_bytes = io.BytesIO()
    card_image.save(result_image_bytes, format=IMAGE_FORMAT)
    result_image_bytes.seek(0)

    return result_image_bytes


if __name__ == "__main__":
    # WORD_SET = "/usr/share/dict/words"
    WORD_SET = "bingotestlabels.txt"
    image = generate_card(WORD_SET)
    open("bingotestcard.png", "wb").write(image.read())
