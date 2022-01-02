from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
import tkinter as tk
import os

from main import main


def run():
    print("Running...")
    level = int(levelEntry.get())

    if level >= 19:
        level = 19
    if level <=0:
        level = 1

    kmX = float(kmEentry.get().replace(",", "."))
    kmY = float(kmSentry.get().replace(",", "."))

    lat = float(latEntry.get().replace(",", "."))
    lon = float(lonEntry.get().replace(",", "."))

    path = filedialog.asksaveasfile(
        mode='w', defaultextension=".tiff", initialfile="Imagen").name

    newIm, tlCoords, trCoords, blCoords, brCoords = main(lat, lon, kmX, kmY, level, filename=path)


    print('\nTop-Left coords: ')
    tlcoor = tk.Entry()
    tlcoor.insert(END, f'{tlCoords[0]:.6f}, {tlCoords[1]:.6f}')
    tlcoor.grid(row=18, column=0)

    print('Top-Right coords: ')
    tlcoor = tk.Entry()
    tlcoor.insert(END, f'{trCoords[0]:.6f}, {trCoords[1]:.6f}')
    tlcoor.grid(row=18, column=1)

    print('Bottom-Right coords: ')
    tlcoor = tk.Entry()
    tlcoor.insert(END, f'{brCoords[0]:.6f}, {brCoords[1]:.6f}')
    tlcoor.grid(row=19, column=1)

    print('Bottom-Left coords: ')
    tlcoor = tk.Entry()
    tlcoor.insert(END, f'{blCoords[0]:.6f}, {blCoords[1]:.6f}')
    tlcoor.grid(row=19, column=0)
 
    # window.destroy()
        
    def openImage():
            os.startfile(path, 'open')
            return
        
    button2 = tk.Button(window, padx=20,
                        pady=8,
                        text="Open image",
                        bg='blue', fg='white',
                        command=openImage)
    button2.grid(row=21, column=0, pady=20)

    return

window = tk.Tk()
window.geometry("600x450")
window.title('Bing Maps pull')

window.grid_columnconfigure((0,1), weight=1)

Title = tk.Label(text=" ")
Title.grid(row=1, column=0)


latLab = tk.Label(text="Lattitude WGS84")
latLab.grid(row=2, column=0)
latEntry = tk.Entry()
latEntry.insert(END, "-38,919336")
latEntry.grid(row=2, column=1)

lonLab = tk.Label(text="Longitude WGS84")
lonLab.grid(row=3, column=0)
lonEntry = tk.Entry()
lonEntry.insert(END, "-68,147202")
lonEntry.grid(row=3, column=1)

kmE = tk.Label(text="Kms to East")
kmEentry = tk.Entry()
kmEentry.insert(END, "1")
kmE.grid(row=4, column=0)
kmEentry.grid(row=4, column=1)

kmS = tk.Label(text="Kms to South")
kmSentry = tk.Entry()
kmSentry.insert(END, "1")
kmS.grid(row=5, column=0)
kmSentry.grid(row=5, column=1)

levelLab = tk.Label(text="Level (1-19)")
levelEntry = tk.Entry()
levelEntry.insert(END, "19")
levelLab.grid(row=6, column=0)
levelEntry.grid(row=6, column=1)

button = tk.Button(window, padx=20,
                   pady=8,
                   text="RUN",
                   bg='blue', fg='white',
                   command=run)
button.grid(row=10, column=0, pady=30)

window.mainloop()

