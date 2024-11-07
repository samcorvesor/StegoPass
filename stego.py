import os
import time

import numpy as np
import cv2

import getpass

class Stego:
    def __init__(self):
        self.directory = os.path.dirname(os.path.abspath(__file__))

    #==================================================================

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
                self.getFileAndPass()
            elif inp == 9:
                exit()

    #==================================================================

    def retrievePass(self):
        print()

    #==================================================================

    #Combine a user's password and a given image
    def getFileAndPass(self):
        #Use getpass to take the user's password without it being output to the screen
        plainPass, pass2 = 0, 1
        while plainPass != pass2:
            plainPass = getpass.getpass("Enter your password")
            pass2 = getpass.getpass("Please confirm your password")
            print()
            if plainPass != pass2:
                print("Please try again, passwords did not match.")
                print()

        #CHOICE: Do I want the user to prompt for an image, or use an image in the directory by assumption?
        #For now just take image from directory
        fileTypes = ('.jpg', '.jpeg', '.png') #Maybe add more later - needs error checking
        images = [f for f in os.listdir(self.directory) if f.lower().endswith(fileTypes)]
        

        #Check number of images found
        if len(images) < 1:
            print("No Image found")
        else:
            #Just open the first
            im = cv2.imread(images[0])
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            
            #Redirect to actually embed the password
            self.embed(plainPass, im, images[0])

    #Perform the embedding
    def embed(self, pas, im, imName):
        #Convert into binary, and left pad with 0s.
        binString = list(map(lambda x: f"{x:08b}", bytearray(pas, 'utf-8')))
        numBits = sum(len(x) for x in binString)

        #print("Contents of binString:", binString)
        
        #Create binary representation of data count, add it to data
        dataCount = f"{numBits:032b}"
        fullBits = [int(x) for x in dataCount + "".join(binString)]

        #Convert to numpy array
        arr = np.array(fullBits)

        #Flatten image data, and convert into binary strings
        shape = im.shape
        flatIm = im.flatten()

        #print(fullBits)
        #print(flatIm[0:len(fullBits)])

        #Embed
        #   Can replace vector function?
        #   Loops password so not a large issue
        for i in range(len(fullBits)):
            flatIm[i] = (flatIm[i] & 0xFE) | fullBits[i]

        newIm = flatIm.reshape(shape)

        #Save image into image folder
        newIm = cv2.cvtColor(newIm, cv2.COLOR_RGB2BGR)
        cv2.imwrite("Images/"+imName, newIm)

        #keep this for after
        #test = bytes(int(b, 2) for b in binString).decode('utf-8')

        print("Image Saved! Press Enter to Return To Menu")
        a = input()

    #==================================================================

def __main__():
    s = Stego()
    s.menuLoop()

if __name__ == "__main__":
    __main__()