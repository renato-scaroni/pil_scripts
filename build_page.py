from PIL import Image
from PIL.Image import open as i_open
from PIL import ImageDraw

DPI = 300 # dots per inch
PAGE_WIDTH = 11.7 # inches, A4 paper
PAGE_HEIGHT = 8.27 # inches, A4 paper
MARGIN = .125 # 1/8 inch margin, same as the bleeding area for each card
OUTPUT_FILE = 'proxies.pdf'

# TODO: read input from file
input_string = """
2 x Snowbourn Scout.jpg
1 x Gleowine.jpg
2 x Steward of Gondor.jpg
1 x Celebrian_s Stone.jpg
1 x Unexpected Courage.jpg
2 x Sneak Attack.jpg
2 x A Test of Will.jpg
"""

# compute width and height in pixels
width, height = int(PAGE_HEIGHT * DPI), int(PAGE_WIDTH * DPI) 
# compute margin in pixels
margin = MARGIN * DPI 

print("loading images...")
# input line format: <number of copies> x <filename>
input_parse = map(lambda i: i.split(' x '), input_string.split('\n'))
input_parse = filter(lambda i: len(i) == 2, input_parse)
images = [int(i[0]) * [i_open(f'player_cards/{i[1]}')] for i in input_parse]
flatten_list = lambda l: [item for sublist in l for item in sublist]
images = flatten_list(images)

print("resizing images...")
#resize images to be 2.5 x 3.5 inches
images = [i.resize((int(2.625*DPI), int(3.625*DPI))) for i in images]

print("adjusting image colors...")
factor = 1.15
for img in images:
    d = img.getdata()
    
    new_image = []
    for item in d:
        item = list(map(lambda i: int(i*factor), item))
        new_image.append(tuple(item+[255]))
    
    img.putdata(new_image)

 
def compute_boxes_positions(r, c, margin=margin, width=width, height=height):
    vw_width, vw_height = width - 2*margin, height - 2*margin
    get_x = lambda i: int(margin+vw_width/c*(i%c))
    get_y = lambda i: int(margin+vw_height/r*(i//c))
    boxes = map(lambda i: (get_x(i), get_y(i)), range(r*c))
    return list(boxes)

print("computing boxes positions...")
boxes = compute_boxes_positions(3, 3)
print("creating pages...")
pages = [Image.new('RGBA', (width, height), 'white') for _ in range(len(images)//9+1)]

#recursively paste images into pages
def populate_pages(images, boxes, pages, img_idx=0):
    if img_idx >= len(images):
        return pages
    page_idx = img_idx//9
    pages[page_idx].paste(images[img_idx], box=boxes[img_idx%9])
    return populate_pages(images, boxes, pages, img_idx+1)

print('populating pages...')
pages = populate_pages(images, boxes, pages)

def draw_guides(page, margin, width=width, height=height):
    draw = ImageDraw.Draw(page)
    card_height = 3.5*DPI
    card_width = 2.5*DPI
    for i in range(0, 9, 3):
        box = boxes[i]
        draw.line([(0, box[1]+margin), (width, box[1]+margin)], fill='black', width=3)
        draw.line([(0, box[1]+margin+card_height), (width, box[1]+margin+card_height)], fill='black', width=3)
    for box in boxes[:3]:
        draw.line([(box[0]+margin, 0), (box[0]+margin, height)], fill='black', width=3)
        draw.line([(box[0]+margin+card_width, 0), (box[0]+margin+card_width, height)], fill='black', width=3)
    
    return page

print('drawing cut guides...')
pages = list(map(lambda p: draw_guides(p, margin/2), pages))

print('saving pdf...')
pages[0].save(OUTPUT_FILE, save_all=True, append_images=pages[1:])

print('done!')