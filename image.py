from PIL import Image
from resizeimage import resizeimage

def preprocessingImage(filepath: str, width=500, height=281, colors=16):
    '''
        reduce colors and resolution from image
        @param filepath string
        @returns a object PIL.Image
    '''
    colors = int(colors)
    width = int(width)
    height = int(height)
    file = open(filepath, 'rb')
    image = Image.open(file)
    width = min(width, image.width)
    height = min(height, image.height)
    frmt = image.format
    #resize
    image = resizeimage.resize_cover(image, [width, height]) 
    #change color
    image = image.convert('P', palette=Image.ADAPTIVE, colors=colors).convert('RGB')
    image.format = frmt
    return image

def getPixelByColors(img: Image):
    '''
    create groups pixel coordinates by equal colors
    @param img PIL.Image
    @returns a dict with image colors tuple as the keys
    '''
    
    pixelbycolors = {}
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            c = img.getpixel((x,y))
            if not c in pixelbycolors:
                pixelbycolors[c] = []
            pixelbycolors[c].append((x,y))
    return pixelbycolors

