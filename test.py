from main import main
from PIL import Image

lat = -38.203799 
lon =  -69.388419 

kmsEast = 50
kmSouth = 50

zoomLevel = 18

done = main(lat, lon, kmsEast, kmSouth, zoomLevel, "test")

if done:
    im  = Image.open("test.jpg", mode='r')
    im.show()
