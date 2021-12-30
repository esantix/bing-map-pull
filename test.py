from main import main
from PIL import Image

lat = -37.203799 
lon =  -69.388419 

kmsEast = 10
kmSouth = 10

zoomLevel = 19

done = main(lat, lon, kmsEast, kmSouth, zoomLevel, "test")

