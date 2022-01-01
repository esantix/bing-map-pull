# Author: Santiago Echevarria (santiago93echevarria@gmail.com)
# Pull map from https://www.bing.com/maps/
# Input: initial coordinates, length (km) to East and South
# Source: https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system?redirectedfrom=MSDN

from PIL import Image as pimg
import io
import asyncio
import aiohttp
import time
import math

# Level depending data
# dim: Map Width and Height (pixels)
# res: Ground Resolution (meters / pixel)
# scale: Map Scale (at 96 dpi)  1:XX

TILEDIM = 256

# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg
SUBSAMPLING = -1
QUALITY = 100

DATA = {
    1: {'dim': 512, 'res': 78271.5170, 'scale': 295829355.45},
    2: {'dim': 1024, 'res': 39135.7585, 'scale': 147914677.73},
    3: {'dim': 2048, 'res': 19567.8792, 'scale': 73957338.86},
    4: {'dim': 4096, 'res': 9783.9396, 'scale': 36978669.43},
    5: {'dim': 8192, 'res': 4891.9698, 'scale': 18489334.72},
    6: {'dim': 16384, 'res': 2445.9849, 'scale': 9244667.36},
    7: {'dim': 32768, 'res': 1222.9925, 'scale': 4622333.68},
    8: {'dim': 65536, 'res': 611.4962, 'scale': 2311166.84},
    9: {'dim': 131072, 'res': 305.7481, 'scale': 1155583.42},
    10: {'dim': 262144, 'res': 152.8741, 'scale': 577791.71},
    11: {'dim': 524288, 'res': 76.4370, 'scale': 288895.85},
    12: {'dim': 1048576, 'res': 38.2185, 'scale': 144447.93},
    13: {'dim': 2097152, 'res': 19.1093, 'scale': 72223.96},
    14: {'dim': 4194304, 'res': 9.5546, 'scale': 36111.98},
    15: {'dim': 8388608, 'res': 4.7773, 'scale': 18055.99},
    16: {'dim': 16777216, 'res': 2.3887, 'scale': 9028.00},
    17: {'dim': 33554432, 'res': 1.1943, 'scale': 4514.00},
    18: {'dim': 67108864, 'res': 0.5972, 'scale': 2257.00},
    19: {'dim': 134217728, 'res': 0.2986, 'scale': 1128.50},
    20: {'dim': 268435456, 'res': 0.1493, 'scale': 564.25},
    21: {'dim': 536870912, 'res': 0.0746, 'scale': 282.12},
    22: {'dim': 1073741824, 'res': 0.0373, 'scale': 141.06},
    23: {'dim': 2147483648, 'res': 0.0187, 'scale': 70.53}
}


def num2base(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(str(int(n % b)))
        n //= b
    return ''.join(digits[::-1])


def coo2tiles(latitude, longitude, level):

    aux = (2**level)

    sinLatitude = math.sin(latitude * math.pi/180)

    pixelX = ((longitude + 180) / 360)*aux
    pixelY = (0.5 - math.log((1+sinLatitude) /
              (1-sinLatitude)) / (4 * math.pi))*aux

    tileX = math.floor(pixelX)
    tileY = math.floor(pixelY)

    return tileX, tileY


def tiles2quad(tileX, tileY):

    binX = f'{tileX:b}'
    binY = f'{tileY:b}'

    # Force same binary length representation (10, 100)->(010,100)
    num = max(len(binX), len(binY))
    binX = f'{tileX:0{num}b}'
    binY = f'{tileY:0{num}b}'

    # Interleave binary representations
    res = "".join(i + j for i, j in zip(binY, binX))

    quadkey = int(res, 2)  # To binary
    quadkey = num2base(quadkey, 4)  # To base-4

    return quadkey


def getImgs(qList):

    if len(qList) == 0:
        tkprint("ERROR: Distances and level combination too small")
        return False

    def sParam(params):  # Http param string
        string = '?'
        for k in params.keys():
            string += f'{k}={params[k]}&'
        return string[:-1]

    imCollection = {}

    async def get(q, session):
        # url = f'https://t0.ssl.ak.dynamic.tiles.virtualearth.net/comp/ch/{q[1]}'
        # params= {
        #     'mkt': 'es-AR',
        #     'ur': 'ar',
        #     'it': 'A,G,L,LA',
        #     'shading': 't',
        #     'og': '1677',
        #     'n': 'z',
        #     'o': 'webp'
        #     }

        url = f'https://t0.ssl.ak.tiles.virtualearth.net/tiles/a{q[1]}.jpeg'
        params = {
            'g': 11640,
            'n': 'z'
        }

        url += sParam(params)

        async with session.get(url=url) as response:  # Get tile
            resp = await response.read()

            inMemory = io.BytesIO(resp)
            imCollection[q[0]] = pimg.open(inMemory)  # Save tile with index

            downImgs = len(imCollection)  # Downloaded images
            totalImgs = len(qList)  # Total images

            print(
                f"Image {downImgs}/{totalImgs} downloaded ({100*downImgs/totalImgs:.1f}%)")

    async def runn(qs):
       
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*[get(q, session) for q in qs])

    start = time.time()
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # For windows
    asyncio.run(runn(qList))  # Run downloads
    end = time.time()

    print(f"\nTook {end - start:.4f} seconds to download {len(qList)} tiles.")
    print(f"{(end - start)/len(qList):.4f} seconds per tile.")

    return imCollection



def pix2coor(pixelX, pixelY, zoomLevel):
    lon = pixelX*360/(math.pow(2,zoomLevel)) - 180; 
    lat = math.asin((math.exp((0.5 - pixelY / math.pow(2,zoomLevel)) * 4 * math.pi) - 1) / (math.exp((0.5 - pixelY / math.pow(2,zoomLevel)) * 4 * math.pi) + 1)) * 180 / math.pi 

    
    return lat, lon



def main(lat, lon, kmX, kmY, level, filename):
    dimX = kmX*1000/DATA[level]['res']
    dimY = kmY*1000/DATA[level]['res']

    totPx = (dimX)*(dimY)  # Total amount pixels
    tkprint("Downloading image...")
    tkprint(f"Image is {dimX:.0f}x{dimY:.0f} px")

    cTileX, cTileY = coo2tiles(lat, lon, level)  # Get reference tile

    KMPERPIXEL = DATA[level]['res']/1000
    pixelsX = kmX/KMPERPIXEL  # Get total image width
    pixelsY = kmY/KMPERPIXEL  # Get total image height

    numTilesX = math.floor(pixelsX/TILEDIM)  # Num of tiles to X (East)
    numTilesY = math.floor(pixelsY/TILEDIM)  # Num of tiles to y (South)

    qArray = []
    i = 0
    for ty in range(cTileY, cTileY+numTilesY):
        for tx in range(cTileX, cTileX+numTilesX):
            q = tiles2quad(tx, ty)
            qArray.append([i, q])  # Map tiles index and quadkey
            i += 1

    imArray = getImgs(qArray)  # Get images
    if imArray == False:
        return
    newIm = pimg.new('RGB', (numTilesX*TILEDIM, numTilesY*TILEDIM))

    yOffset = 0
    xOffset = 0
    rowIdx = 0

    tlCoords = pix2coor(cTileX, cTileY, level)
    brCoords = pix2coor(cTileX+numTilesX, cTileY+numTilesY, level)
    trCoords = pix2coor(cTileX+numTilesX, cTileY, level)
    blCoords = pix2coor(cTileX, cTileY+numTilesY, level)



    tkprint('\nTop-Left coords: ')
    tlcoor = tk.Entry()
    tlcoor.insert(END, f'{tlCoords[0]:.6f}, {tlCoords[1]:.6f}')
    tlcoor.pack()

    tkprint('Top-Right coords: ')
    tlcoor = tk.Entry()
    tlcoor.insert(END, f'{trCoords[0]:.6f}, {trCoords[1]:.6f}')
    tlcoor.pack()

    tkprint('Bottom-Right coords: ')
    tlcoor = tk.Entry()
    tlcoor.insert(END, f'{brCoords[0]:.6f}, {brCoords[1]:.6f}')
    tlcoor.pack()

    tkprint('Bottom-Left coords: ')
    tlcoor = tk.Entry()
    tlcoor.insert(END, f'{blCoords[0]:.6f}, {blCoords[1]:.6f}')
    tlcoor.pack()
   
    

    # Compile image
    for i in range(len(imArray)):
        im = imArray[i]
        if rowIdx >= numTilesX:
            rowIdx = 0
            yOffset += im.size[1]
            xOffset = 0

        newIm.paste(im, (xOffset, yOffset))
        rowIdx += 1
        xOffset += im.size[0]

    newIm.save(filename, format='JPEG',
               subsampling=SUBSAMPLING, quality=QUALITY)
    # newIm.show()

    tkprint(f'\nGround Resolution (m/px): {DATA[level]["res"]}')
    tkprint(f'Map Width (px): {numTilesX*TILEDIM}')
    tkprint(f'Map Height (px): {numTilesY*TILEDIM}')
    tkprint(f'Map Scale (at 96 dpi):  1:{DATA[level]["scale"]}')
    tkprint(f'Zoom level: {level}')

    tkprint(f'\nSaving....')

    return newIm


import tkinter as tk
from tkinter.ttk import *
import time
from tkinter import filedialog
from tkinter import *

window = tk.Tk()
window.geometry("400x650")
window.title('Bing Maps pull')

corLab = tk.Label(text="Coordinates ( xx,xxx, yy,yyy)")
corEntry = tk.Entry()
corEntry.insert(END, "-38,919336, -68,147202")
corLab.pack()
corEntry.pack()

kmE = tk.Label(text="Km to East")
kmEentry = tk.Entry()
kmEentry.insert(END, "1")
kmE.pack()
kmEentry.pack()

kmS = tk.Label(text="Km to South")
kmSentry = tk.Entry()
kmSentry.insert(END, "1")
kmS.pack()
kmSentry.pack()

levelLab = tk.Label(text="Level (1-19)")
levelEntry = tk.Entry()
levelEntry.insert(END, "19")
levelLab.pack()
levelEntry.pack()

from tkinter import filedialog
def tkprint(string):
    if True:
        aaa = tk.Label(text=string, justify=LEFT).pack(fill='both')
    print(string)
    return

def run():
    tkprint("Running...")
    level = int(levelEntry.get())
    cor = corEntry.get().split(" ")




    def browsefunc():
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".jpeg", initialfile ="Imagen")
        print(filename.name)
        return filename.name



    path = browsefunc()
    
    
    
    
    
    
    
    
    kmX = float(kmEentry.get().replace(",", "."))
    kmY = float(kmSentry.get().replace(",", "."))

    lat = float(cor[0].replace(",", ".")[:-1])
    lon = float(cor[1].replace(",", "."))

    main(lat, lon, kmX, kmY, level, filename=path)
    
    
    import os
    # window.destroy()
    def openImage():
        os.startfile(path, 'open')
        return
    button2 = tk.Button(window, padx=20,

                    pady=8,
                    text="Open image",
                    fg="green",
                    command=openImage)
    button2.pack()

    return

button = tk.Button(window, padx=20,

                    pady=8,
                    text="RUN",
                    fg="blue",
                    command=run)
button.pack()

window.mainloop()
