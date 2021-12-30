from main import main
from PIL import Image

lat = -38.203799 
lon =  -69.388419 

kmsEast = 1000 
kmSouth = 1000

zoomLevel = 5

main(lat, lon, kmsEast, kmSouth, zoomLevel, "test")

im  = Image.open("test.jpg", mode='r')
im.show()
