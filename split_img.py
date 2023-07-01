from PIL.Image import open as i_open
import argparse
import os
from crop_img import aspects, get_img_info

def split(i, folder, img_name):
    w, h = i.size
    img_name_1 = img_name.split('_')[0]
    img_name_2 = img_name.split('_')[1]

    target_h = w*aspects[img_name_1]
    if target_h < h:
        print('top')
        bottom = w*h/aspects[img_name_1]
        box1 = (0, 0, w, bottom)
        right = w*aspects[img_name_2]
        box2 = (0, right, w, h)
    else:
        left = w - h/aspects[img_name_1]
        box1 = (left, 0, w, h)
        right = w - h/aspects[img_name_2]
        box2 = (0, 0, right, h)

    i.crop(box1).save(f'{folder}/{img_name_1}.jpg')
    i.crop(box2).save(f'{folder}/{img_name_2}.jpg')

def split_middle(i, folder, img_name):
    w, h = i.size
    img_name_1 = img_name.split('_')[0]
    img_name_2 = img_name.split('_')[1]

    box1 = (0, 0, w/2, h)
    box2 = (w/2, 0, w, h)

    i.crop(box1).save(f'{folder}/{img_name_1}.jpg')
    i.crop(box2).save(f'{folder}/{img_name_2}.jpg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create a pdf template with images in a given folder'
    )

    parser.add_argument(
        'img_path',
        nargs=1,
        type=str,
        help='path to img to be splitted'
    )

    img_path = parser.parse_args().img_path[0]
    folder, img_name, _ = get_img_info(img_path)
    split_middle(i_open(f'{folder}/{img_name}.jpg'), folder, img_name)