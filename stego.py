import cv2
import numpy as np
import os

class Stego:
    def __init__(self):
        #Setup Here
        a = 1

    #Very basic menu in order to loop use choice
    def menuLoop(self):
        inp = 0

        while inp != 9:
            #Clear the terminal for better readability
            if os.name == 'nt':
                os.system('cls')

            print("(1) Retrieve a Password")
            print("(2) Embed a Password")
            print("(9) Exit")
            inp = input()
            
            #Prevent typecasting errors
            try:
                inp = int(inp)
            except:
                inp = 0

            #Redirect the user to different modules
            if inp == 1:
                print("Recall password")
            elif inp == 2:
                print("Add password")
            elif inp == 9:
                exit()

def __main__():
    s = Stego()
    s.menuLoop()

if __name__ == "__main__":
    __main__()