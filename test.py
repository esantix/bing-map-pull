from main import main
from PIL import Image

lat = -37.203799 
lon =  -69.388419 

kmsEast = 5
kmSouth = 5

zoomLevel = 18

done = main(lat, lon, kmsEast, kmSouth, zoomLevel, "test")

