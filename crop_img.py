from PIL.Image import open as i_open
import argparse
import os

aspects = {
    'top': 1/2,
    'bottom': 1/2,
    'left': 7/20,
    'right': 7/20,
    'front': 7/10,
    'back': 7/10
}

def get_img_info(img_path, aspects=aspects):
    folder = img_path.split('/')[0]
    img_name = img_path.split('/')[-1].split('.')[0]
    aspect = aspects[img_name] if img_name in aspects else None
    return folder, img_name, aspect

def load_and_crop(img_path):
    folder, img_name, aspect = get_img_info(img_path)
    i = i_open(img_path)
    crop(i, aspect, folder, img_name)

def crop(i, aspect, folder, img_name):
    w, h = i.size
    target_h = w*aspect
    if target_h < h:
        print('top')
        i.crop((0,h-w*aspect,w, h))\
    .save(f'{folder}/{img_name}.jpg')
    else:
        i.crop((w - h/aspect,0,h/aspect, h))\
    .save(f'{folder}/{img_name}.jpg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create a pdf template with images in a given folder'
    )

    parser.add_argument(
        'folder_name',
        nargs=1,
        type=str,
        help='folder name of the images to be printed'
    )

    folder = parser.parse_args().folder_name[0]
    images_paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.jpg')]
    images_paths = [i for i in images_paths if i.split('/')[-1].split('.')[0] in aspects]
    print(images_paths)

    for p in images_paths: load_and_crop(p)