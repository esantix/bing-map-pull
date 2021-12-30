# Author: Santiago Echevarria (santiago93echevarria@gmail.com)
# 
# Pull map from https://www.bing.com/maps/
# Input: initial coordinates, length (km) to East and South
# 
# Source: https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system?redirectedfrom=MSDN

import math
from PIL import Image
import io
import asyncio
import aiohttp
import io
import time
import math

LEVEL = 19

def num2base(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(str(int(n % b)))
        n //= b
    return ''.join(digits[::-1])

def coo2tiles(latitude, longitude):

    aux = (2**LEVEL)
    
    sinLatitude = math.sin(latitude * math.pi/180)

    pixelX = ((longitude + 180) / 360)*aux
    pixelY = (0.5 - math.log(  (1+sinLatitude) / (1-sinLatitude)) / (4 * math.pi))*aux

    tileX = math.floor(pixelX)
    tileY = math.floor(pixelY)

    return tileX, tileY

def tiles2quad(tileX, tileY):

    binX = f'{tileX:b}'
    binY = f'{tileY:b}'

    num = max(len(binX),len(binY))
    binX = f'{tileX:0{num}b}'
    binY = f'{tileY:0{num}b}'
   
    # Interleave binary representations
    res = "".join(i + j for i, j in zip(binY, binX))

    quadkey = int(res, 2)
    quadkey = num2base(quadkey, 4)

    return quadkey

def getImgs(qList):

    def sParam(params):
        string = '?'
        for p in params.keys():
            string += f'{p}={params[p]}&'
        return string[:-1]


    imList = {}

    async def get(q, session):
        url = f'https://t0.ssl.ak.dynamic.tiles.virtualearth.net/comp/ch/{q[1]}'
        params= {
            'mkt': 'es-AR',
            'ur': 'ar',
            'it': 'A,G,L,LA',
            'shading': 't',
            'og': '1677',
            'n': 'z',
            'o': 'webp'
        }
        url += sParam(params)

        async with session.get(url=url) as response:
            resp = await response.read()

            in_memory_file = io.BytesIO(resp)
            im = Image.open(in_memory_file)
            imList[q[0]] = im
            # Save with index since it's async

    async def main(qs):
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*[get(q, session) for q in qs])

    start = time.time()
    asyncio.run(main(qList))
    end = time.time()

    print("\n"*20)
    print(f"Took {end - start} seconds to pull {len(qList)} tiles.")
    return imList


def main(lat, lon, kmX, kmY, filename="bing_map_pull"):


    cTileX, cTileY = coo2tiles(lat, lon)

    kmPerPixel = 0.2986/1000
    pixelsX  = kmX/kmPerPixel
    pixelsY  = kmY/kmPerPixel

    numTilesX = math.floor(pixelsX/256)
    numTilesY = math.floor(pixelsY/256)

    qArray=[]
    i=0
    for ty in range(cTileY, cTileY+numTilesY):
        for tx in range(cTileX, cTileX+numTilesX):
            q = tiles2quad(tx, ty)
            qArray.append([i,q])
            i+=1
            
    imArray = getImgs(qArray)

    new_im = Image.new('RGB', (numTilesX*256, numTilesY*256))
    
    y_offset = 0
    x_offset = 0
    rowIdx = 0

    for i in range(len(imArray)):
        im = imArray[i]
        if rowIdx >= numTilesX:
            rowIdx = 0
            y_offset += im.size[1]
            x_offset = 0

        new_im.paste(im, (x_offset, y_offset))
        rowIdx += 1
        x_offset += im.size[0]

    new_im.save(filename + ".jpg" )
    # new_im.show()

    return 

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Bing Maps map pull')
    parser.add_argument('-e', '--east', required=True, help="Km's to East")
    parser.add_argument('-s', '--south', required=True, help="Km's to South")
    parser.add_argument('-x', '--lat', required=True, help="Initial latitude")
    parser.add_argument('-y', '--lon', required=True, help="Initial longitude")
    parser.add_argument('-f', '--filename', required=False, help="Output filename (without extension)")

    args = parser.parse_args()
    
    main(args.lat, args.lon, args.e, args.s, args.filename)

    