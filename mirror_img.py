from PIL.Image import open as i_open, FLIP_LEFT_RIGHT
import argparse
import os
from crop_img import get_img_info


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create a pdf template with images in a given folder'
    )

    parser.add_argument(
        'img_path',
        nargs=1,
        type=str,
        help='path to img to be mirrored'
    )

    img_path = parser.parse_args().img_path[0]
    folder, img_name, _ = get_img_info(img_path)
    i_open(f'{folder}/{img_name}.jpg')\
    .transpose(FLIP_LEFT_RIGHT)\
    .save(f'{folder}/{img_name}_mirrored.jpg')
 