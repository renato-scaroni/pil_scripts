from itertools import combinations
from PIL import Image
from PIL.Image import open as i_open
from PIL import ImageDraw
import argparse
import os
import sys

DPI = 300 # dots per inch
PAGE_WIDTH = 11.7 # inches, A4 paper
PAGE_HEIGHT = 8.27 # inches, A4 paper
MARGIN = .125 # 1/8 inch margin, same as the bleeding area for each card
OUTPUT_FILE = 'box_template.pdf'
box_dims_cm ={
    'length': 20,
    'height': 7,
    'depth': 10
}

# compute width and height in pixels
width, height = int(PAGE_HEIGHT * DPI), int(PAGE_WIDTH * DPI) 
# compute margin in pixels
margin = MARGIN * DPI 

# parse inputs
parser = argparse.ArgumentParser(
    description='Create a pdf template with images in a given folder'
)

parser.add_argument(
    'folder_name',
    nargs=1,
    type=str,
    help='folder name of the images to be printed'
)

print("loading images...")
folder_name = parser.parse_args().folder_name[0]
images_paths = [os.path.join(folder_name, f) for f in os.listdir(folder_name) if f.endswith('.jpg')]
def order_rule(img_path):
    img_name = img_path.split('/')[-1].split('.')[0]
    order = ['top', 'bottom', 'left', 'right', 'front', 'back']
    order = {order[i]: i for i in range(len(order))}
    return order[img_name]
images_paths.sort(key=order_rule)
print(images_paths)
images = [i_open(i) for i in images_paths]

def compute_box_positions(box_sides_dims, margin=margin, width=width, height=height):
    vw_width, vw_height = width - 2*margin, height - 2*margin
    curr_x, curr_y = margin, margin
    page = 0
    boxes = []
    for box in box_sides_dims:
        if box[0] > vw_width or box[1] > vw_height:
            print(f'box {box} is too big for the page, skipping...')
            continue
        
        if curr_x + box[0] > vw_width:
            curr_x = margin
            curr_y += boxes[-1]['h'] + margin
        
        if curr_y + box[1] > vw_height:
            curr_x, curr_y = margin, margin
            page += 1
        
        boxes.append({
            'x': curr_x,
            'y': curr_y,
            'w': box[0],
            'h': box[1],
            'page': page
        })
        
        curr_x += box[0] + margin
        
    return boxes


def compute_box_sides_dims(box_dims_cm):
    sides = [box_dims_cm[key]*DPI/2.54 for key in box_dims_cm]
    sides = combinations(sides, 2)
    sides = map(lambda s: (max(s), min(s)), sides)
    return list(sides)*2

print("computing boxes positions...")
box_sides_dims = compute_box_sides_dims(box_dims_cm)
box_sides_dims.sort(key=lambda b: b[0]*b[1], reverse=True)
def filter_dims(box_sides_dims, images_paths):
    dims = []
    for path in images_paths:
        img_name = path.split('/')[-1].split('.')[0]
        order = ['top', 'bottom', 'left', 'right', 'front', 'back']
        order = {order[i]: i for i in range(len(order))}
        print(img_name, order[img_name])
        dim = box_sides_dims[order[img_name]]
        dims.append(dim)
    return dims
box_sides_dims = filter_dims(box_sides_dims, images_paths)
boxes = compute_box_positions(box_sides_dims)

print("resizing images...")
def image_box_resizing(images, boxes):
    img_box = []
    for i, img in enumerate(images):
        box = boxes[i]
        w, h = int(box['w']), int(box['h'])
        img = img.resize((w, h))
        img_box.append((img, box))
    return img_box
img_box = image_box_resizing(images, boxes)

print(len(img_box))
print("creating pages...")
pages = [Image.new('RGBA', (width, height), 'white') for _ in range(boxes[-1]['page']+1)]
def populate_pages(img_box, pages):
    for img, box in img_box:
        x, y = int(box['x']), int(box['y'])
        pages[box['page']].paste(img, box=(x, y))
    return pages
print('populating pages...')
pages = populate_pages(img_box, pages)

def draw_guides(pages, boxes):
    for box in boxes:
        page = pages[box['page']]
        draw = ImageDraw.Draw(page)
        bounds = [
            [(box['x'], box['y']), (box['x']+box['w'], box['y'])],
            [(box['x'], box['y']), (box['x'], box['y']+box['h'])],
            [(box['x'], box['y']+box['h']), (box['x']+box['w'], box['y']+box['h'])],
            [(box['x']+box['w'], box['y']), (box['x']+box['w'], box['y']+box['h'])]
        ]
        for b in bounds:
            draw.line(b, fill='black', width=3)
        
    return pages

print('saving pdf...')
pages[0].save(folder_name+'/'+OUTPUT_FILE, save_all=True, append_images=pages[1:])

print('done!')