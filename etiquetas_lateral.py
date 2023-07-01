from PIL import Image
from PIL.Image import open as i_open
from PIL import ImageDraw
import argparse

# parse inputs
parser = argparse.ArgumentParser(description='Create a pdf with the given images')
parser.add_argument('file_names',
                    nargs=1,
                    type=str,
                    help='file_names of the image to be printed')

parser.add_argument('img_dims',
                    nargs=2,
                    type=float,
                    help='image dimensions')

parser.add_argument('-r',
                    '--rotate',
                    type=float,
                    help='rotate image by the given angle in degrees')                 

file_names = parser.parse_args().file_names
img_dims = parser.parse_args().img_dims
rotate = parser.parse_args().rotate

print(len(file_names), len(img_dims)/2)

if len(file_names) != len(img_dims)/2:
    raise Exception('The number of file names must be the same as the number of image dimensions')

def cm_to_inches(cm):
    return cm/2.54

img_dims = list(map(cm_to_inches, img_dims))

DPI = 300 # dots per inch
PAGE_WIDTH = 11.7 # inches, A4 paper
PAGE_HEIGHT = 8.27 # inches, A4 paper
MARGIN = .125 # 1/8 inch margin, same as the bleeding area for each card
OUTPUT_FILE = 'etiqueta.pdf'

# compute width and height in pixels
width, height = int(PAGE_HEIGHT * DPI), int(PAGE_WIDTH * DPI)
# compute margin in pixels
margin = MARGIN * DPI

print(file_names)

print("loading images...")
images = [i_open(f) for f in file_names]

print(images)

print("resizing images...")
flatten = lambda l: [item for sublist in l for item in sublist]
if rotate:
    images = list(map(lambda i: i.rotate(rotate, expand=True), images))
def resize_image(args):
    img, (width, height) = args
    return img.resize((int(width*DPI), int(height*DPI)))
def reshape_list(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]
img_dims = reshape_list(img_dims, 2)
images = list(map(resize_image, zip(images, img_dims)))

# print("adjusting image colors...")
# factor = 1.15
# for img in images:
#     d = img.getdata()

#     new_image = []
#     for item in d:
#         item = list(map(lambda i: int(i*factor), item))
#         new_image.append(tuple(item+[255]))

#     img.putdata(new_image)


def compute_boxes_positions(r, c, margin=margin, width=width, height=height):
    vw_width, vw_height = width - 2*margin, height - 2*margin
    get_x = lambda i: int(margin+vw_width/c*(i%c))
    get_y = lambda i: int(margin+vw_height/r*(i//c))
    boxes = map(lambda i: (get_x(i), get_y(i)), range(r*c))
    return list(boxes)

# print("computing boxes positions...")
# boxes = compute_boxes_positions(3, 3)
print("creating pages...")
page = Image.new('RGBA', (width, height), 'white')
# pages = [Image.new('RGBA', (width, height), 'white') for _ in range(len(images)//9+1)]

box = (int(1), 1)

page.paste(images[0], box=box)

# #recursively paste images into pages
# def populate_pages(images, boxes, pages, img_idx=0):
#     if img_idx >= len(images):
#         return pages
#     page_idx = img_idx//9
#     pages[page_idx].paste(images[img_idx], box=boxes[img_idx%9])
#     return populate_pages(images, boxes, pages, img_idx+1)

# print('populating pages...')
# pages = populate_pages(images, boxes, pages)

# def draw_guides(page, margin, width=width, height=height):
#     draw = ImageDraw.Draw(page)
#     card_height = 3.5*DPI
#     card_width = 2.5*DPI
#     for i in range(0, 9, 3):
#         box = boxes[i]
#         draw.line([(0, box[1]+margin), (width, box[1]+margin)], fill='black', width=3)
#         draw.line([(0, box[1]+margin+card_height), (width, box[1]+margin+card_height)], fill='black', width=3)
#     for box in boxes[:3]:
#         draw.line([(box[0]+margin, 0), (box[0]+margin, height)], fill='black', width=3)
#         draw.line([(box[0]+margin+card_width, 0), (box[0]+margin+card_width, height)], fill='black', width=3)

#     return page

# print('drawing cut guides...')
# pages = list(map(lambda p: draw_guides(p, margin/2), pages))

print('saving pdf...')
# pages[0].save(OUTPUT_FILE, save_all=True, append_images=pages[1:])
page.save(OUTPUT_FILE, save_all=True)
# print('done!')