# Author: Santiago Echevarria (santiago93echevarria@gmail.com)
# Pull map from https://www.bing.com/maps/
# Input: initial coordinates, length (km) to East and South
# Source: https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system?redirectedfrom=MSDN


import math


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


def pix2coor(pixelX, pixelY, zoomLevel):
    lon = pixelX*360/(math.pow(2, zoomLevel)) - 180
    lat = math.asin((math.exp((0.5 - pixelY / math.pow(2, zoomLevel)) * 4 * math.pi) - 1) /
                    (math.exp((0.5 - pixelY / math.pow(2, zoomLevel)) * 4 * math.pi) + 1)) * 180 / math.pi

    return lat, lon