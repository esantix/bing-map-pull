# Author: Santiago Echevarria (santiago93echevarria@gmail.com)
# Pull map from https://www.bing.com/maps/
# Input: initial coordinates, length (km) to East and South
# Source: https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system?redirectedfrom=MSDN

import math
from PIL import Image
import io
import asyncio
import aiohttp
import io
import time
import math

# Level depending data
# dim: Map Width and Height (pixels)	
# res: Ground Resolution (meters / pixel)	
# scale: Map Scale (at 96 dpi)  1:XX

TILEDIM = 256
DATA = {
    1:	{'dim':	512,	    'res':	78271.5170	,'scale':	 295829355.45},
    2:	{'dim':	1024,	    'res':	39135.7585	,'scale':	 147914677.73},
    3:	{'dim':	2048,	    'res':	19567.8792	,'scale':	 73957338.86},
    4:	{'dim':	4096,	    'res':	9783.9396	,'scale':	 36978669.43},
    5:	{'dim':	8192,	    'res':	4891.9698	,'scale':	 18489334.72},
    6:	{'dim':	16384,	    'res':	2445.9849	,'scale':	 9244667.36},
    7:	{'dim':	32768,	    'res':	1222.9925	,'scale':	 4622333.68},
    8:	{'dim':	65536,	    'res':	611.4962	,'scale':	 2311166.84},
    9:	{'dim':	131072,	    'res':	305.7481	,'scale':	 1155583.42},
    10:	{'dim':	262144,	    'res':	152.8741	,'scale':	 577791.71},
    11:	{'dim':	524288,	    'res':	76.4370	    ,'scale':	 288895.85},
    12:	{'dim':	1048576,	'res':	38.2185	    ,'scale':	 144447.93},
    13:	{'dim':	2097152,	'res':	19.1093	    ,'scale':	 72223.96},
    14:	{'dim':	4194304,	'res':	9.5546	    ,'scale':	 36111.98},
    15:	{'dim':	8388608,	'res':	4.7773	    ,'scale':	 18055.99},
    16:	{'dim':	16777216,	'res':	2.3887	    ,'scale':	 9028.00},
    17:	{'dim':	33554432,	'res':	1.1943	    ,'scale':	 4514.00},
    18:	{'dim':	67108864,	'res':	0.5972	    ,'scale':	 2257.00},
    19:	{'dim':	134217728,	'res':	0.2986	    ,'scale':	 1128.50},
    20:	{'dim':	268435456,	'res':	0.1493	    ,'scale':	 564.25},
    21:	{'dim':	536870912,	'res':	0.0746	    ,'scale':	 282.12},
    22:	{'dim':	1073741824,	'res':	0.0373	    ,'scale':	 141.06},
    23:	{'dim':	2147483648,	'res':	0.0187	    ,'scale':	 70.53}
    }

def clrScreen():
    print(chr(27)+'[2j')
    print('\033c')
    print('\x1bc')
    return

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
    pixelY = (0.5 - math.log(  (1+sinLatitude) / (1-sinLatitude)) / (4 * math.pi))*aux

    tileX = math.floor(pixelX)
    tileY = math.floor(pixelY)

    return tileX, tileY

def tiles2quad(tileX, tileY):

    binX = f'{tileX:b}'
    binY = f'{tileY:b}'

    num = max(len(binX),len(binY)) # Force same binary length representation (10, 100)->(010,100)
    binX = f'{tileX:0{num}b}'
    binY = f'{tileY:0{num}b}'
   
    res = "".join(i + j for i, j in zip(binY, binX)) # Interleave binary representations

    quadkey = int(res, 2) # To binary
    quadkey = num2base(quadkey, 4) # To base-4

    return quadkey

def getImgs(qList):

    def sParam(params): # Http param string
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
        params= {    
            'g':11640,
            'n':'z'
        }

        url += sParam(params)

        async with session.get(url=url) as response: # Get tile
            resp = await response.read()

            inMemory = io.BytesIO(resp)
            imCollection[q[0]] = Image.open(inMemory) # Save tile with index

            downImgs = len(imCollection) # Downloaded images
            totalImgs = len(qList) # Total images
            
            print(f"Image {downImgs}/{totalImgs} downloaded ({100*downImgs/totalImgs:.1f}%)")
            
            # if len(imCollection) % 50  == 0: 
            #     clrScreen()

    async def main(qs):
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*[get(q, session) for q in qs])

    start = time.time()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # For windows
    asyncio.run(main(qList)) # Run downloads
    end = time.time()

    print(f"\nTook {end - start:.4f} seconds to download {len(qList)} tiles.")
    print(f"{(end - start)/len(qList):.4f} seconds per tile.")

    return imCollection

def main(lat, lon, kmX, kmY, level, filename="bing_map_pull"):
    dimX = kmX*1000/DATA[level]['res']
    dimY = kmY*1000/DATA[level]['res']
    
    totPx = (dimX)*(dimY) # Total amount pixels
    
    print(f"WARNING: Image is {dimX:.0f}x{dimY:.0f} px")
    
    cTileX, cTileY = coo2tiles(lat, lon, level) # Get reference tile

    KMPERPIXEL = DATA[level]['res']/1000
    pixelsX  = kmX/KMPERPIXEL # Get total image width
    pixelsY  = kmY/KMPERPIXEL # Get total image height

    numTilesX = math.floor(pixelsX/TILEDIM) # Num of tiles to X (East)
    numTilesY = math.floor(pixelsY/TILEDIM) # Num of tiles to y (South)

    qArray=[] 
    i=0
    for ty in range(cTileY, cTileY+numTilesY):
        for tx in range(cTileX, cTileX+numTilesX):
            q = tiles2quad(tx, ty)
            qArray.append([i,q]) # Map tiles index and quadkey
            i+=1
            
    imArray = getImgs(qArray) # Get images

    newIm = Image.new('RGB', (numTilesX*TILEDIM, numTilesY*TILEDIM))
    
    yOffset = 0
    xOffset = 0
    rowIdx = 0

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

    newIm.save(filename + ".png" )
    # newIm.show()

    print(f'\nGround Resolution (m/px): {DATA[level]["res"]}')
    print(f'Map Width (px): {numTilesX*TILEDIM}')
    print(f'Map Height (px): {numTilesY*TILEDIM}')
    print(f'Map Scale (at 96 dpi):  1:{DATA[level]["scale"]}')
    print(f'Zoom level: {level}')

    print(f'\nSaving....')

    return newIm

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Bing Maps map pull')
    parser.add_argument('-e', '--east', required=True, help="Km's to East")
    parser.add_argument('-s', '--south', required=True, help="Km's to South")
    parser.add_argument('-x', '--lat', required=True, help="Initial latitude")
    parser.add_argument('-y', '--lon', required=True, help="Initial longitude")
    parser.add_argument('-l', '--level', required=False, default=19, help="Zoom level (1-19). defaults to 19")
    parser.add_argument('-f', '--filename', required=False, help="Output filename (without extension)")

    args = parser.parse_args()
    
    main(args.lat, args.lon, args.e, args.s, args.level, args.filename)
