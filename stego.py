import os
import time

import numpy as np
import cv2

import getpass
import pyperclip

class Stego:
    def __init__(self):
        self.directory = os.path.dirname(os.path.abspath(__file__))
        self.fileTypes = ('.jpg', '.jpeg', '.png') #Maybe add more later - needs error checking

    #==================================================================

    #Very basic menu in order to loop use choice
    #Improvements:
    #   Add more options
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
            print()
            
            #Prevent typecasting errors
            try:
                inp = int(inp)
            except:
                inp = 0

            #Redirect the user to different modules
            if inp == 1:
                self.retrievePass()
            elif inp == 2:
                self.getFileAndPass()

            #Can add option to update or delete passwords

            elif inp == 9:
                exit()

    #==================================================================

    #Retrieves the password associated with a specific file
    #Improvements:
    #   Vectorise 1 calculation
    def retrievePass(self):
        d = self.directory+"\\Images\\"#Escape the backslashes
        images = [f for f in os.listdir(d) if f.lower().endswith(self.fileTypes)]
        
        if len(images) < 1:
            print("No files found! Press Enter to Return to Menu")
            a = input()
            return

        #Print file options
        ans = -1
        f = None
        while not f:
            for i in range(len(images)):
                print("("+str(i+1)+") "+images[i])
            print("(x) Cancel")
            ans = input()
            print()

            if ans == "x":
                return
            else:
                try:
                    ans = int(ans)
                except:
                    ans = 0
            f = images[ans-1]

        #Read in image and convert
        im = cv2.imread(d+f)
        flatIm = im.flatten()
        
        #Retrieve Password length
        pLen = ""
        for i in range(32):#Again, can replace this with a vector calculation
            pLen += str(flatIm[i] & 1)
        
        #print(pLen)
        #print(int(pLen, 2))

        #Retrieve the actual password
        binPass = [int(x) for x in flatIm[32:32+int(pLen, 2)]]
        plainPass = ""
        for val in binPass:
            plainPass += str(val & 1)

        #Convert String into bytes, then ints
        passBytes = [plainPass[i:i+8] for i in range(0, len(plainPass), 8)]
        passInts = [int(b, 2) for b in passBytes]

        #Decode back into ascii
        recovered = bytes(passInts).decode('utf-8')
        #print(recovered)

        #Add to clipboard so as not to display on screen
        pyperclip.copy(recovered)

        print("Password is now on clipboard! Press Enter to Return to Menu.")

        a = input()

    #==================================================================

    #Get the user's input for a password
    #Improvements:
    #   Decouple from embed, so data is returned to menu, then embed is called
    #   Add menu for user to choose image
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
        images = [f for f in os.listdir(self.directory) if f.lower().endswith(self.fileTypes)]
        
        #Check number of images found
        if len(images) < 1:
            print("No Image found")
        else:
            #Just open the first
            im = cv2.imread(images[0])
            
            #Redirect to actually embed the password
            self.embed(plainPass, im, images[0])

    #Perform the embedding
    #Improvements:
    #   Vectorise 1 calculation
    def embed(self, pas, im, imName):
        #Convert into binary, and left pad with 0s.
        binString = list(map(lambda x: f"{x:08b}", bytearray(pas, 'utf-8')))
        numBits = sum(len(x) for x in binString)

        #print("Contents of binString:", binString)
        
        #Create binary representation of data count, add it to data
        dataCount = f"{numBits:032b}"
        fullBits = [int(x) for x in dataCount + "".join(binString)]

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

        #print(flatIm[0:len(fullBits)])
        newIm = flatIm.reshape(shape)
        
        #Save image into image folder
        ext = "."+imName.split(".")[1]
        name = input("Please Enter A File Name (No Extension)")
        cv2.imwrite("Images\\"+name+ext, newIm)

        print("Image Saved! Press Enter to Return To Menu")
        a = input()

    #==================================================================

def __main__():
    s = Stego()
    s.menuLoop()

if __name__ == "__main__":
    __main__()